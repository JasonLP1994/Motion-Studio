// Pure, deterministic statue + fracture code shared by the Remotion video (Statue.tsx) and the
// path-traced stills (scripts/pathtrace). No React: everything is a function of the raw scan and time.
import * as THREE from "three";
import { random } from "remotion";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { statueConfig as C } from "./config";

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
export const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
export const smooth = (a: number, b: number, x: number) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
export const R = (k: string) => random(`${C.fracture.seed}-${k}`);
export const P = C.statue.plinth, F = C.fracture, PA = C.paint, T = C.t;

// Story time: real time until the boom, then slow motion, then ramps back to real speed.
export const storyTime = (t: number) => {
  if (t <= T.boom) return t;
  const s = C.slowMo;
  if (t <= T.slowEnd) return T.boom + (t - T.boom) * s;
  const base = T.boom + (T.slowEnd - T.boom) * s;
  const rd = T.rampEnd - T.slowEnd;
  if (t <= T.rampEnd) { const u = t - T.slowEnd; return base + s * u + ((1 - s) * u * u) / (2 * rd); }
  return base + s * rd + ((1 - s) * rd) / 2 + (t - T.rampEnd);
};

export type Piece = { geo: THREE.BufferGeometry; centre: THREE.Vector3; radius: number; size: number };

