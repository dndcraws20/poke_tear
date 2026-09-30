// 3D booster pack — a pillow-shaped foil packet rendered with Three.js, textured with the set's
// existing 2D pack art. Sits over an <img> (kept for layout + fallback), tilts toward the pointer,
// catches a sweeping highlight, and can be "torn" by clipping its top when the opening animation runs.
//
//   const pack = new Pack3D(hostEl, imgEl, { watchOpened: true });
//   pack.setImage(url)  // or just change imgEl.src — it watches the attribute
//   pack.pause() / pack.resume() / pack.dispose()
(function () {
  'use strict';

  const CANVAS_SCALE = { x: 1.5, y: 1.4 }; // canvas overflows the image box so a tilted pack isn't cropped
  const BULGE = 0.075;                     // pillow depth relative to pack height
  const CRIMP = 0.07;                      // flat sealed strip at top and bottom (fraction of height)

  function makeEnvMap(renderer) {
    // Small procedural studio environment: dark violet floor, bright soft window, warm rim.
    const c = document.createElement('canvas'); c.width = 256; c.height = 128;
    const g = c.getContext('2d');
    const sky = g.createLinearGradient(0, 0, 0, 128);
    sky.addColorStop(0, '#f6f0ff'); sky.addColorStop(0.45, '#6d4bb4'); sky.addColorStop(0.55, '#2a1650'); sky.addColorStop(1, '#07030f');
    g.fillStyle = sky; g.fillRect(0, 0, 256, 128);
    const win = g.createRadialGradient(70, 38, 4, 70, 38, 60); win.addColorStop(0, 'rgba(255,255,255,1)'); win.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = win; g.fillRect(0, 0, 256, 128);
    const warm = g.createRadialGradient(200, 60, 4, 200, 60, 70); warm.addColorStop(0, 'rgba(255,190,90,.9)'); warm.addColorStop(1, 'rgba(255,190,90,0)');
    g.fillStyle = warm; g.fillRect(0, 0, 256, 128);
    const tex = new THREE.CanvasTexture(c); tex.mapping = THREE.EquirectangularReflectionMapping; tex.colorSpace = THREE.SRGBColorSpace;
    const pmrem = new THREE.PMREMGenerator(renderer); pmrem.compileEquirectangularShader();
    const env = pmrem.fromEquirectangular(tex).texture; pmrem.dispose(); tex.dispose();
    return env;
  }

  function pillowGeometry(w, h, front) {
    const geo = new THREE.PlaneGeometry(w, h, 40, 64);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), y = pos.getY(i);
      const u = x / w + 0.5, v = y / h + 0.5;
      let z = 0;
      if (v > CRIMP && v < 1 - CRIMP) {
        const vv = (v - CRIMP) / (1 - 2 * CRIMP);
        z = h * BULGE * Math.pow(Math.sin(Math.PI * u), 0.55) * Math.pow(Math.sin(Math.PI * vv), 0.5);
      } else {
        // sealed crimp: tiny ripple so the foil edge catches light
        z = h * 0.004 * Math.sin(u * Math.PI * 22);
      }
      pos.setZ(i, front ? z : -z);
    }
    geo.computeVertexNormals();
    return geo;
  }

  class Pack3D {
    constructor(host, img, opts) {
      this.host = host; this.img = img; this.opts = opts || {};
      this.ok = false; this.running = false; this.disposed = false; this.frameId = 0;
      this.tilt = { x: 0, y: 0 }; this.target = { x: 0, y: 0 }; this.pointerNear = 0; this.t0 = performance.now();
      this.clip = 0;
      if (!window.THREE || !img) return;
      this.reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
      try { this.setup(); } catch (e) { console.warn('Pack3D setup failed', e); this.ok = false; return; }
      this.onMove = e => {
        const r = this.host.getBoundingClientRect(); if (!r.width) return;
        const nx = (e.clientX - (r.left + r.width / 2)) / (r.width * 1.6), ny = (e.clientY - (r.top + r.height / 2)) / (r.height * 1.6);
        this.target.y = Math.max(-0.55, Math.min(0.55, nx * 1.1));
        this.target.x = Math.max(-0.4, Math.min(0.4, ny * 0.8));
        this.pointerNear = Math.max(0, 1 - Math.hypot(nx, ny) * 0.9);
      };
      this.onLeave = () => { this.target.x = 0; this.target.y = 0; this.pointerNear = 0; };
      window.addEventListener('pointermove', this.onMove, { passive: true });
      window.addEventListener('pointerleave', this.onLeave); window.addEventListener('blur', this.onLeave);
      this.srcObserver = new MutationObserver(() => this.setImage(this.img.getAttribute('src')));
      this.srcObserver.observe(this.img, { attributes: true, attributeFilter: ['src'] });
      if (this.opts.watchOpened) {
        this.openObserver = new MutationObserver(() => { this.clipTarget = this.host.classList.contains('opened') ? 0.13 : 0; });
        this.openObserver.observe(this.host, { attributes: true, attributeFilter: ['class'] });
      }
      this.clipTarget = 0;
      this.ro = new ResizeObserver(() => this.resize()); this.ro.observe(this.host);
      this.setImage(this.img.getAttribute('src'));
    }

    setup() {
      const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
      renderer.localClippingEnabled = true;
      const canvas = renderer.domElement; canvas.className = 'pack3d-canvas'; canvas.setAttribute('aria-hidden', 'true');
      this.host.appendChild(canvas);
      this.renderer = renderer; this.canvas = canvas;
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(28, 1, 0.1, 50);
      this.env = makeEnvMap(renderer);
      this.scene.environment = this.env;
      this.scene.add(new THREE.AmbientLight(0xffffff, 0.35));
      const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(2, 3, 4); this.scene.add(key);
      const rim = new THREE.DirectionalLight(0xb388ff, 1.1); rim.position.set(-3, 1, -2); this.scene.add(rim);
      this.sweep = new THREE.PointLight(0xffe0a0, 6, 12, 1.6); this.sweep.position.set(2, 2, 2.5); this.scene.add(this.sweep);
      this.group = new THREE.Group(); this.scene.add(this.group);
      this.clipPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 10); // moves down to "tear" the top
      this.loader = new THREE.TextureLoader(); this.loader.setCrossOrigin('anonymous');
      this.ok = true;
    }

    setImage(src) {
      if (!this.ok || !src) return;
      const token = this.loadToken = (this.loadToken || 0) + 1;
      this.loader.load(src, tex => {
        if (token !== this.loadToken || this.disposed) { tex.dispose(); return; }
        tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
        this.buildPack(tex); this.img.classList.add('pack3d-hidden'); this.canvas.style.visibility = 'visible'; this.resume();
      }, undefined, () => {
        // cross-origin art without CORS headers (some shop CDNs) -> keep the flat image
        if (token !== this.loadToken) return;
        this.img.classList.remove('pack3d-hidden'); this.canvas.style.visibility = 'hidden'; this.pause();
      });
    }

    buildPack(tex) {
      if (this.pack) { this.group.remove(this.pack); this.pack.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) { if (o.material.map) o.material.map.dispose(); o.material.dispose(); } }); }
      const iw = tex.image.naturalWidth || tex.image.width, ih = tex.image.naturalHeight || tex.image.height;
      const h = 1, w = Math.max(0.3, Math.min(1.2, iw / ih));
      this.aspect = w / h;
      const front = new THREE.Mesh(pillowGeometry(w, h, true), new THREE.MeshPhysicalMaterial({
        map: tex, roughness: 0.38, metalness: 0.22, clearcoat: 1, clearcoatRoughness: 0.18, envMapIntensity: 1.1,
        clippingPlanes: [this.clipPlane], side: THREE.FrontSide,
      }));
      // back: same pillow turned around, so it bulges the other way and shows the art darkened (foil backside)
      const back = new THREE.Mesh(pillowGeometry(w, h, true), new THREE.MeshPhysicalMaterial({
        map: tex, color: 0x8f86a8, roughness: 0.5, metalness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.3, envMapIntensity: 0.9,
        clippingPlanes: [this.clipPlane], side: THREE.FrontSide,
      }));
      back.rotation.y = Math.PI;
      this.pack = new THREE.Group(); this.pack.add(front, back); this.group.add(this.pack);
      this.resize();
    }

    resize() {
      if (!this.ok) return;
      // layout size (ignores CSS transforms such as the opening overlay's scale-in animation)
      const bw = this.host.clientWidth || this.img.clientWidth || 200, bh = this.host.clientHeight || this.img.clientHeight || 340;
      const cw = Math.round(bw * CANVAS_SCALE.x), ch = Math.round(bh * CANVAS_SCALE.y);
      this.renderer.setSize(cw, ch, false);
      this.canvas.style.width = cw + 'px'; this.canvas.style.height = ch + 'px';
      this.canvas.style.left = Math.round((bw - cw) / 2) + 'px'; this.canvas.style.top = Math.round((bh - ch) / 2) + 'px';
      this.camera.aspect = cw / ch;
      // pack height is 1 world unit; make it fill the image box's share of the canvas height
      const visibleH = CANVAS_SCALE.y * 1.0;
      this.camera.position.set(0, 0, (visibleH / 2) / Math.tan((this.camera.fov / 2) * Math.PI / 180));
      this.camera.updateProjectionMatrix();
      this.render(0);
    }

    resume() { if (!this.ok || this.running || this.disposed) return; this.running = true; const loop = () => { if (!this.running) return; this.frameId = requestAnimationFrame(loop); this.tick(); }; loop(); }
    pause() { this.running = false; cancelAnimationFrame(this.frameId); }
    visible() { return !document.hidden && this.host.offsetParent !== null && this.host.getBoundingClientRect().width > 0; }

    tick() {
      if (!this.visible()) return;
      this.render((performance.now() - this.t0) / 1000);
    }

    render(t) {
      if (!this.pack) return;
      const k = 0.12;
      this.tilt.x += (this.target.x - this.tilt.x) * k; this.tilt.y += (this.target.y - this.tilt.y) * k;
      const idle = this.reduced ? 0 : 1;
      this.pack.rotation.x = this.tilt.x + Math.sin(t * 0.9) * 0.05 * idle;
      this.pack.rotation.y = this.tilt.y + Math.sin(t * 0.6) * 0.16 * idle;
      this.pack.rotation.z = Math.sin(t * 0.5) * 0.02 * idle;
      this.pack.position.y = Math.sin(t * 1.1) * 0.02 * idle;
      const a = t * 0.8;
      this.sweep.position.set(Math.cos(a) * 2.4, 1.2 + Math.sin(a * 0.7) * 1.2, 2.2);
      this.sweep.intensity = 5 + this.pointerNear * 5;
      this.clip += ((this.clipTarget || 0) - this.clip) * 0.2;
      this.clipPlane.constant = 0.5 - this.clip; // plane y <= 0.5 - clip keeps everything below the torn edge
      this.renderer.render(this.scene, this.camera);
    }

    dispose() {
      this.pause(); this.disposed = true;
      window.removeEventListener('pointermove', this.onMove); window.removeEventListener('pointerleave', this.onLeave); window.removeEventListener('blur', this.onLeave);
      if (this.srcObserver) this.srcObserver.disconnect(); if (this.openObserver) this.openObserver.disconnect(); if (this.ro) this.ro.disconnect();
      if (this.renderer) { this.renderer.dispose(); if (this.canvas.parentNode) this.canvas.parentNode.removeChild(this.canvas); }
      this.img.classList.remove('pack3d-hidden');
    }
  }

  window.Pack3D = Pack3D;
})();
