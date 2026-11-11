// Reduce a high-res binary STL scan to a lighter indexed mesh for real-time 3D in Remotion.
// Usage: node scripts/decimate-stl.mjs <in.stl> <out.stl> [targetTriangles=80000]
// Steps: read binary STL -> weld duplicate vertices -> meshoptimizer simplify -> centre, scale to
// height 1 with the base at y=0 -> write a binary STL (normals recomputed at load time).
import fs from "fs";
import { MeshoptSimplifier } from "meshoptimizer";

const [inPath, outPath, targetArg] = process.argv.slice(2);
const target = Number(targetArg ?? 80000);
const buf = fs.readFileSync(inPath);
const n = buf.readUInt32LE(80);
console.log(`input triangles: ${n}`);

// weld: quantise positions to merge shared corners
const map = new Map();
const verts = [];
const idx = new Uint32Array(n * 3);
for (let t = 0; t < n; t++) {
  const o = 84 + t * 50 + 12;
  for (let k = 0; k < 3; k++) {
    const x = buf.readFloatLE(o + k * 12), y = buf.readFloatLE(o + k * 12 + 4), z = buf.readFloatLE(o + k * 12 + 8);
    const key = `${Math.round(x * 1e4)},${Math.round(y * 1e4)},${Math.round(z * 1e4)}`;
    let id = map.get(key);
    if (id === undefined) { id = verts.length / 3; verts.push(x, y, z); map.set(key, id); }
    idx[t * 3 + k] = id;
  }
}
const pos = new Float32Array(verts);
console.log(`welded vertices: ${pos.length / 3}`);

await MeshoptSimplifier.ready;
const [simp, err] = MeshoptSimplifier.simplify(idx, pos, 3, target * 3, 0.05, ["LockBorder"]);
console.log(`simplified triangles: ${simp.length / 3} (error ${err.toFixed(5)})`);

// bounds -> orient: scans are often Z-up; pick the longest axis as up if it's Z
let min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
for (let i = 0; i < pos.length; i += 3) for (let a = 0; a < 3; a++) { min[a] = Math.min(min[a], pos[i + a]); max[a] = Math.max(max[a], pos[i + a]); }
const size = max.map((m, a) => m - min[a]);
console.log(`bounds size x/y/z: ${size.map((s) => s.toFixed(2)).join(" / ")}`);
const upAxis = process.env.UP ? "xyz".indexOf(process.env.UP) : size.indexOf(Math.max(...size));
const h = size[upAxis];
const c = [(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2];
const remap = (x, y, z) => {
  const p = [x - c[0], y - c[1], z - c[2]];
  let X = p[0], Y = p[1], Z = p[2];
  if (upAxis === 2) { Y = p[2]; Z = -p[1]; } // Z-up -> Y-up
  if (upAxis === 0) { Y = p[0]; X = -p[1]; }
  return [X / h, Y / h + 0.5, Z / h]; // height 1, base at y = 0
};

const tri = simp.length / 3;
const out = Buffer.alloc(84 + tri * 50);
out.write("decimated scan (see scripts/decimate-stl.mjs)", 0);
out.writeUInt32LE(tri, 80);
for (let t = 0; t < tri; t++) {
  const o = 84 + t * 50;
  for (let k = 0; k < 3; k++) {
    const v = simp[t * 3 + k] * 3;
    const [X, Y, Z] = remap(pos[v], pos[v + 1], pos[v + 2]);
    out.writeFloatLE(X, o + 12 + k * 12); out.writeFloatLE(Y, o + 16 + k * 12); out.writeFloatLE(Z, o + 20 + k * 12);
  }
}
fs.writeFileSync(outPath, out);
console.log(`wrote ${outPath} (${(out.length / 1e6).toFixed(1)} MB), up axis ${"xyz"[upAxis]}`);