// Weld, orient and fracture the scan into a stump + pieces (inner shell + side walls on each piece).
export const buildStatue = (raw: THREE.BufferGeometry) => {
  const g0 = raw.clone(); g0.deleteAttribute("normal");
  const g = mergeVertices(g0, 1e-5); g.computeVertexNormals();
  g.center();
  g.applyMatrix4(new THREE.Matrix4().compose(new THREE.Vector3(), new THREE.Quaternion().setFromEuler(new THREE.Euler(C.statue.rotX, C.statue.rotY, C.statue.rotZ, "YXZ")), new THREE.Vector3().setScalar(C.statue.height)));
  g.computeBoundingBox(); const b0 = g.boundingBox!;
  g.translate(-(b0.min.x + b0.max.x) / 2, P.h - b0.min.y, -(b0.min.z + b0.max.z) / 2);
  g.computeBoundingBox(); const bb = g.boundingBox!;
  const pos = g.attributes.position as THREE.BufferAttribute, nor = g.attributes.normal as THREE.BufferAttribute, idx = g.index!;
  const triCount = idx.count / 3, V = pos.count;
  const cutY = bb.min.y + (bb.max.y - bb.min.y) * F.cutFraction;
  const cen = new Float32Array(triCount * 3);
  for (let t = 0; t < triCount; t++) for (let k = 0; k < 3; k++) { const v = idx.getX(t * 3 + k); cen[t * 3] += pos.getX(v) / 3; cen[t * 3 + 1] += pos.getY(v) / 3; cen[t * 3 + 2] += pos.getZ(v) / 3; }
  const upper: number[] = []; for (let t = 0; t < triCount; t++) if (cen[t * 3 + 1] >= cutY) upper.push(t);
  const seeds: THREE.Vector3[] = [];
  for (let i = 0; i < F.pieces; i++) { const t = upper[Math.floor(R(`s${i}`) * upper.length)]; seeds.push(new THREE.Vector3(cen[t * 3], cen[t * 3 + 1], cen[t * 3 + 2])); }
  const owner = new Int32Array(triCount);
  for (let t = 0; t < triCount; t++) {
    if (cen[t * 3 + 1] < cutY) { owner[t] = -1; continue; }
    let best = 0, bd = Infinity;
    for (let i = 0; i < seeds.length; i++) { const dx = cen[t * 3] - seeds[i].x, dy = (cen[t * 3 + 1] - seeds[i].y) * 0.8, dz = cen[t * 3 + 2] - seeds[i].z; const d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; best = i; } }
    owner[t] = best;
  }
  // crack distance: geodesic-ish distance from each vertex to the nearest piece border
  const vOwners: Set<number>[] = Array.from({ length: V }, () => new Set<number>());
  const adj: number[][] = Array.from({ length: V }, () => []);
  for (let t = 0; t < triCount; t++) { const a = idx.getX(t * 3), b = idx.getX(t * 3 + 1), c = idx.getX(t * 3 + 2); for (const v of [a, b, c]) vOwners[v].add(owner[t]); adj[a].push(b, c); adj[b].push(a, c); adj[c].push(a, b); }
  const crack = new Float32Array(V).fill(1);
  const queue: number[] = [];
  for (let v = 0; v < V; v++) if (vOwners[v].size > 1) { crack[v] = 0; queue.push(v); }
  for (let qi = 0; qi < queue.length; qi++) {
    const v = queue[qi];
    for (const w of adj[v]) {
      const d = crack[v] + Math.hypot(pos.getX(v) - pos.getX(w), pos.getY(v) - pos.getY(w), pos.getZ(v) - pos.getZ(w));
      if (d < crack[w] && d < 0.06) { crack[w] = d; queue.push(w); }
    }
  }
  const build = (sel: (t: number) => boolean, centre?: THREE.Vector3) => {
    const map = new Map<number, number>(); const p: number[] = [], n: number[] = [], o: number[] = [], cr: number[] = [], ix: number[] = [];
    for (let t = 0; t < triCount; t++) if (sel(t)) for (let k = 0; k < 3; k++) {
      const v = idx.getX(t * 3 + k); let id = map.get(v);
      if (id === undefined) { id = p.length / 3; map.set(v, id); const x = pos.getX(v), y = pos.getY(v), z = pos.getZ(v); o.push(x, y, z); cr.push(crack[v]); p.push(x - (centre?.x ?? 0), y - (centre?.y ?? 0), z - (centre?.z ?? 0)); n.push(nor.getX(v), nor.getY(v), nor.getZ(v)); }
      ix.push(id);
    }
    const th = F.thickness, Vn = p.length / 3, triN = ix.length / 3, outerCount = ix.length;
    const NO = [0, -10, 0];
    // inner shell: a shrunken copy towards the piece centre (never folds over itself like a normal offset does)
    const cg = new THREE.Vector3(); for (let v = 0; v < Vn; v++) cg.add(new THREE.Vector3(p[v * 3], p[v * 3 + 1], p[v * 3 + 2])); cg.divideScalar(Math.max(1, Vn));
    let rad = 0; for (let v = 0; v < Vn; v++) rad = Math.max(rad, Math.hypot(p[v * 3] - cg.x, p[v * 3 + 1] - cg.y, p[v * 3 + 2] - cg.z));
    const k = centre ? Math.max(0.35, 1 - (th * 2.2) / Math.max(rad, 1e-4)) : 1; // the stump keeps the normal offset (it is not a closed chunk)
    for (let v = 0; v < Vn; v++) {
      const x = p[v * 3], y = p[v * 3 + 1], z = p[v * 3 + 2];
      if (centre) p.push(cg.x + (x - cg.x) * k, cg.y + (y - cg.y) * k, cg.z + (z - cg.z) * k);
      else p.push(x - n[v * 3] * th, y - n[v * 3 + 1] * th, z - n[v * 3 + 2] * th);
      n.push(-n[v * 3], -n[v * 3 + 1], -n[v * 3 + 2]); o.push(...NO); cr.push(1);
    }
    for (let t = 0; t < triN; t++) ix.push(ix[t * 3] + Vn, ix[t * 3 + 2] + Vn, ix[t * 3 + 1] + Vn);
    const ec = new Map<string, number>();
    for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) { const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`; ec.set(key, (ec.get(key) ?? 0) + 1); }
    for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) {
      const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`;
      if (ec.get(key) !== 1) continue;
      const A = new THREE.Vector3(p[a * 3], p[a * 3 + 1], p[a * 3 + 2]), B = new THREE.Vector3(p[b * 3], p[b * 3 + 1], p[b * 3 + 2]);
      const Ai = new THREE.Vector3(p[(a + Vn) * 3], p[(a + Vn) * 3 + 1], p[(a + Vn) * 3 + 2]), Bi = new THREE.Vector3(p[(b + Vn) * 3], p[(b + Vn) * 3 + 1], p[(b + Vn) * 3 + 2]);
      // fracture face normal: outward from the piece centre, perpendicular to the surface (smooth, no stripes)
      const sn = new THREE.Vector3(n[a * 3] + n[b * 3], n[a * 3 + 1] + n[b * 3 + 1], n[a * 3 + 2] + n[b * 3 + 2]).normalize();
      const out = A.clone().add(B).multiplyScalar(0.5).sub(cg); out.addScaledVector(sn, -out.dot(sn));
      const flat = new THREE.Vector3().subVectors(Ai, A).cross(new THREE.Vector3().subVectors(B, A)).normalize();
      const wn = out.lengthSq() > 1e-10 ? out.normalize().lerp(flat, 0.25).normalize() : flat;
      const base = p.length / 3;
      for (const q of [A, B, Bi, Ai]) { p.push(q.x, q.y, q.z); n.push(wn.x, wn.y, wn.z); o.push(...NO); cr.push(0); }
      ix.push(base, base + 3, base + 1, base + 1, base + 3, base + 2);
    }
    const bg = new THREE.BufferGeometry();
    bg.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); bg.setAttribute("normal", new THREE.Float32BufferAttribute(n, 3));
    bg.setAttribute("aOrig", new THREE.Float32BufferAttribute(o, 3)); bg.setAttribute("aCrack", new THREE.Float32BufferAttribute(cr, 1)); bg.setIndex(ix);
    bg.addGroup(0, outerCount, 0); bg.addGroup(outerCount, ix.length - outerCount, 1);
    return bg;
  };
  const stump = build((t) => owner[t] === -1);
  const pieces: Piece[] = [];
  for (let i = 0; i < seeds.length; i++) {
    const tris: number[] = []; for (let t = 0; t < triCount; t++) if (owner[t] === i) tris.push(t);
    if (tris.length < 8) continue;
    const c = new THREE.Vector3(); for (const t of tris) c.add(new THREE.Vector3(cen[t * 3], cen[t * 3 + 1], cen[t * 3 + 2])); c.divideScalar(tris.length);
    const set = new Set(tris); const geo = build((t) => set.has(t), c); geo.computeBoundingSphere();
    pieces.push({ geo, centre: c, radius: geo.boundingSphere!.radius, size: tris.length });
  }
  // surface sample points for chips / dust
  const samples: THREE.Vector3[] = [];
  for (let i = 0; i < 700; i++) { const t = upper[Math.floor(R(`p${i}`) * upper.length)]; samples.push(new THREE.Vector3(cen[t * 3], cen[t * 3 + 1], cen[t * 3 + 2])); }
  const headCentre = new THREE.Vector3(0, (cutY + bb.max.y) / 2, 0);
  return { stump, pieces, samples, topY: bb.max.y, bb, headCentre };
};

