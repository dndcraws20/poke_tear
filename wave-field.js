// Scroll Wave Field background — vanilla port of the Originkit "Scroll Wave Field" WebGL component.
// A 3D field of glowing points rolling toward the camera as a wave; the pointer lifts the surface.
// Same hooks as CellField / FlowerExpansion: flare(a, b, ms, speedMult), setDanger(bool), pause(), resume().
(function () {
  'use strict';

  const FIELD_W = 3600, FIELD_D = 7000, CAM_Z0 = 700, FOV = 60, TAU = Math.PI * 2, MAX_COLORS = 8;
  const CAM_Y_FULL = 550, CAM_REF_AREA = 1200 * 800, CAM_SCALE_MIN = 0.5, CAM_SCALE_MAX = 2.5, CURSOR_FOLLOW = 7;
  const FLOW_PER_WAVE = 260 / 160, GLOW_PER_LIFT = 100 / 45;

  const VERT = [
    'precision highp float;',
    'attribute vec2 aGrid; attribute vec2 aSeed;',
    'uniform vec2 uRes; uniform float uFocal; uniform float uTime; uniform float uAmp; uniform float uScatter; uniform float uFreq;',
    'uniform vec2 uDir; uniform float uFlow; uniform float uDepth; uniform float uCamY; uniform float uCamZ; uniform float uPitch; uniform float uRoll;',
    'uniform float uDot; uniform float uColorCount; uniform vec2 uJit; uniform vec3 uColors[8]; uniform vec3 uCursor; uniform float uCurR; uniform float uCurS; uniform float uHover;',
    'varying vec3 vCol; varying float vA; varying float vHot;',
    'vec3 pickColor(float sel) { float idx = floor(sel * uColorCount); vec3 c = uColors[0];',
    '  for (int i = 1; i < 8; i++) { if (float(i) >= uColorCount) break; if (float(i) == idx) c = uColors[i]; } return c; }',
    'float surf(vec2 q) { return sin(q.x) * 0.55 + sin(q.x * 0.55 + q.y * 1.15) * 0.30 + sin(q.y * 0.75) * 0.22; }',
    'void main() {',
    '  vec2 w = aGrid + (aSeed - 0.5) * uJit;',
    '  w.y = uCamZ + mod(w.y - uFlow - uCamZ, uDepth);',
    '  float h3 = fract(sin(dot(aSeed, vec2(91.37, 47.13))) * 12345.678);',
    '  float h = surf(w * uFreq - uDir * uTime) * uAmp + (h3 - 0.5) * uScatter;',
    '  float cd = length(w - uCursor.xy);',
    '  float g = exp(-(cd * cd) / (uCurR * uCurR)) * uCursor.z;',
    '  h += g * uCurS;',
    '  float g2 = g * g; g2 = g2 * g2; g2 = g2 * g2;',
    '  vec3 p = vec3(w.x, h - uCamY, w.y - uCamZ);',
    '  float c = cos(uPitch); float s = sin(uPitch);',
    '  float ry = p.y * c + p.z * s; float rz = -p.y * s + p.z * c;',
    '  if (rz < 40.0) { gl_Position = vec4(2.0, 2.0, 0.0, 1.0); gl_PointSize = 0.0; vCol = uColors[0]; vA = 0.0; vHot = 0.0; return; }',
    '  float cr = cos(uRoll); float sr = sin(uRoll);',
    '  float rx = p.x * cr - ry * sr; float ryr = p.x * sr + ry * cr;',
    '  float sx = rx * uFocal / rz; float sy = ryr * uFocal / rz;',
    '  gl_Position = vec4(sx / (uRes.x * 0.5), sy / (uRes.y * 0.5), 0.0, 1.0);',
    '  float rad = max(uDot * uFocal / rz, 0.55);',
    '  gl_PointSize = clamp(rad * 2.0 * (1.0 + g2 * uHover * 0.20), 1.0, 220.0);',
    '  float bri = 0.28 + h3 * 0.72;',
    '  vec2 bq = w * vec2(0.0040, 0.0032) - uDir * uTime * 0.30;',
    '  float band = sin(bq.x) + sin(bq.y);',
    '  float sel = fract((band + 2.0) * 0.25 + (aSeed.y - 0.5) * 0.55);',
    '  vCol = pickColor(sel);',
    '  float lum = dot(vCol, vec3(0.299, 0.587, 0.114));',
    '  vHot = (0.25 + 0.75 * lum) * bri * bri * 0.7 + g2 * uHover * 0.55;',
    '  float fog = (1.0 - smoothstep(2800.0, 6400.0, rz)) * smoothstep(70.0, 240.0, rz);',
    '  vA = bri * fog * (1.0 + g2 * uHover * 0.55);',
    '}',
  ].join('\n');
  const FRAG = [
    'precision highp float;',
    'varying vec3 vCol; varying float vA; varying float vHot;',
    'void main() {',
    '  float d = length(gl_PointCoord - 0.5) * 2.0; if (d > 1.0) discard;',
    '  float a = (1.0 - smoothstep(0.90, 1.0, d)) * vA;',
    '  vec3 col = vCol + vec3(1.0) * pow(1.0 - d, 10.0) * vHot * 0.9;',
    '  gl_FragColor = vec4(col * a, a); }',
  ].join('\n');

  // Originkit preset values
  const DEFAULTS = {
    colors: ['#5A4AE0', '#F2D98A'], density: 145, dotSize: 2, scatter: 108, cameraHeight: 50,
    waveSpeed: 250, waveHeight: 200, waveLength: 2070, tiltStart: 12, rollStart: 0,
    cursorRadius: 25, cursorLift: 45, fps: 30, maxDpr: 1.25,
  };

  function parseColor(input) {
    let h = String(input || '').replace('#', '').trim();
    if (h.length === 3 || h.length === 4) h = h.split('').map(c => c + c).join('');
    h = h.padEnd(6, '0');
    return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
  }
  function mulberry32(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function compile(gl, type, src) {
    const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) { console.warn('WaveField shader:', gl.getShaderInfoLog(sh)); gl.deleteShader(sh); return null; }
    return sh;
  }
  const lerp = (a, b, t) => a + (b - a) * t;

  class WaveField {
    constructor(canvas, cfg) {
      this.canvas = canvas;
      this.cfg = Object.assign({}, DEFAULTS, cfg || {});
      this.ok = false; this.running = false; this.disposed = false; this.frameId = 0; this.last = 0; this.acc = 0;
      this.phase = 0; this.flow = 0; this.count = 0; this.spacingX = 1; this.spacingZ = 1; this.builtDensity = -1;
      this.dpr = 1; this.cssW = 0; this.cssH = 0; this.areaScale = 1;
      this.p = { x: 0, y: 0, sx: 0, sy: 0, active: 0, target: 0, press: 0, pressTarget: 0 };
      this.hitX = 0; this.hitZ = -1e6;
      this.basePal = this.cfg.colors.map(parseColor); this.curPal = this.basePal.map(c => c.slice());
      this.flareUntil = 0; this.flarePal = null; this.flareSpeed = 1; this.danger = false; this.speedMult = 1;
      this.palBuf = new Float32Array(MAX_COLORS * 3);
      this.reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
      this.onMove = e => { this.p.x = e.clientX; this.p.y = e.clientY; this.p.target = 1; };
      this.onLeave = () => { this.p.target = 0; this.p.pressTarget = 0; };
      this.onDown = e => { this.onMove(e); this.p.pressTarget = 1; };
      this.onUp = () => { this.p.pressTarget = 0; };
      this.onVisibility = () => { this.last = performance.now(); };
      window.addEventListener('pointermove', this.onMove, { passive: true });
      window.addEventListener('pointerdown', this.onDown, { passive: true });
      window.addEventListener('pointerup', this.onUp); window.addEventListener('pointercancel', this.onUp);
      window.addEventListener('pointerleave', this.onLeave); window.addEventListener('blur', this.onLeave);
      document.addEventListener('visibilitychange', this.onVisibility);
      this.init();
    }

    init() {
      const gl = this.canvas.getContext('webgl', { alpha: true, antialias: false, premultipliedAlpha: true, depth: false, powerPreference: 'low-power' });
      if (!gl) return;
      const vs = compile(gl, gl.VERTEX_SHADER, VERT), fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
      if (!vs || !fs) return;
      const prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { console.warn('WaveField link:', gl.getProgramInfoLog(prog)); return; }
      gl.useProgram(prog);
      this.aGrid = gl.getAttribLocation(prog, 'aGrid'); this.aSeed = gl.getAttribLocation(prog, 'aSeed');
      const U = n => gl.getUniformLocation(prog, n);
      this.u = { res: U('uRes'), focal: U('uFocal'), time: U('uTime'), amp: U('uAmp'), scatter: U('uScatter'), freq: U('uFreq'), dir: U('uDir'), flow: U('uFlow'), depth: U('uDepth'), camY: U('uCamY'), camZ: U('uCamZ'), pitch: U('uPitch'), roll: U('uRoll'), dot: U('uDot'), colorCount: U('uColorCount'), jit: U('uJit'), colors: U('uColors[0]'), cursor: U('uCursor'), curR: U('uCurR'), curS: U('uCurS'), hover: U('uHover') };
      this.gridBuf = gl.createBuffer(); this.seedBuf = gl.createBuffer();
      gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
      this.gl = gl; this.ok = true;
    }

    buildGrid(d) {
      const gl = this.gl, cols = Math.max(8, Math.round(d)), rows = Math.max(8, Math.round(d * 2));
      this.count = cols * rows; this.spacingX = FIELD_W / (cols - 1); this.spacingZ = FIELD_D / (rows - 1);
      const grid = new Float32Array(this.count * 2), seed = new Float32Array(this.count * 2), rnd = mulberry32(0x5eed);
      let i = 0;
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) { grid[i * 2] = -FIELD_W / 2 + (c + 0.5) * this.spacingX; grid[i * 2 + 1] = r * this.spacingZ; seed[i * 2] = rnd(); seed[i * 2 + 1] = rnd(); i++; }
      gl.bindBuffer(gl.ARRAY_BUFFER, this.gridBuf); gl.bufferData(gl.ARRAY_BUFFER, grid, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.seedBuf); gl.bufferData(gl.ARRAY_BUFFER, seed, gl.STATIC_DRAW);
      this.builtDensity = d;
    }

    resize() {
      const canvas = this.canvas, gl = this.gl;
      this.dpr = Math.min(window.devicePixelRatio || 1, this.cfg.maxDpr);
      this.cssW = canvas.clientWidth || window.innerWidth; this.cssH = canvas.clientHeight || window.innerHeight;
      this.areaScale = this.cssW > 0 && this.cssH > 0 ? Math.min(CAM_SCALE_MAX, Math.max(CAM_SCALE_MIN, Math.sqrt((this.cssW * this.cssH) / CAM_REF_AREA))) : 1;
      const w = Math.max(1, Math.round(this.cssW * this.dpr)), h = Math.max(1, Math.round(this.cssH * this.dpr));
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      gl.viewport(0, 0, w, h);
    }

    // Shared hooks -----------------------------------------------------------
    flare(a, b, ms, speedMult) { this.flarePal = [parseColor(a), parseColor(b)]; this.flareUntil = performance.now() + (ms || 3000); this.flareSpeed = speedMult || 2.5; if (this.reduced) this.drawFrame(0); }
    setDanger(on) { this.danger = !!on; if (this.reduced) this.drawFrame(0); }
    setPalette(colors) { this.basePal = colors.map(parseColor); }
    start() { this.resume(); return this; }
    resume() {
      if (!this.ok || this.disposed || this.running) return;
      this.running = true; this.last = performance.now(); this.acc = 0;
      if (this.reduced) { this.drawFrame(0); this.running = false; return; }
      const loop = () => { if (!this.running) return; this.frameId = requestAnimationFrame(loop); this.tick(); };
      loop();
    }
    pause() { this.running = false; cancelAnimationFrame(this.frameId); }

    tick() {
      if (document.hidden) return;
      const now = performance.now(); this.acc += now - this.last; this.last = now;
      if (this.acc < 1000 / this.cfg.fps) return;
      const dt = Math.min(0.1, this.acc / 1000); this.acc = 0;
      this.drawFrame(dt);
    }

    groundHit(mx, my, wDev, hDev, focal, pitch, roll, camY, camZ) {
      const px = mx * this.dpr - wDev / 2, py = -(my * this.dpr - hDev / 2);
      const cr = Math.cos(roll), sr = Math.sin(roll);
      const sx = px * cr + py * sr, sy = -px * sr + py * cr;
      const dx = sx / focal, dy = sy / focal, c = Math.cos(pitch), s = Math.sin(pitch);
      const wy = dy * c - s, wz = dy * s + c;
      if (wy > -1e-4) return null;
      const t = -camY / wy;
      return { x: dx * t, z: camZ + wz * t };
    }

    drawFrame(dt) {
      const gl = this.gl, L = this.cfg, u = this.u, p = this.p;
      if (!gl) return;
      this.resize();
      if (this.cssW <= 0 || this.cssH <= 0) return;
      if (L.density !== this.builtDensity) this.buildGrid(L.density);
      if (!this.count) return;

      // hover / press easing (replaces the motion library)
      const ke = 1 - Math.exp(-dt * 6);
      p.active = lerp(p.active, p.target, ke); p.press = lerp(p.press, p.pressTarget, ke);
      const now = performance.now();
      const flaring = this.flarePal && now < this.flareUntil;
      const tPal = flaring ? this.flarePal : this.danger ? [[1, 0.18, 0.18], [1, 0.6, 0]] : this.basePal;
      const tSpeed = flaring ? this.flareSpeed : this.danger ? 1.8 : 1;
      const kp = 1 - Math.exp(-dt * 3);
      this.speedMult = lerp(this.speedMult, tSpeed, kp);
      if (this.curPal.length !== tPal.length) this.curPal = tPal.map(c => c.slice());
      this.curPal = this.curPal.map((c, i) => [lerp(c[0], tPal[i][0], kp), lerp(c[1], tPal[i][1], kp), lerp(c[2], tPal[i][2], kp)]);
      const speedMul = (1 + p.press) * this.speedMult;

      if (p.active < 0.002) { p.sx = p.x; p.sy = p.y; } else { const k = 1 - Math.exp(-dt * CURSOR_FOLLOW); p.sx += (p.x - p.sx) * k; p.sy += (p.y - p.sy) * k; }
      this.phase += dt * (L.waveSpeed / 100) * speedMul;
      this.flow = (this.flow + dt * (L.waveSpeed * FLOW_PER_WAVE) * speedMul) % FIELD_D;

      const pitch = (L.tiltStart * Math.PI) / 180, roll = (-L.rollStart * Math.PI) / 180;
      const camY = (Math.min(100, Math.max(0, L.cameraHeight)) / 100) * CAM_Y_FULL * this.areaScale, camZ = CAM_Z0;
      const wDev = this.canvas.width, hDev = this.canvas.height;
      const focal = hDev / (2 * Math.tan(((FOV / 2) * Math.PI) / 180));
      if (p.active <= 0.001) { this.hitX = 0; this.hitZ = -1e6; }
      else { const hit = this.groundHit(p.sx, p.sy, wDev, hDev, focal, pitch, roll, camY, camZ); if (hit) { this.hitX = hit.x; this.hitZ = hit.z; } else if (this.hitZ === -1e6) { this.hitX = 0; this.hitZ = FIELD_D; } }

      const pal = this.curPal.slice(0, MAX_COLORS);
      for (let i = 0; i < pal.length; i++) { this.palBuf[i * 3] = pal[i][0]; this.palBuf[i * 3 + 1] = pal[i][1]; this.palBuf[i * 3 + 2] = pal[i][2]; }
      const hoverGlow = Math.min(400, Math.abs(L.cursorLift) * GLOW_PER_LIFT);

      gl.uniform2f(u.res, wDev, hDev); gl.uniform1f(u.focal, focal); gl.uniform1f(u.time, this.phase);
      gl.uniform1f(u.amp, L.waveHeight); gl.uniform1f(u.scatter, L.scatter); gl.uniform1f(u.freq, TAU / Math.max(50, L.waveLength));
      gl.uniform2f(u.dir, 0, -1); gl.uniform1f(u.flow, this.flow); gl.uniform1f(u.depth, FIELD_D);
      gl.uniform1f(u.camY, camY); gl.uniform1f(u.camZ, camZ); gl.uniform1f(u.pitch, pitch); gl.uniform1f(u.roll, roll);
      gl.uniform1f(u.dot, L.dotSize); gl.uniform1f(u.colorCount, pal.length);
      gl.uniform2f(u.jit, this.spacingX * 0.25, this.spacingZ * 0.7); gl.uniform3fv(u.colors, this.palBuf);
      gl.uniform3f(u.cursor, this.hitX, this.hitZ, p.active);
      gl.uniform1f(u.curR, Math.max(1, (L.cursorRadius / 100) * (FIELD_W / 2))); gl.uniform1f(u.curS, L.cursorLift); gl.uniform1f(u.hover, hoverGlow / 100);

      gl.bindBuffer(gl.ARRAY_BUFFER, this.gridBuf); gl.enableVertexAttribArray(this.aGrid); gl.vertexAttribPointer(this.aGrid, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.seedBuf); gl.enableVertexAttribArray(this.aSeed); gl.vertexAttribPointer(this.aSeed, 2, gl.FLOAT, false, 0, 0);
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.POINTS, 0, this.count);
    }

    dispose() {
      this.pause(); this.disposed = true;
      window.removeEventListener('pointermove', this.onMove); window.removeEventListener('pointerdown', this.onDown);
      window.removeEventListener('pointerup', this.onUp); window.removeEventListener('pointercancel', this.onUp);
      window.removeEventListener('pointerleave', this.onLeave); window.removeEventListener('blur', this.onLeave);
      document.removeEventListener('visibilitychange', this.onVisibility);
    }
  }

  window.WaveField = WaveField;
})();
