// Path-traced preview stills of the PaintedStatue piece (three-gpu-pathtracer, MIT).
// Rebuilds three moments of the Remotion video with real geometry instead of shader tricks:
//   ?shot=macro (t 2.6s)  ?shot=break (t 7.6s)  ?shot=rome (t 18.9s)   &spp=<samples per pixel>
// Shares the statue + fracture code with the video (src/statue/fracture.ts) and every value in config.ts.
// Bundled by scripts/pathtrace/run.cjs and rendered in headless Chromium.
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { TTFLoader } from "three/examples/jsm/loaders/TTFLoader.js";
import { Font } from "three/examples/jsm/loaders/FontLoader.js";
import { GLTFExporter } from "three/examples/jsm/exporters/GLTFExporter.js";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { WebGLPathTracer, GradientEquirectTexture, PhysicalCamera } from "three-gpu-pathtracer";
import { statueConfig as C } from "../../src/statue/config";
import { buildStatue, flight, storyTime, easeInOut, easeOut, smooth, R, F, PA, T, P } from "../../src/statue/fracture";

const q = new URLSearchParams(location.search);
const SHOT = q.get("shot") ?? "macro";
const SPP = Number(q.get("spp") ?? 64);
const W = Number(q.get("w") ?? 1920), H = Number(q.get("h") ?? 1080);
const TIME: Record<string, number> = { macro: 1.7, break: 7.6, rome: 18.9 };
const t = TIME[SHOT];
const log: string[] = []; (window as any).log = log;

// ---------- noise (JS ports of the GLSL in Statue.tsx) ----------
const fract = (x: number) => x - Math.floor(x);
const h1 = (n: number) => fract(Math.sin(n) * 43758.5453);
const n1 = (x: number) => { const i = Math.floor(x), f = x - i; return h1(i) + (h1(i + 1) - h1(i)) * f * f * (3 - 2 * f); };
const h3 = (x: number, y: number, z: number) => fract(Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453);
const n3 = (x: number, y: number, z: number) => {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  let fx = x - ix, fy = y - iy, fz = z - iz; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); fz = fz * fz * (3 - 2 * fz);
  const L = (a: number, b: number, k: number) => a + (b - a) * k;
  return L(L(L(h3(ix, iy, iz), h3(ix + 1, iy, iz), fx), L(h3(ix, iy + 1, iz), h3(ix + 1, iy + 1, iz), fx), fy),
           L(L(h3(ix, iy, iz + 1), h3(ix + 1, iy, iz + 1), fx), L(h3(ix, iy + 1, iz + 1), h3(ix + 1, iy + 1, iz + 1), fx), fy), fz);
};
const fbm = (x: number, y: number, z: number) => { let a = 0.5, s = 0; for (let i = 0; i < 4; i++) { s += a * n3(x, y, z); x *= 2.03; y *= 2.03; z *= 2.03; a *= 0.5; } return s; };
const sstep = (a: number, b: number, x: number) => { const k = Math.min(1, Math.max(0, (x - a) / (b - a))); return k * k * (3 - 2 * k); };
const paintMask = (x: number, y: number, z: number, topY: number, flow: number) => {
  if (flow <= 0 || y < -5) return 0;
  const cap = PA.capDepth, st = PA.streaks, ang = Math.atan2(z, x);
  const lobe = n1(ang * st + 3.1) * 0.6 + n1(ang * st * 2.3 + 9.0) * 0.4;
  const longDrip = Math.pow(n1(ang * st * 0.7 + 17.0), 6);
  const front = topY - Math.min(flow, cap) - Math.max(flow - cap, 0) * (0.78 + 0.32 * lobe + 1.4 * longDrip);
  const wobble = (n3(x * 9, y * 9, z * 9) - 0.5) * 0.025;
  return sstep(front - 0.006, front + 0.006, y + wobble);
};

