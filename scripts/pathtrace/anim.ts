// Export the whole PaintedStatue animation for Blender (scripts/blender/build_anim.py).
// Run: ENTRY=anim PT_OUT=<dir> node scripts/pathtrace/run.cjs anim 1 x.png "model=models/bearded-man-200k.stl"
// Writes to <dir>:
//   pieces.glb   stump + every piece as its own mesh in LOCAL coordinates (outer surface only; Blender solidifies),
//                each vertex carries paintT0/paintT1 (seconds when the blood sheet starts / finishes covering it)
//   chips.glb    one small chip per object
//   anim.json    per frame: piece + chip transforms, camera, depth of field, fade and the floor/ROME/dust values
//   floor/m_0001.png ...  top-down liquid map per frame (pool + splats + rivulets), from the video's floor formula
//   rome_mask.png the video's letter mask (Blender carves + fills the letters)
// Everything is computed from src/statue/config.ts and src/statue/fracture.ts, exactly like the video.
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { GLTFExporter } from "three/examples/jsm/exporters/GLTFExporter.js";
import { statueConfig as C } from "../../src/statue/config";
import { buildStatue, flight, storyTime, easeInOut, easeOut, smooth, clamp, R, F, PA, T, P } from "../../src/statue/fracture";

const q = new URLSearchParams(location.search);
const log: string[] = []; (window as any).log = log;
const FPS = C.output.fps, N = Math.round(C.output.durationInSeconds * FPS);
const save = (name: string, body: BodyInit) => fetch(`/save?name=${encodeURIComponent(name)}`, { method: "POST", body });

// ---- noise (JS ports of the GLSL in Statue.tsx, for the paint arrival times) ----
const fract = (x: number) => x - Math.floor(x);
const h1 = (n: number) => fract(Math.sin(n) * 43758.5453);
const n1 = (x: number) => { const i = Math.floor(x), f = x - i; return h1(i) + (h1(i + 1) - h1(i)) * f * f * (3 - 2 * f); };
const h3 = (x: number, y: number, z: number) => fract(Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453);
const n3 = (x: number, y: number, z: number) => {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z); let fx = x - ix, fy = y - iy, fz = z - iz;
  fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); fz = fz * fz * (3 - 2 * fz); const L = (a: number, b: number, k: number) => a + (b - a) * k;
  return L(L(L(h3(ix, iy, iz), h3(ix + 1, iy, iz), fx), L(h3(ix, iy + 1, iz), h3(ix + 1, iy + 1, iz), fx), fy), L(L(h3(ix, iy, iz + 1), h3(ix + 1, iy, iz + 1), fx), L(h3(ix, iy + 1, iz + 1), h3(ix + 1, iy + 1, iz + 1), fx), fy), fz);
};
// Time at which the paint front has travelled depth d below the crown along a streak with spread k.
const timeForDepth = (d: number, k: number) => {
  if (d <= 0) return T.paintStart;
  const flow = d <= PA.capDepth ? d : PA.capDepth + (d - PA.capDepth) / k;
  return T.paintStart + Math.pow(flow / PA.speed, 1 / PA.slowdown);
};
const paintTimes = (x: number, y: number, z: number, topY: number) => {
  const st = PA.streaks, ang = Math.atan2(z, x);
  const lobe = n1(ang * st + 3.1) * 0.6 + n1(ang * st * 2.3 + 9.0) * 0.4, longDrip = Math.pow(n1(ang * st * 0.7 + 17.0), 6);
  const k = 0.78 + 0.32 * lobe + 1.4 * longDrip, wob = (n3(x * 9, y * 9, z * 9) - 0.5) * 0.025;
  const d = topY - (y + wob);
  return [timeForDepth(d - 0.006, k), timeForDepth(d + 0.006, k)]; // mask 0 -> 1
};

