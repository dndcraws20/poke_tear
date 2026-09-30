// Cell Field background — vanilla port of the Originkit "Cell Field" React component.
// Dots on a grid are coloured by the nearest of a handful of drifting seeds (a soft Voronoi),
// the pointer acts as an extra seed, and the game can "flare" the palette for big pulls.
//
//   const fx = new CellField(canvas, { colorA: '#5b2a9e', colorB: '#ff9800', alpha: .35 }).start();
//   fx.flare('#ff1a1a', '#ffda00', 4000, 3);   // fire palette for 4s at 3x speed
//   fx.setDanger(true);                         // hold a red tint until setDanger(false)
(function () {
  'use strict';

  const DEFAULTS = {
    colorA: '#5b2a9e', colorB: '#ff9800', alpha: 0.35,
    cells: 12, count: 9, size: 8, edge: 13, speed: 8, strength: 20,
    followPointer: true, fps: 30,
  };

  const clamp = (v, lo, hi, fb) => Math.max(lo, Math.min(hi, typeof v === 'number' && isFinite(v) ? v : fb));
  const settingsFor = cfg => ({
    cell: 250 - clamp(cfg.cells, 1, 20, DEFAULTS.cells) * 9.5,
    spacing: 54 - clamp(cfg.count, 1, 20, DEFAULTS.count) * 1.9,
    size: 0.6 + clamp(cfg.size, 1, 20, DEFAULTS.size) * 0.14,
    edge: 0.04 + clamp(cfg.edge, 1, 20, DEFAULTS.edge) * 0.036,
    speed: 6 + clamp(cfg.speed, 0, 20, DEFAULTS.speed) * 5,
    bias: 0.6 + clamp(cfg.strength, 1, 20, DEFAULTS.strength) * 0.045,
  });
  function parseHex(hex) {
    const h = String(hex || '').replace('#', '').trim();
    if (h.length === 3) return [parseInt(h[0] + h[0], 16), parseInt(h[1] + h[1], 16), parseInt(h[2] + h[2], 16)];
    if (h.length >= 6) return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
    return [128, 128, 128];
  }
  const lerp = (a, b, t) => a + (b - a) * t;
  const lerp3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

  class CellField {
    constructor(canvas, cfg) {
      this.canvas = canvas;
      this.cfg = Object.assign({}, DEFAULTS, cfg || {});
      this.ctx = canvas.getContext('2d');
      this.seeds = []; this.width = 0; this.height = 0; this.dpr = 1;
      this.frameId = 0; this.lastT = 0; this.acc = 0; this.tintSeq = 0; this.disposed = false;
      this.px = -1; this.py = -1; this.tx = -1; this.ty = -1; this.grip = 0; this.gripTarget = 0;
      // palette state: current colours ease toward the target, which is base, danger or a flare
      this.baseA = parseHex(this.cfg.colorA); this.baseB = parseHex(this.cfg.colorB);
      this.curA = this.baseA.slice(); this.curB = this.baseB.slice();
      this.flareUntil = 0; this.flareA = null; this.flareB = null; this.flareSpeed = 1;
      this.danger = false; this.speedMult = 1; this.alphaMult = 1;
      this.reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

      this.onMove = e => {
        this.tx = e.clientX; this.ty = e.clientY;
        if (this.px < 0) { this.px = this.tx; this.py = this.ty; }
        this.gripTarget = 1;
      };
      this.onLeave = () => { this.gripTarget = 0; };
      this.onResize = () => this.setSize(window.innerWidth, window.innerHeight);
      this.onVisibility = () => { this.lastT = performance.now(); };
      window.addEventListener('pointermove', this.onMove, { passive: true });
      window.addEventListener('pointerdown', this.onMove, { passive: true });
      window.addEventListener('pointerleave', this.onLeave);
      window.addEventListener('blur', this.onLeave);
      window.addEventListener('resize', this.onResize);
      document.addEventListener('visibilitychange', this.onVisibility);
    }

    wanted(S) {
      const area = ((this.width || 300) * (this.height || 300)) / (S.cell * S.cell);
      return Math.max(2, Math.min(40, Math.round(area)));
    }
    spawn(S) {
      const a = Math.random() * Math.PI * 2;
      this.seeds.push({ x: Math.random() * (this.width || 300), y: Math.random() * (this.height || 300), vx: Math.cos(a) * S.speed, vy: Math.sin(a) * S.speed, tint: (this.tintSeq++ * 0.6180339887) % 1 });
    }
    build() { const S = settingsFor(this.cfg); this.seeds = []; const n = this.wanted(S); for (let i = 0; i < n; i++) this.spawn(S); }

    setSize(width, height) {
      if (this.disposed || width <= 0 || height <= 0) return;
      this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      const first = this.width === 0;
      if (!first) { const kx = width / this.width, ky = height / this.height; this.seeds.forEach(s => { s.x *= kx; s.y *= ky; }); }
      this.width = width; this.height = height;
      this.canvas.width = Math.round(width * this.dpr); this.canvas.height = Math.round(height * this.dpr);
      this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      if (first || !this.seeds.length) this.build();
    }

    start() {
      this.setSize(window.innerWidth, window.innerHeight);
      if (this.reduced) { this.drawStatic(); return this; }
      this.lastT = performance.now();
      const loop = () => { this.frameId = requestAnimationFrame(loop); this.tick(); };
      loop();
      return this;
    }

    // Public palette controls -------------------------------------------------
    setPalette(a, b) { this.baseA = parseHex(a); this.baseB = parseHex(b); }
    flare(a, b, ms, speedMult) {
      this.flareA = parseHex(a); this.flareB = parseHex(b);
      this.flareUntil = performance.now() + (ms || 3000); this.flareSpeed = speedMult || 2.5;
      if (this.reduced) this.drawStatic();
    }
    setDanger(on) { if (this.danger !== !!on) { this.danger = !!on; if (this.reduced) this.drawStatic(); } }

    targetPalette(now) {
      if (this.flareA && now < this.flareUntil) return [this.flareA, this.flareB, this.flareSpeed, 1.6];
      if (this.danger) return [[255, 45, 45], [255, 152, 0], 1.8, 1.35];
      return [this.baseA, this.baseB, 1, 1];
    }

    tick() {
      if (this.disposed || document.hidden) return;
      const now = performance.now();
      let dt = (now - this.lastT) / 1000;
      if (!isFinite(dt) || dt < 0) dt = 0;
      if (dt > 0.05) dt = 0.05;
      this.acc += now - this.lastT; this.lastT = now;
      if (this.acc < 1000 / this.cfg.fps) return; // frame cap
      const frameDt = Math.min(0.1, this.acc / 1000); this.acc = 0;
      this.step(frameDt, now);
    }

    step(dt, now) {
      const S = settingsFor(this.cfg);
      const [ta, tb, tSpeed, tAlpha] = this.targetPalette(now);
      const k = 1 - Math.exp(-dt * 3);
      this.curA = lerp3(this.curA, ta, k); this.curB = lerp3(this.curB, tb, k);
      this.speedMult = lerp(this.speedMult, tSpeed, k); this.alphaMult = lerp(this.alphaMult, tAlpha, k);

      const want = this.wanted(S);
      if (this.seeds.length < want) this.spawn(S); else if (this.seeds.length > want) this.seeds.pop();

      if (this.px >= 0) { const kp = 1 - Math.exp(-dt * 12); this.px += (this.tx - this.px) * kp; this.py += (this.ty - this.py) * kp; }
      const hover = this.cfg.followPointer && this.px >= 0 ? this.gripTarget : 0;
      this.grip += (hover - this.grip) * (1 - Math.exp(-dt * 4));

      const sp = S.speed * this.speedMult;
      for (const s of this.seeds) {
        const n = Math.hypot(s.vx, s.vy) || 1;
        s.x += (s.vx / n) * sp * dt; s.y += (s.vy / n) * sp * dt;
        if (s.x < 0) { s.x = -s.x; s.vx = Math.abs(s.vx); } else if (s.x > this.width) { s.x = 2 * this.width - s.x; s.vx = -Math.abs(s.vx); }
        if (s.y < 0) { s.y = -s.y; s.vy = Math.abs(s.vy); } else if (s.y > this.height) { s.y = 2 * this.height - s.y; s.vy = -Math.abs(s.vy); }
      }
      this.draw(S);
    }

    drawStatic() { this.draw(settingsFor(this.cfg), true); }

    draw(S, still) {
      const ctx = this.ctx, w = this.width, h = this.height;
      ctx.clearRect(0, 0, w, h);
      const a = still ? this.targetPalette(performance.now())[0] : this.curA;
      const b = still ? this.targetPalette(performance.now())[1] : this.curB;
      const step = Math.max(8, S.spacing);
      const cols = Math.ceil(w / step) + 1, rows = Math.ceil(h / step) + 1;
      const ox = (w - (cols - 1) * step) * 0.5, oy = (h - (rows - 1) * step) * 0.5;
      const cursorLive = !still && this.grip > 0.02 && this.px >= 0;
      const seeds = this.seeds, alpha = Math.min(1, this.cfg.alpha * (still ? 1 : this.alphaMult));
      for (let r = 0; r < rows; r++) {
        const y = oy + r * step;
        for (let c = 0; c < cols; c++) {
          const x = ox + c * step;
          let best = Infinity, second = Infinity, tint = 0;
          for (let i = 0; i < seeds.length; i++) {
            const dx = x - seeds[i].x, dy = y - seeds[i].y, d = dx * dx + dy * dy;
            if (d < best) { second = best; best = d; tint = seeds[i].tint; } else if (d < second) second = d;
          }
          if (cursorLive) {
            const dx = x - this.px, dy = y - this.py, d = ((dx * dx + dy * dy) / S.bias) * (1 / this.grip);
            if (d < best) { second = best; best = d; tint = 0.5; } else if (d < second) second = d;
          }
          const d1 = Math.sqrt(best), d2 = Math.sqrt(second === Infinity ? best : second);
          const own = d1 + d2 > 0.001 ? (d2 - d1) / (d2 + d1) : 1;
          const solid = Math.min(1, own / S.edge);
          const rr = Math.round(a[0] + (b[0] - a[0]) * tint), gg = Math.round(a[1] + (b[1] - a[1]) * tint), bb = Math.round(a[2] + (b[2] - a[2]) * tint);
          ctx.fillStyle = 'rgba(' + rr + ',' + gg + ',' + bb + ',' + ((0.12 + solid * 0.8) * alpha).toFixed(3) + ')';
          ctx.beginPath(); ctx.arc(x, y, S.size * (0.45 + solid * 0.75), 0, Math.PI * 2); ctx.fill();
        }
      }
    }

    dispose() {
      this.disposed = true; cancelAnimationFrame(this.frameId);
      window.removeEventListener('pointermove', this.onMove); window.removeEventListener('pointerdown', this.onMove);
      window.removeEventListener('pointerleave', this.onLeave); window.removeEventListener('blur', this.onLeave);
      window.removeEventListener('resize', this.onResize); document.removeEventListener('visibilitychange', this.onVisibility);
    }
  }

  window.CellField = CellField;
})();