// ---------- materials: real blood, not paint ----------
// Blood: very dark red body, near-black where thick, brighter crimson where thin, glassy wet top coat.
const BLOOD_THIN = new THREE.Color("#9A0A10"), BLOOD_THICK = new THREE.Color("#2E0003");
const blood = new THREE.MeshPhysicalMaterial({ name: "blood" } as any) as THREE.MeshPhysicalMaterial; blood.setValues({ vertexColors: true, roughness: 0.03, clearcoat: 1, clearcoatRoughness: 0.01, ior: 1.36, specularIntensity: 1 });
const bloodFlat = new THREE.MeshPhysicalMaterial({ name: "bloodFlat" } as any) as THREE.MeshPhysicalMaterial; bloodFlat.setValues({ color: "#5A0207", roughness: 0.025, clearcoat: 1, clearcoatRoughness: 0.01, ior: 1.36 });
const marble = new THREE.MeshPhysicalMaterial({ name: "marble" } as any) as THREE.MeshPhysicalMaterial; marble.setValues({ color: C.colors.marble, roughness: 0.32, clearcoat: 0.25, clearcoatRoughness: 0.4, sheen: 0.4, sheenRoughness: 0.6, sheenColor: new THREE.Color("#FFD6CC") });
const marbleRaw = new THREE.MeshPhysicalMaterial({ name: "marbleRaw" } as any) as THREE.MeshPhysicalMaterial; marbleRaw.setValues({ color: "#D9D1C4", roughness: 0.75 }); // broken insides: matte, slightly darker
const noiseTex = (seed: number, size = 1024, scale = 6) => {
  const c = document.createElement("canvas"); c.width = c.height = size; const g = c.getContext("2d")!; const img = g.createImageData(size, size);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { const v = fbm(x / size * scale, y / size * scale, seed) * 0.8 + n3(x / size * 90, y / size * 90, seed) * 0.2; const k = (y * size + x) * 4; img.data[k] = img.data[k + 1] = img.data[k + 2] = Math.round(v * 255); img.data[k + 3] = 255; }
  g.putImageData(img, 0, 0); const tex = new THREE.CanvasTexture(c); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; return tex;
};
const stoneRough = noiseTex(3.7); stoneRough.repeat.set(6, 6);
const stone = new THREE.MeshPhysicalMaterial({ name: "stone" } as any) as THREE.MeshPhysicalMaterial; stone.setValues({ color: "#1E0608", roughness: 0.55, roughnessMap: stoneRough, clearcoat: 0.15, clearcoatRoughness: 0.35 });

// ---------- helpers ----------
// Thin liquid film over a heightfield: positive f = inside the liquid. Rounded meniscus edge.
const liquidSheet = (field: (x: number, z: number) => number, x0: number, x1: number, z0: number, z1: number, res: number, height: number, edge: number) => {
  const nx = Math.round((x1 - x0) * res), nz = Math.round((z1 - z0) * res);
  const pos: number[] = [], col: number[] = [], idx: number[] = []; const id = new Int32Array((nx + 1) * (nz + 1)).fill(-1);
  const fv = new Float32Array((nx + 1) * (nz + 1));
  for (let j = 0; j <= nz; j++) for (let i = 0; i <= nx; i++) fv[j * (nx + 1) + i] = field(x0 + (x1 - x0) * i / nx, z0 + (z1 - z0) * j / nz);
  const vid = (i: number, j: number) => {
    const k = j * (nx + 1) + i; if (id[k] >= 0) return id[k];
    const f = fv[k], hk = sstep(-edge * 0.15, edge, f);
    id[k] = pos.length / 3; pos.push(x0 + (x1 - x0) * i / nx, 0.0006 + height * hk, z0 + (z1 - z0) * j / nz);
    const c = BLOOD_THIN.clone().lerp(BLOOD_THICK, Math.min(1, hk * 1.15)); col.push(c.r, c.g, c.b); return id[k];
  };
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const m = Math.max(fv[j * (nx + 1) + i], fv[j * (nx + 1) + i + 1], fv[(j + 1) * (nx + 1) + i], fv[(j + 1) * (nx + 1) + i + 1]);
    if (m < -edge * 0.15) continue;
    const a = vid(i, j), b = vid(i + 1, j), c = vid(i + 1, j + 1), d = vid(i, j + 1); idx.push(a, d, b, b, d, c);
  }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3)); g.setIndex(idx); g.computeVertexNormals();
  return g;
};