// ---- floor liquid map: same maths as Statue.tsx makeFloor (pool, splats, rivulets), written as a plain shader ----
const MAX_SPLATS = 24;
const MAP = { x0: -2.0, x1: 2.0, z0: -2.0, z1: 2.2, px: 2048 };
const floorFrag = /* glsl */ `
precision highp float;
varying vec2 vXZ;
uniform float uPool, uHalfW, uHalfD, uStream, uDrain, uCarve, uRomeW, uRomeA;
uniform vec2 uRomeC; uniform float uStreamX[4]; uniform vec4 uSplats[${MAX_SPLATS}];
float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float n3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h3(i), h3(i+vec3(1,0,0)), f.x), mix(h3(i+vec3(0,1,0)), h3(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i+vec3(0,0,1)), h3(i+vec3(1,0,1)), f.x), mix(h3(i+vec3(0,1,1)), h3(i+vec3(1,1,1)), f.x), f.y), f.z); }
float fbm(vec3 p){ float a = 0.5, s = 0.0; for (int i = 0; i < 4; i++) { s += a * n3(p); p *= 2.03; a *= 0.5; } return s; }
void main(){
  vec2 w = vXZ;
  vec2 q = abs(w) - vec2(uHalfW, uHalfD);
  float dBox = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
  float edge = (fbm(vec3(w * 2.2, 1.0)) - 0.5) * 0.9 * uPool + (n3(vec3(w * 9.0, 4.0)) - 0.5) * 0.04;
  float pm = (uPool > 0.0) ? 1.0 - smoothstep(-0.008, 0.008, dBox - uPool * (0.75 + 0.5 * fbm(vec3(normalize(w + 1e-4) * 1.7, 2.0))) - edge) : 0.0;
  for (int i = 0; i < ${MAX_SPLATS}; i++) { vec4 s = uSplats[i]; if (s.z <= 0.0) continue;
    float d = length(w - s.xy) + (n3(vec3(w * 18.0, s.w)) - 0.5) * s.z * 0.5;
    pm = max(pm, 1.0 - smoothstep(s.z - 0.006, s.z + 0.006, d)); }
  float hW = uRomeW * uRomeA, zTop = uRomeC.y - hW * 0.3, st = 0.0;
  for (int k = 0; k < 4; k++) { float fk = float(k);
    float xc = uRomeC.x + uStreamX[k] + 0.022 * sin(w.y * 13.0 + fk * 2.1);
    float z0 = mix(uRomeC.y - 0.45, zTop - 0.01, uDrain);
    float z1 = mix(z0, zTop, clamp(uStream * 1.2 - fk * 0.06, 0.0, 1.0));
    float wd = 0.024 + 0.008 * sin(w.y * 29.0 + fk * 3.0) + 0.01 * smoothstep(z1 - 0.05, z1, w.y);
    st = max(st, (1.0 - smoothstep(wd * 0.55, wd, abs(w.x - xc))) * step(z0, w.y) * (1.0 - smoothstep(z1 - 0.006, z1, w.y))); }
  st *= uCarve * (1.0 - smoothstep(0.75, 0.98, uDrain));
  gl_FragColor = vec4(vec3(max(pm, st)), 1.0);
}`;

