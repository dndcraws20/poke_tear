// Flower Expansion background — vanilla port of the Originkit "Flower Expansion" WebGL component.
// A kaleidoscopic bloom rendered by a full-screen fragment shader. Same hooks as CellField:
//   const fx = new FlowerExpansion(canvas, { preset }).start();
//   fx.flare(a, b, ms, speedMult)   // colours are ignored; brightness + speed surge instead
//   fx.setDanger(bool)              // faster, hotter while the quota clock is under 10s
//   fx.pause() / fx.resume()        // the background manager toggles these on scene changes
(function () {
  'use strict';

  const VERT = 'attribute vec2 a_pos; void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }';
  const FRAG = [
    '#ifdef GL_FRAGMENT_PRECISION_HIGH', 'precision highp float;', '#else', 'precision mediump float;', '#endif',
    'uniform vec2 uRes; uniform float uTSpin; uniform float uTShear; uniform float uTWobble; uniform float uTHue;',
    'uniform float uDiv; uniform float uLobes; uniform float uWobble; uniform float uSharp; uniform float uEcho;',
    'uniform float uHueSpread; uniform float uSat; uniform float uExposure; uniform vec3 uBg;',
    'const float PI = 3.14159265; const float TAU = 6.28318531;',
    'vec3 hsb2rgb(float h, float s, float b) {',
    '  vec3 rgb = clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);',
    '  rgb = rgb * rgb * (3.0 - 2.0 * rgb); return b * mix(vec3(1.0), rgb, s); }',
    'float hash21(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123); }',
    'vec4 getColor(vec2 p, float x, float y, float power) {',
    '  x -= uTSpin * 0.1; float sh = fract(uTShear * 0.125);',
    '  float v0 = (x - sh + y) * uDiv; float v1 = (x + sh - y) * uDiv;',
    '  float i0 = mod(floor(v0), uDiv); float i1 = mod(floor(v1), uDiv);',
    '  float phase = uHueSpread * hash21(vec2(i0, i1));',
    '  float alpha = pow(max(sin(PI * v0) * sin(PI * v1), 0.0), power);',
    '  float r = length(p);',
    '  vec3 base = hsb2rgb(fract(uTHue * 0.1 + phase), r * 0.707 * uSat, uExposure * 2.0 * sqrt(r * 0.707));',
    '  return vec4(base, alpha); }',
    'void main() {',
    '  vec2 p = (gl_FragCoord.xy * 2.0 - uRes) / uRes.y; float y = length(p);',
    '  float x = (atan(p.y, p.x + 1e-7) + PI) / TAU;',
    '  y *= 1.0 + uWobble * sin(TAU * uLobes * x + uTWobble); y = pow(max(y, 0.0), 0.25);',
    '  vec4 c1 = getColor(p, x, y, uSharp) * 0.8;',
    '  vec4 c2 = getColor(p, x + 0.015 * uEcho, y + 0.03 * uEcho, uSharp * 1.2) * 0.6;',
    '  vec4 c3 = getColor(p, x + 0.030 * uEcho, y + 0.06 * uEcho, uSharp * 1.4) * 0.4;',
    '  vec4 col = c3;',
    '  col.rgb = (1.0 - c2.a) * col.rgb + c2.a * c2.rgb; col.a = col.a + c2.a - col.a * c2.a;',
    '  col.rgb = (1.0 - c1.a) * col.rgb + c1.a * c1.rgb; col.a = col.a + c1.a - col.a * c1.a;',
    '  float a = clamp(col.a, 0.0, 1.0); gl_FragColor = vec4(mix(uBg, col.rgb * a, a), 1.0); }',
  ].join('\n');

  // Originkit preset + component defaults (speed 35, divisions 12, sharpness 37)
  const DEFAULTS = {
    background: '#0c0618', speed: 35, divisions: 12, sharpness: 37,
    petals: { wobble: 107, lobes: 17, echo: 0, spin: 89 },
    color: { hueSpread: 108, hueSpeed: 100, saturation: 100, exposure: 100 },
    fps: 30, maxDpr: 1,
  };
  const num = (v, fb) => typeof v === 'number' && isFinite(v) ? v : fb;
  function parseColor(str, fb) {
    const h = String(str || '').replace('#', '').trim();
    if (h.length === 3) return [parseInt(h[0] + h[0], 16) / 255, parseInt(h[1] + h[1], 16) / 255, parseInt(h[2] + h[2], 16) / 255];
    if (h.length >= 6) return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
    return fb;
  }
  function compile(gl, type, src) {
    const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) { console.error('FlowerExpansion shader:', gl.getShaderInfoLog(sh)); gl.deleteShader(sh); return null; }
    return sh;
  }
  const lerp = (a, b, t) => a + (b - a) * t;

  class FlowerExpansion {
    constructor(canvas, cfg) {
      this.canvas = canvas;
      const c = Object.assign({}, DEFAULTS, cfg || {});
      c.petals = Object.assign({}, DEFAULTS.petals, (cfg && cfg.petals) || {});
      c.color = Object.assign({}, DEFAULTS.color, (cfg && cfg.color) || {});
      this.cfg = c;
      this.v = {
        bg: parseColor(c.background, [0, 0, 0]),
        div: Math.max(2, Math.round(num(c.divisions, 12))),
        lobes: Math.max(0, Math.round(num(c.petals.lobes, 6))),
        wobble: 0.25 * num(c.petals.wobble, 100) / 100,
        sharp: Math.max(0.01, num(c.sharpness, 25) / 100),
        echo: num(c.petals.echo, 100) / 100,
        hueSpread: 0.5 * num(c.color.hueSpread, 100) / 100,
        sat: num(c.color.saturation, 100) / 100,
        exposure: num(c.color.exposure, 100) / 100,
        speed: num(c.speed, 50) / 50,
        spin: num(c.petals.spin, 100) / 100,
        hueSpeed: num(c.color.hueSpeed, 100) / 100,
      };
      this.t = { spin: 0, shear: 0, wobble: 0, hue: 0 };
      this.ok = false; this.running = false; this.disposed = false; this.frameId = 0; this.last = 0; this.acc = 0;
      this.flareUntil = 0; this.flareSpeed = 1; this.danger = false; this.speedMult = 1; this.glow = 1;
      this.reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
      this.onVisibility = () => { this.last = performance.now(); };
      document.addEventListener('visibilitychange', this.onVisibility);
      this.init();
    }

    init() {
      const gl = this.canvas.getContext('webgl', { antialias: false, alpha: false, depth: false, powerPreference: 'low-power' });
      if (!gl) return;
      const vs = compile(gl, gl.VERTEX_SHADER, VERT), fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
      if (!vs || !fs) return;
      const prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { console.error('FlowerExpansion link:', gl.getProgramInfoLog(prog)); return; }
      gl.useProgram(prog);
      const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      const pos = gl.getAttribLocation(prog, 'a_pos'); gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
      this.u = {};
      ['uRes', 'uTSpin', 'uTShear', 'uTWobble', 'uTHue', 'uDiv', 'uLobes', 'uWobble', 'uSharp', 'uEcho', 'uHueSpread', 'uSat', 'uExposure', 'uBg'].forEach(n => this.u[n] = gl.getUniformLocation(prog, n));
      this.gl = gl; this.ok = true;
    }

    // Shared hooks with CellField ------------------------------------------
    flare(a, b, ms, speedMult) { this.flareUntil = performance.now() + (ms || 3000); this.flareSpeed = speedMult || 2.5; if (this.reduced) this.drawFrame(0); }
    setDanger(on) { this.danger = !!on; if (this.reduced) this.drawFrame(0); }
    setPalette() {}

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
      const now = performance.now();
      this.acc += now - this.last; this.last = now;
      if (this.acc < 1000 / this.cfg.fps) return;
      const dt = Math.min(0.1, this.acc / 1000); this.acc = 0;
      this.drawFrame(dt);
    }

    drawFrame(dt) {
      const gl = this.gl, v = this.v, u = this.u, canvas = this.canvas;
      if (!gl) return;
      const now = performance.now();
      const tSpeed = now < this.flareUntil ? this.flareSpeed : this.danger ? 2 : 1;
      const tGlow = now < this.flareUntil ? 1.5 : this.danger ? 1.25 : 1;
      const k = 1 - Math.exp(-dt * 3);
      this.speedMult = lerp(this.speedMult, tSpeed, k); this.glow = lerp(this.glow, tGlow, k);
      const step = dt * v.speed * this.speedMult;
      this.t.spin = (this.t.spin + step * v.spin + 1e4) % 1e4;
      this.t.shear = (this.t.shear + step) % 8;
      this.t.wobble = (this.t.wobble + step) % (Math.PI * 2);
      this.t.hue = (this.t.hue + step * v.hueSpeed) % 10;

      const dpr = Math.min(window.devicePixelRatio || 1, this.cfg.maxDpr);
      const cw = canvas.clientWidth || window.innerWidth, ch = canvas.clientHeight || window.innerHeight;
      const bw = Math.max(1, Math.round(cw * dpr)), bh = Math.max(1, Math.round(ch * dpr));
      if (canvas.width !== bw || canvas.height !== bh) { canvas.width = bw; canvas.height = bh; gl.viewport(0, 0, bw, bh); }

      gl.uniform2f(u.uRes, bw, bh);
      gl.uniform1f(u.uTSpin, this.t.spin); gl.uniform1f(u.uTShear, this.t.shear); gl.uniform1f(u.uTWobble, this.t.wobble); gl.uniform1f(u.uTHue, this.t.hue);
      gl.uniform1f(u.uDiv, v.div); gl.uniform1f(u.uLobes, v.lobes); gl.uniform1f(u.uWobble, v.wobble); gl.uniform1f(u.uSharp, v.sharp); gl.uniform1f(u.uEcho, v.echo);
      gl.uniform1f(u.uHueSpread, v.hueSpread); gl.uniform1f(u.uSat, v.sat); gl.uniform1f(u.uExposure, v.exposure * this.glow);
      gl.uniform3f(u.uBg, v.bg[0], v.bg[1], v.bg[2]);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    dispose() { this.pause(); this.disposed = true; document.removeEventListener('visibilitychange', this.onVisibility); }
  }

  window.FlowerExpansion = FlowerExpansion;
})();