// Split outer statue surface into a marble skin + a raised blood layer (thickness follows the paint mask, so edges bead).
const paintLayer = (geos: THREE.BufferGeometry[], topY: number, flow: number) => {
  const marbleG: THREE.BufferGeometry[] = [], bloodG: THREE.BufferGeometry[] = [];
  for (const g0 of geos) {
    const g = g0.index ? g0.toNonIndexed() : g0; const pos = g.attributes.position, nor = g.attributes.normal, org = g.attributes.aOrig;
    const N = pos.count, m = new Float32Array(N);
    for (let v = 0; v < N; v++) m[v] = paintMask(org.getX(v), org.getY(v), org.getZ(v), topY, flow);
    const bp: number[] = [], bc: number[] = [];
    for (let tr = 0; tr < N; tr += 3) {
      if (Math.max(m[tr], m[tr + 1], m[tr + 2]) < 0.5) continue;
      for (let k = 0; k < 3; k++) {
        const v = tr + k, th = 0.0012 + PA.thickness * 1.1 * m[v] * (0.75 + 0.5 * n3(org.getX(v) * 30, org.getY(v) * 30, org.getZ(v) * 30));
        bp.push(pos.getX(v) + nor.getX(v) * th, pos.getY(v) + nor.getY(v) * th, pos.getZ(v) + nor.getZ(v) * th);
        const c = BLOOD_THIN.clone().lerp(BLOOD_THICK, Math.min(1, m[v] * (0.55 + 0.6 * n3(org.getX(v) * 14, org.getY(v) * 14 + 5, org.getZ(v) * 14)))); bc.push(c.r, c.g, c.b);
      }
    }
    const b = new THREE.BufferGeometry(); b.setAttribute("position", new THREE.Float32BufferAttribute(bp, 3)); b.setAttribute("color", new THREE.Float32BufferAttribute(bc, 3));
    b.computeVertexNormals(); // non-indexed: faceted; smooth by welding
    bloodG.push(b);
    const mg = new THREE.BufferGeometry(); mg.setAttribute("position", pos); mg.setAttribute("normal", nor); marbleG.push(mg);
  }
  return { marble: mergeGeometries(marbleG), blood: smoothNormals(mergeGeometries(bloodG)) };
};
const smoothNormals = (g: THREE.BufferGeometry) => {
  const p = g.attributes.position, map = new Map<string, number[]>();
  for (let v = 0; v < p.count; v++) { const k = `${Math.round(p.getX(v) * 2e4)},${Math.round(p.getY(v) * 2e4)},${Math.round(p.getZ(v) * 2e4)}`; (map.get(k) ?? map.set(k, []).get(k)!).push(v); }
  g.computeVertexNormals(); const n = g.attributes.normal;
  for (const vs of map.values()) { if (vs.length < 2) continue; const a = new THREE.Vector3(); for (const v of vs) a.add(new THREE.Vector3(n.getX(v), n.getY(v), n.getZ(v))); a.normalize(); for (const v of vs) n.setXYZ(v, a.x, a.y, a.z); }
  return g;
};
// Outer surface (group 0) or inner shell + walls (group 1) of a piece geometry, transformed.
const groupGeo = (g: THREE.BufferGeometry, gi: number, mat?: THREE.Matrix4) => {
  const gr = g.groups[gi]; const idx = g.index!; const sub = new THREE.BufferGeometry();
  for (const name of ["position", "normal", "aOrig"]) sub.setAttribute(name, g.attributes[name]);
  sub.setIndex(Array.from((idx.array as Uint32Array).slice(gr.start, gr.start + gr.count)));
  const out = sub.toNonIndexed(); if (mat) { out.applyMatrix4(mat); } return out;
};