async function main() {
  const raw = new STLLoader().parse(await (await fetch(q.get("model") ?? "models/bearded-man-200k.stl")).arrayBuffer());
  const st = buildStatue(raw); log.push(`statue: ${st.pieces.length} pieces`);
  const topY = st.topY;

  // ---- geometry: outer surfaces in local coords with paint arrival times ----
  const outerMesh = (g: THREE.BufferGeometry, name: string) => {
    const gr = g.groups[0], idx = (g.index!.array as Uint32Array).slice(gr.start, gr.start + gr.count);
    const used = new Map<number, number>(); const remap: number[] = [];
    for (const v of idx) if (!used.has(v)) { used.set(v, remap.length); remap.push(v); }
    const pos = g.attributes.position, nor = g.attributes.normal, org = g.attributes.aOrig;
    const P = new Float32Array(remap.length * 3), Nn = new Float32Array(remap.length * 3), T0 = new Float32Array(remap.length), T1 = new Float32Array(remap.length);
    remap.forEach((v, i) => {
      P.set([pos.getX(v), pos.getY(v), pos.getZ(v)], i * 3); Nn.set([nor.getX(v), nor.getY(v), nor.getZ(v)], i * 3);
      const [a, b] = paintTimes(org.getX(v), org.getY(v), org.getZ(v), topY); T0[i] = a; T1[i] = b;
    });
    const out = new THREE.BufferGeometry();
    out.setAttribute("position", new THREE.BufferAttribute(P, 3)); out.setAttribute("normal", new THREE.BufferAttribute(Nn, 3));
    out.setAttribute("_paintt0", new THREE.BufferAttribute(T0, 1)); out.setAttribute("_paintt1", new THREE.BufferAttribute(T1, 1));
    out.setIndex(Array.from(idx, (v) => used.get(v)!));
    const m = new THREE.Mesh(out, new THREE.MeshStandardMaterial({ name: "statue" })); m.name = name; return m;
  };
  const group = new THREE.Group();
  group.add(outerMesh(st.stump, "stump"));
  st.pieces.forEach((p, i) => group.add(outerMesh(p.geo, `piece_${String(i).padStart(2, "0")}`)));
  const glb = await new GLTFExporter().parseAsync(group, { binary: true }) as ArrayBuffer;
  await save("pieces.glb", glb); log.push(`pieces.glb ${(glb.byteLength / 1e6).toFixed(1)} MB`);

  const chipG = new THREE.Group();
  for (let i = 0; i < C.particles.chips; i++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 0), new THREE.MeshStandardMaterial({ name: R(`cc${i}`) < 0.4 ? "chipBlood" : "chipMarble" })); m.name = `chip_${String(i).padStart(2, "0")}`; chipG.add(m); }
  await save("chips.glb", await new GLTFExporter().parseAsync(chipG, { binary: true }) as ArrayBuffer);

  // ---- per-frame values (the same formulas as Statue.tsx Scene) ----
  const shots = C.camera.shots, RM = C.rome, S3 = C.scene3;
  const big = st.pieces.map((p, i) => ({ p, i })).sort((a, b) => b.p.size - a.p.size).slice(0, MAX_SPLATS);
  const frames: unknown[] = [];
  // floor map renderer (top-down orthographic, SwiftShader handles this small shader fine)
  const H = Math.round(MAP.px * (MAP.z1 - MAP.z0) / (MAP.x1 - MAP.x0));
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true }); renderer.setSize(MAP.px, H); renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
  const fs = new THREE.Scene(), oc = new THREE.OrthographicCamera(MAP.x0, MAP.x1, -MAP.z0, -MAP.z1, -1, 1); // looking down -y after rotation below
  const fu: Record<string, { value: unknown }> = { uPool: { value: 0 }, uHalfW: { value: P.w / 2 }, uHalfD: { value: P.d / 2 }, uStream: { value: 0 }, uDrain: { value: 0 }, uCarve: { value: 0 }, uRomeW: { value: RM.width }, uRomeA: { value: 0.3125 }, uRomeC: { value: new THREE.Vector2(...RM.centre) }, uStreamX: { value: RM.streams }, uSplats: { value: Array.from({ length: MAX_SPLATS }, () => new THREE.Vector4()) } };
  // plane in the XY plane carrying world (x, z) in a varying; image row 0 = smallest z (top of the PNG = far side)
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(MAP.x1 - MAP.x0, MAP.z1 - MAP.z0), new THREE.ShaderMaterial({ uniforms: fu, fragmentShader: floorFrag,
    vertexShader: `varying vec2 vXZ; void main(){ vXZ = vec2(position.x + ${((MAP.x0 + MAP.x1) / 2).toFixed(4)}, -position.y + ${((MAP.z0 + MAP.z1) / 2).toFixed(4)}); gl_Position = vec4(position.x / ${((MAP.x1 - MAP.x0) / 2).toFixed(4)}, position.y / ${((MAP.z1 - MAP.z0) / 2).toFixed(4)}, 0.0, 1.0); }` }));
  fs.add(plane);
  const only = q.get("frames"); const [fA, fB] = only ? only.split("-").map(Number) : [1, N];

  for (let f = 1; f <= N; f++) {
    const t = (f - 1) / FPS, s = storyTime(t);
    // camera
    const shot = shots.find((sh) => t >= sh.t0 && t < sh.t1) ?? shots[shots.length - 1];
    const u = (t - shot.t0) / (shot.t1 - shot.t0), sk = easeInOut(u) * 0.85 + u * 0.15;
    const cp = new THREE.Vector3(...shot.pos0).lerp(new THREE.Vector3(...shot.pos1), sk), cl = new THREE.Vector3(...shot.look0).lerp(new THREE.Vector3(...shot.look1), sk);
    if (t > T.boom && t < T.boom + 0.5) { const k = (1 - (t - T.boom) / 0.5) * C.camera.boomShake; cp.x += Math.sin(t * 90) * k; cp.y += Math.cos(t * 77) * k; }
    let fade = 1; for (const sh of shots.slice(1)) { const dd = sh.dip ?? C.camera.dip, d = Math.abs(t - sh.t0); if (d < dd) fade = Math.min(fade, d / dd); }
    fade = Math.min(fade, clamp(t / 0.4), clamp((C.output.durationInSeconds - t) / 0.6));
    const fp = shot.focus ? new THREE.Vector3(...shot.focus) : t < T.boom + 1.5 ? (shot === shots[0] ? new THREE.Vector3(0.05, 0.6, 0.3) : st.headCentre) : new THREE.Vector3(0, 0.15, 0);
    // pieces
    const crackK = smooth(T.crackStart, T.boom, t), tremor = t > T.crackStart && t < T.boom ? F.tremor * crackK : 0;
    const states = st.pieces.map((p, i) => {
      const f2 = flight(`pc${i}`, p.centre, st.headCentre, Math.max(0.03, p.radius * 0.45), s);
      if (tremor > 0) f2.pos.add(new THREE.Vector3(Math.sin(t * 61 + i) * tremor, Math.sin(t * 53 + i * 2) * tremor * 0.5, Math.cos(t * 57 + i) * tremor));
      const sp = new THREE.Vector3(R(`w1${i}`) - 0.5, R(`w2${i}`) - 0.5, R(`w3${i}`) - 0.5).multiplyScalar(7);
      return { ...f2, rot: [sp.x * f2.tau, sp.y * f2.tau, sp.z * f2.tau] };
    });
    const dustK = clamp((t - S3.dust[0]) / (S3.dust[1] - S3.dust[0]));
    const sweptAt = (x: number, j: number) => clamp((x * 0.4 + 0.75 + (j - 0.5) * 0.35) / 1.5);
    const chips = Array.from({ length: C.particles.chips }, (_, i) => {
      const start = st.samples[i % st.samples.length], sz = 0.004 + R(`cs${i}`) * 0.012, f2 = flight(`ch${i}`, start, st.headCentre, sz, s, 1.15);
      return [+f2.pos.x.toFixed(5), +f2.pos.y.toFixed(5), +f2.pos.z.toFixed(5), +(f2.tau * 9 * R(`cr1${i}`)).toFixed(4), +(f2.tau * 9 * R(`cr2${i}`)).toFixed(4), s > T.boom && dustK <= sweptAt(f2.pos.x, R(`cj${i}`)) ? +sz.toFixed(5) : 0];
    });
    // floor values
    const pool = PA.poolMax * (1 - Math.exp(-Math.max(0, t - PA.floorReach) / (PA.poolGrow / 3)));
    const drainK = smooth(S3.drain[0], S3.drain[1], t);
    fu.uPool.value = pool * (1 - 0.95 * drainK); fu.uDrain.value = drainK; fu.uCarve.value = t >= RM.carveFrom ? 1 : 0; fu.uStream.value = smooth(RM.streamT[0], RM.streamT[1], t);
    const splats = fu.uSplats.value as THREE.Vector4[];
    big.forEach(({ p, i }, k) => { const stt = states[i]; if (!stt.landed) { splats[k].set(0, 0, 0, 0); return; }
      const r = (F.splatRadius[0] + (F.splatRadius[1] - F.splatRadius[0]) * R(`sp${i}`)) * Math.min(1, p.radius * 6);
      splats[k].set(stt.land.x, stt.land.z, r * easeOut((s - stt.landS) / 0.25) * (1 - drainK), i + 1); });
    frames.push({ f, t: +t.toFixed(4), cam: { pos: cp.toArray().map((v) => +v.toFixed(5)), look: cl.toArray().map((v) => +v.toFixed(5)), up: shot.topDown ? [0, 0, -1] : [0, 1, 0], fov: shot.fov, focus: +cp.distanceTo(fp).toFixed(4), fstop: shot.topDown ? 2.8 : t < T.boom ? 1.8 : 2.4 },
      fade: +fade.toFixed(4), carve: fu.uCarve.value, fill: +smooth(RM.fillT[0], RM.fillT[1], t).toFixed(4), dust: +dustK.toFixed(4), crack: +crackK.toFixed(4),
      pieces: states.map((x) => [+x.pos.x.toFixed(5), +x.pos.y.toFixed(5), +x.pos.z.toFixed(5), +x.rot[0].toFixed(4), +x.rot[1].toFixed(4), +x.rot[2].toFixed(4)]), chips });
    if (f >= fA && f <= fB) {
      renderer.render(fs, oc);
      const png = await new Promise<Blob>((res) => renderer.domElement.toBlob((b) => res(b!), "image/png"));
      await save(`floor/m_${String(f).padStart(4, "0")}.png`, png);
      if (f % 60 === 0) log.push(`floor map ${f}/${N}`);
    }
  }
  await save("anim.json", JSON.stringify({ fps: FPS, frames: N, map: { ...MAP, h: H }, rome: { centre: RM.centre, width: RM.width }, headCentre: st.headCentre.toArray(), frameData: frames }));

  // ROME mask (same drawing as Statue.tsx, at 2x)
  document.fonts.add(await new FontFace("CinzelLocal", "url(fonts/Cinzel.ttf)", { weight: "700" }).load());
  const Wm = 4096, Hm = 1280, c = document.createElement("canvas"); c.width = Wm; c.height = Hm; const g = c.getContext("2d")!;
  g.fillStyle = "#000"; g.fillRect(0, 0, Wm, Hm); g.font = `${RM.weight} 880px CinzelLocal`; g.textAlign = "center"; g.textBaseline = "middle";
  const mw = g.measureText(RM.text).width, k = Math.min(1, (Wm * 0.92) / mw);
  g.save(); g.translate(Wm / 2, Hm / 2 + 40); g.scale(k, 1); g.fillStyle = "#fff"; (g as any).letterSpacing = "60px"; g.fillText(RM.text, 0, 0); g.restore();
  await save("rome_mask.png", await new Promise<Blob>((res) => c.toBlob((b) => res(b!), "image/png")));
  log.push(`anim.json: ${N} frames`); (window as any).exported = true; (window as any).ready = true;
}
main().catch((e) => { log.push("ERROR " + (e?.stack ?? e)); (window as any).failed = String(e); });