// Ballistic flight from the boom (in story time): outward, upward kick, one bounce, rest on the floor.
export const flight = (key: string, start: THREE.Vector3, from: THREE.Vector3, restY: number, s: number, landScale = 1) => {
  const dt = s - T.boom;
  const pos = start.clone();
  if (dt <= 0) return { pos, landed: false, landS: 0, land: pos.clone(), tau: 0, T: 1 };
  const out = new THREE.Vector3(start.x - from.x, 0, start.z - from.z);
  if (out.lengthSq() < 1e-6) out.set(R(`${key}dx`) - 0.5, 0, R(`${key}dz`) - 0.5);
  out.normalize().applyAxisAngle(new THREE.Vector3(0, 1, 0), (R(`${key}a`) - 0.5) * 0.7);
  const g = F.gravity;
  const vy = F.explodeSpeed[0] + (F.explodeSpeed[1] - F.explodeSpeed[0]) * R(`${key}vy`);
  const drop = start.y - restY;
  const Tl = (vy + Math.sqrt(vy * vy + 2 * g * Math.max(0.01, drop))) / g;
  const R0 = Math.hypot(start.x, start.z);
  const Rl = (F.landMin + (F.landMax - F.landMin) * R(`${key}l`)) * landScale;
  const vh = Math.max(0.2, (Rl - R0) / Tl);
  const tau = Math.min(dt, Tl);
  pos.set(start.x + out.x * vh * tau, start.y + vy * tau - 0.5 * g * tau * tau, start.z + out.z * vh * tau);
  const land = new THREE.Vector3(start.x + out.x * vh * Tl, 0, start.z + out.z * vh * Tl);
  if (dt > Tl) {
    const b = dt - Tl, hb = F.bounce * Math.min(0.25, drop * 0.3), Tb = 2 * Math.sqrt((2 * hb) / g);
    pos.copy(land); pos.y = restY + (b < Tb ? 4 * hb * (b / Tb) * (1 - b / Tb) : 0);
    const slide = easeOut(Math.min(b, 0.6) / 0.6) * 0.1; pos.x += out.x * slide; pos.z += out.z * slide;
    return { pos, landed: true, landS: T.boom + Tl, land, tau: Tl + Math.min(b, 0.5) * 0.5, T: Tl };
  }
  return { pos, landed: false, landS: 0, land, tau, T: Tl };
};