// ---------- camera + lights (from config) ----------
const camFor = (time: number) => {
  const shots = C.camera.shots, shot = shots.find((s) => time >= s.t0 && time < s.t1) ?? shots[shots.length - 1];
  const u = (time - shot.t0) / (shot.t1 - shot.t0), sk = easeInOut(u) * 0.85 + u * 0.15;
  const cp = new THREE.Vector3(...shot.pos0).lerp(new THREE.Vector3(...shot.pos1), sk), cl = new THREE.Vector3(...shot.look0).lerp(new THREE.Vector3(...shot.look1), sk);
  return { shot, cp, cl };
};

async function main() {
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setSize(W, H); renderer.setPixelRatio(1);
  renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = Number(q.get("exp") ?? 1.0);
  document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  // dark maroon world with a soft glow overhead (the cove): lights the scene a little, reads as infinite
  const env = new GradientEquirectTexture(256); env.topColor.set("#5A1A20"); env.bottomColor.set(C.colors.fog); env.exponent = 1.6; env.update();
  scene.environment = env; scene.background = new THREE.Color(C.colors.fog); scene.environmentIntensity = 0.55;

  const { shot, cp, cl } = camFor(t);
  const cam = q.get("nodof") ? new THREE.PerspectiveCamera(shot.fov, W / H, 0.02, 60) as unknown as PhysicalCamera : new PhysicalCamera(shot.fov, W / H, 0.02, 60);
  cam.position.copy(cp); cam.up.set(0, shot.topDown ? 0 : 1, shot.topDown ? -1 : 0); cam.lookAt(cl);

  // lights: a big soft key (front-left, above) and the hidden softbox for wet highlights, both out of shot
  const L = C.light;
  const key = new THREE.RectAreaLight(C.colors.key, 9, 1.4, 1.0); key.position.set(...L.key.position); key.lookAt(0, 0.45, 0.2); scene.add(key);
  const box = new THREE.RectAreaLight("#FFE4DE", 14, L.softbox.size[0], L.softbox.size[1]); box.position.set(...L.softbox.position); box.lookAt(...L.softbox.target); scene.add(box);
  const rim = new THREE.RectAreaLight(C.colors.rimB, 10, 1.2, 0.6); rim.position.set(...L.rimB.position); rim.lookAt(0, 0.4, 0); scene.add(rim);

  if (SHOT === "rome") {
    // bird's-eye: dark stone floor with ROME carved in Cinzel capitals, the grooves brim-full of blood
    if (q.get("export")) {
      // same mask as the video (Statue.tsx drawRome): Blender carves the grooves and fills them from it
      document.fonts.add(await new FontFace("CinzelLocal", "url(fonts/Cinzel.ttf)", { weight: "700" }).load());
      const Wm = 4096, Hm = 1280, c = document.createElement("canvas"); c.width = Wm; c.height = Hm; const g = c.getContext("2d")!;
      g.fillStyle = "#000"; g.fillRect(0, 0, Wm, Hm); g.font = `${C.rome.weight} 880px CinzelLocal`; g.textAlign = "center"; g.textBaseline = "middle";
      const m = g.measureText(C.rome.text); const k = Math.min(1, (Wm * 0.92) / m.width);
      g.save(); g.translate(Wm / 2, Hm / 2 + 40); g.scale(k, 1); g.fillStyle = "#fff"; (g as any).letterSpacing = "60px"; g.fillText(C.rome.text, 0, 0); g.restore();
      const png = await new Promise<Blob>((res) => c.toBlob((b) => res(b!), "image/png"));
      await fetch(`/save?name=rome_mask.png`, { method: "POST", body: png });
      const meta = { shot: SHOT, t, fov: shot.fov, aspect: W / H, pos: cp.toArray(), look: cl.toArray(), up: cam.up.toArray(), focus: cp.distanceTo(new THREE.Vector3(C.rome.centre[0], 0, C.rome.centre[1])), fStop: 3.2, topDown: true, romeCentre: C.rome.centre, romeWidth: C.rome.width, romeAspect: Hm / Wm };
      await fetch(`/save?name=rome.json`, { method: "POST", body: JSON.stringify(meta, null, 1) });
      log.push("exported rome mask"); (window as any).exported = true; (window as any).ready = true; return;
    }
    const font = new Font(new TTFLoader().parse(await (await fetch("fonts/Cinzel.ttf")).arrayBuffer()));
    const cnv = document.createElement("canvas").getContext("2d")!;
    document.fonts.add(await new FontFace("CinzelLocal", "url(fonts/Cinzel.ttf)", { weight: "700" }).load());
    cnv.font = `${C.rome.weight} 440px CinzelLocal`; const mw = cnv.measureText(C.rome.text).width; // same metrics as the video's mask
    const worldW = (Math.min(1, 2048 * 0.92 / mw) * (mw + 30 * C.rome.text.length)) / 2048 * C.rome.width;
    // letter outlines (+ counters of R and O) laid out like the canvas mask: 440px glyphs, 30px letter spacing
    const spacing = 30 / 440, outers: THREE.Vector2[][] = [], counters: THREE.Vector2[][] = []; let x = 0;
    for (const ch of C.rome.text) {
      for (const sh of font.generateShapes(ch, 1)) {
        outers.push(sh.getPoints(24).map((p) => new THREE.Vector2(p.x + x, p.y)));
        for (const hh of sh.holes) counters.push(hh.getPoints(24).map((p) => new THREE.Vector2(p.x + x, p.y)));
      }
      x += (font.data.glyphs[ch]?.ha ?? 700) / font.data.resolution + spacing;
    }
    x -= spacing;
    let y0 = Infinity, y1 = -Infinity; for (const o of outers) for (const p of o) { y0 = Math.min(y0, p.y); y1 = Math.max(y1, p.y); }
    const sc = worldW / x;
    const place = (g: THREE.BufferGeometry) => { g.translate(-x / 2, -(y0 + y1) / 2, 0); g.scale(sc, sc, sc); g.rotateX(-Math.PI / 2); g.translate(C.rome.centre[0], 0, C.rome.centre[1]); return g; };
    log.push(`ROME width ${worldW.toFixed(3)} world units, ${outers.length} outlines, ${counters.length} counters`);
    // stone slab with letter-shaped holes; the counters of R and O are islands of stone; chiselled lip
    const cx = x / 2, cy = (y0 + y1) / 2, BIG = 40 / sc;
    const slab = new THREE.Shape([new THREE.Vector2(cx - BIG, cy - BIG), new THREE.Vector2(cx + BIG, cy - BIG), new THREE.Vector2(cx + BIG, cy + BIG), new THREE.Vector2(cx - BIG, cy + BIG)]);
    slab.holes = outers.map((o) => new THREE.Path(o));
    const islands = counters.map((c) => new THREE.Shape(c));
    const bev = { bevelEnabled: true, bevelThickness: 0.004 / sc, bevelSize: 0.003 / sc, bevelSegments: 3, curveSegments: 24 };
    const slabG = place(new THREE.ExtrudeGeometry([slab, ...islands], { depth: 0.03 / sc, ...bev }));
    slabG.translate(0, -0.034, 0); // top face (with bevel) at y = 0
    scene.add(new THREE.Mesh(slabG, stone));
    // blood in the grooves: letters inset a hair, rounded meniscus, top just under the stone surface
    const letters = outers.map((o, i) => { const sh = new THREE.Shape(o); sh.holes = counters.filter((c) => { const p = c[0]; let inside = false; for (let a = 0, b = o.length - 1; a < o.length; b = a++) if ((o[a].y > p.y) !== (o[b].y > p.y) && p.x < ((o[b].x - o[a].x) * (p.y - o[a].y)) / (o[b].y - o[a].y) + o[a].x) inside = !inside; return inside; }).map((c) => new THREE.Path(c)); return sh; });
    const fillG = place(new THREE.ExtrudeGeometry(letters, { depth: 0.02 / sc, bevelEnabled: true, bevelThickness: 0.0035 / sc, bevelSize: 0.0035 / sc, bevelOffset: -0.0045 / sc, bevelSegments: 6, curveSegments: 24 }));
    fillG.translate(0, -0.0245, 0);
    scene.add(new THREE.Mesh(fillG, bloodFlat));
    // groove floor (dark) below the blood, in case of gaps
    const floorUnder = new THREE.Mesh(new THREE.PlaneGeometry(80, 80).rotateX(-Math.PI / 2), stone); floorUnder.position.y = -0.03; scene.add(floorUnder);
    cam.fStop = 3.2; cam.focusDistance = cp.distanceTo(new THREE.Vector3(C.rome.centre[0], 0, C.rome.centre[1])); cam.apertureBlades = 7;
  } else {
    const raw = new STLLoader().parse(await (await fetch(SHOT === "macro" ? C.model : "models/bearded-man-200k.stl")).arrayBuffer());
    const st = buildStatue(raw); log.push(`statue built: ${st.pieces.length} pieces`);
    const flow = PA.speed * Math.pow(Math.max(0, t - T.paintStart), PA.slowdown);
    const s = storyTime(t);
    const outer: THREE.BufferGeometry[] = [groupGeo(st.stump, 0)], inner: THREE.BufferGeometry[] = [];
    const broken = t >= T.boom;
    st.pieces.forEach((p, i) => {
      const restY = Math.max(0.03, p.radius * 0.45); const f = flight(`pc${i}`, p.centre, st.headCentre, restY, s);
      const sp = new THREE.Vector3(R(`w1${i}`) - 0.5, R(`w2${i}`) - 0.5, R(`w3${i}`) - 0.5).multiplyScalar(7);
      const mtx = new THREE.Matrix4().compose(f.pos, new THREE.Quaternion().setFromEuler(new THREE.Euler(sp.x * f.tau, sp.y * f.tau, sp.z * f.tau)), new THREE.Vector3(1, 1, 1));
      outer.push(groupGeo(p.geo, 0, mtx)); if (broken) inner.push(groupGeo(p.geo, 1, mtx));
    });
    const layer = paintLayer(outer, st.topY, flow);
    scene.add(new THREE.Mesh(layer.marble, marble), new THREE.Mesh(layer.blood, blood));
    if (inner.length) scene.add(new THREE.Mesh(mergeGeometries(inner.map((g) => { const o = new THREE.BufferGeometry(); o.setAttribute("position", g.attributes.position); o.setAttribute("normal", g.attributes.normal); return o; })), marbleRaw));
    if (broken) { // chips of marble and blood
      const chips: THREE.BufferGeometry[] = [], bchips: THREE.BufferGeometry[] = [];
      for (let i = 0; i < C.particles.chips; i++) {
        const start = st.samples[i % st.samples.length], sz = 0.004 + R(`cs${i}`) * 0.012; const f = flight(`ch${i}`, start, st.headCentre, sz, s, 1.15);
        const g = new THREE.IcosahedronGeometry(sz, 0); g.applyMatrix4(new THREE.Matrix4().compose(f.pos, new THREE.Quaternion().setFromEuler(new THREE.Euler(f.tau * 9 * R(`cr1${i}`), f.tau * 9 * R(`cr2${i}`), 0)), new THREE.Vector3(1, 1, 1)));
        (R(`cc${i}`) < 0.4 ? bchips : chips).push(g);
      }
      scene.add(new THREE.Mesh(mergeGeometries(chips), marbleRaw), new THREE.Mesh(mergeGeometries(bchips), bloodFlat));
    }
    // floor: dark polished stone, infinite; the pool is a real liquid film with a rounded edge
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60).rotateX(-Math.PI / 2), stone); scene.add(floor);
    const pool = PA.poolMax * (1 - Math.exp(-Math.max(0, t - PA.floorReach) / (PA.poolGrow / 3)));
    if (pool > 0.01) {
      const field = (x: number, z: number) => {
        const qx = Math.abs(x) - P.w / 2, qz = Math.abs(z) - P.d / 2; const dBox = Math.hypot(Math.max(qx, 0), Math.max(qz, 0)) + Math.min(Math.max(qx, qz), 0);
        const edge = (fbm(x * 2.2, z * 2.2, 1) - 0.5) * 0.9 * pool + (n3(x * 9, z * 9, 4) - 0.5) * 0.04; const l = Math.hypot(x, z) + 1e-4;
        return pool * (0.75 + 0.5 * fbm(x / l * 1.7, z / l * 1.7, 2)) + edge - dBox;
      };
      const ext = P.w / 2 + pool * 1.6;
      scene.add(new THREE.Mesh(liquidSheet(field, -ext, ext, -ext, ext, 220, 0.006, 0.03), blood));
    }
    const focusP = SHOT === "macro" ? new THREE.Vector3(0.05, 0.6, 0.3) : st.headCentre;
    cam.fStop = SHOT === "macro" ? 2.0 : 2.8; cam.focusDistance = cp.distanceTo(focusP); cam.apertureBlades = 7;
  }

  if (q.get("export")) {
    // hand the scene to Blender: meshes as GLB (three.js Y-up; Blender's importer converts), camera + DOF as JSON
    const group = new THREE.Group(); scene.children.filter((o) => (o as THREE.Mesh).isMesh).forEach((o) => group.add(o.clone()));
    group.traverse((o) => { const m = (o as THREE.Mesh).material as THREE.MeshPhysicalMaterial; if (m && m.roughnessMap) { const c = m.clone(); c.roughnessMap = null; c.name = m.name; (o as THREE.Mesh).material = c; } });
    const glb = await new GLTFExporter().parseAsync(group, { binary: true }) as ArrayBuffer;
    await fetch(`/save?name=${SHOT}.glb`, { method: "POST", body: glb });
    const cl2 = cl; const meta = { shot: SHOT, t, fov: shot.fov, aspect: W / H, pos: cp.toArray(), look: cl2.toArray(), up: cam.up.toArray(), focus: cam.focusDistance, fStop: cam.fStop, topDown: !!shot.topDown };
    await fetch(`/save?name=${SHOT}.json`, { method: "POST", body: JSON.stringify(meta, null, 1) });
    log.push(`exported ${SHOT}.glb (${(glb.byteLength / 1e6).toFixed(1)} MB)`); (window as any).exported = true; (window as any).ready = true; return;
  }
  const pt = new WebGLPathTracer(renderer);
  pt.renderDelay = 0; pt.minSamples = 0; pt.fadeDuration = 0; pt.dynamicLowRes = false; pt.rasterizeScene = false;
  pt.tiles.set(Number(q.get("tiles") ?? 3), Number(q.get("tiles") ?? 3)); pt.bounces = 8; pt.transmissiveBounces = 6; pt.filterGlossyFactor = 0.3; pt.multipleImportanceSampling = true;
  const t0 = performance.now(); pt.setScene(scene, cam); log.push(`setScene ${((performance.now() - t0) / 1000).toFixed(1)}s`);
  (window as any).pt = pt;
  (window as any).runSamples = (n: number) => { const a = performance.now(); const target = Math.floor(pt.samples) + n; while (pt.samples < target) pt.renderSample(); renderer.getContext().finish(); return `${pt.samples.toFixed(0)}/${SPP} spp (+${n} in ${((performance.now() - a) / 1000).toFixed(1)}s)`; };
  (window as any).SPP = SPP;
  (window as any).ready = true;
}
main().catch((e) => { log.push("ERROR " + (e?.stack ?? e)); (window as any).failed = String(e); });
