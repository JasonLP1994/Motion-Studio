// Painted statue that breaks apart (cinematic v2).
// A real marble scan: lights fade up through haze, thick glossy paint pours and drips, molten cracks
// spread, then a slow-motion explosion with chips, dust and splashes into a paint pool on a
// mirror-polished floor. GTAO + depth of field + bloom + film grade.
// Deterministic: everything is computed from frame / fps. The single useFrame below only takes over
// rendering (composer.render()) once per Remotion frame; it animates nothing.
import React, { useMemo } from "react";
import { AbsoluteFill, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useFrame, useLoader, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { Reflector } from "three/examples/jsm/objects/Reflector.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { BokehPass } from "three/examples/jsm/postprocessing/BokehPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { statueConfig as C } from "./config";

const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const smooth = (a: number, b: number, x: number) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const R = (k: string) => random(`${C.fracture.seed}-${k}`);
const P = C.statue.plinth, F = C.fracture, PA = C.paint, T = C.t;

// Story time: real time until the boom, then slow motion, then ramps back to real speed.
const storyTime = (t: number) => {
  if (t <= T.boom) return t;
  const s = C.slowMo;
  if (t <= T.slowEnd) return T.boom + (t - T.boom) * s;
  const base = T.boom + (T.slowEnd - T.boom) * s;
  const rd = T.rampEnd - T.slowEnd;
  if (t <= T.rampEnd) { const u = t - T.slowEnd; return base + s * u + ((1 - s) * u * u) / (2 * rd); }
  return base + s * rd + ((1 - s) * rd) / 2 + (t - T.rampEnd);
};

// ---------- GLSL ----------
const NOISE = /* glsl */ `
float h1(float n){ return fract(sin(n) * 43758.5453); }
float n1(float x){ float i = floor(x), f = fract(x); return mix(h1(i), h1(i + 1.0), f * f * (3.0 - 2.0 * f)); }
float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float n3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h3(i), h3(i+vec3(1,0,0)), f.x), mix(h3(i+vec3(0,1,0)), h3(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i+vec3(0,0,1)), h3(i+vec3(1,0,1)), f.x), mix(h3(i+vec3(0,1,1)), h3(i+vec3(1,1,1)), f.x), f.y), f.z); }
float fbm(vec3 p){ float a = 0.5, s = 0.0; for (int i = 0; i < 4; i++) { s += a * n3(p); p *= 2.03; a *= 0.5; } return s; }
float paintMask(vec3 p, float topY, float flow, float cap, float streaks){
  if (flow <= 0.0 || p.y < -5.0) return 0.0;
  float ang = atan(p.z, p.x);
  float lobe = n1(ang * streaks + 3.1) * 0.6 + n1(ang * streaks * 2.3 + 9.0) * 0.4;      // soft lobes on the sheet's edge
  float longDrip = pow(n1(ang * streaks * 0.7 + 17.0), 6.0);                                // a few long drips
  float front = topY - min(flow, cap) - max(flow - cap, 0.0) * (0.78 + 0.32 * lobe + 1.4 * longDrip);
  float wobble = (n3(p * 9.0) - 0.5) * 0.025;
  return smoothstep(front - 0.006, front + 0.006, p.y + wobble);
}
`;

type Uniforms = Record<string, { value: unknown }>;

// Marble + thick paint (raised in the vertex shader) + glowing cracks (emissive).
const makeMarble = (colour: string, veins: boolean, u: Uniforms) => {
  const m = new THREE.MeshPhysicalMaterial({ color: colour, roughness: 0.33, clearcoat: 0.3, clearcoatRoughness: 0.45, side: THREE.DoubleSide });
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u);
    const decl = `\nuniform float uFlow, uTopY, uCap, uStreaks, uThick, uCrackW, uCrackFront, uCrackI;\nuniform vec3 uPaint, uVein, uCrack;\n${NOISE}`;
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", `#include <common>\nattribute vec3 aOrig;\nattribute float aCrack;\nvarying vec3 vOrig;\nvarying float vCrack;${decl}`)
      .replace("#include <begin_vertex>", `#include <begin_vertex>\nvOrig = aOrig; vCrack = aCrack;\ntransformed += objectNormal * paintMask(aOrig, uTopY, uFlow, uCap, uStreaks) * uThick;`);
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vOrig;\nvarying float vCrack;${decl}`)
      .replace("#include <color_fragment>", `#include <color_fragment>
        ${veins ? "float v = abs(sin(vOrig.x * 9.0 + fbm(vOrig * 6.0) * 6.0)); diffuseColor.rgb = mix(diffuseColor.rgb, uVein, (1.0 - smoothstep(0.0, 0.18, v)) * 0.35);" : ""}
        float pm = paintMask(vOrig, uTopY, uFlow, uCap, uStreaks);
        diffuseColor.rgb = mix(diffuseColor.rgb, uPaint, pm);
        float cg = (1.0 - smoothstep(0.0, max(uCrackW, 1e-4), vCrack)) * step(uCrackFront, vOrig.y) * step(0.0, uCrackW);
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.05), cg * 0.85);`)
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.24, pm);")
      .replace("#include <emissivemap_fragment>", "#include <emissivemap_fragment>\ntotalEmissiveRadiance += uCrack * cg * uCrackI;");
  };
  m.customProgramCacheKey = () => `marble2-${veins}`;
  return m;
};

// Floor overlay above a mirror: dark polished stone (lets reflections through) + paint pool + splats.
const MAX_SPLATS = 24;
const makeFloor = (u: Uniforms) => {
  const m = new THREE.MeshStandardMaterial({ color: C.colors.floor, roughness: 0.9, transparent: true, depthWrite: true }); // matte top: lights never show as hotspots
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u);
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vW;")
      .replace("#include <worldpos_vertex>", "#include <worldpos_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vW;\nuniform float uPool, uHalfW, uHalfD, uFloorA, uFadeA, uFadeB;\nuniform vec3 uPaint, uFogC;\nuniform vec4 uSplats[${MAX_SPLATS}];\n${NOISE}`)
      .replace("#include <color_fragment>", `#include <color_fragment>
        vec2 q = abs(vW.xz) - vec2(uHalfW, uHalfD);
        float dBox = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
        float edge = (fbm(vec3(vW.xz * 2.2, 1.0)) - 0.5) * 0.9 * uPool + (n3(vec3(vW.xz * 9.0, 4.0)) - 0.5) * 0.04;
        float pm = (uPool > 0.0) ? 1.0 - smoothstep(-0.008, 0.008, dBox - uPool * (0.75 + 0.5 * fbm(vec3(normalize(vW.xz + 1e-4) * 1.7, 2.0))) - edge) : 0.0;
        for (int i = 0; i < ${MAX_SPLATS}; i++) { vec4 s = uSplats[i]; if (s.z <= 0.0) continue;
          float d = length(vW.xz - s.xy) + (n3(vec3(vW.xz * 18.0, s.w)) - 0.5) * s.z * 0.5;
          pm = max(pm, 1.0 - smoothstep(s.z - 0.006, s.z + 0.006, d)); }
        diffuseColor.rgb = mix(diffuseColor.rgb, uPaint, pm);
        diffuseColor.a = mix(uFloorA, 1.0, pm);`)
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.04, pm);")
      // infinite floor: with distance the floor turns into exactly the cove's horizon colour (opaque, unlit)
      .replace("#include <fog_fragment>", "#include <fog_fragment>\nfloat far0 = smoothstep(uFadeA, uFadeB, length(vW.xz));\ngl_FragColor = vec4(mix(gl_FragColor.rgb, uFogC, far0), mix(gl_FragColor.a, 1.0, far0));");
  };
  m.customProgramCacheKey = () => "paint-floor3";
  return m;
};

// Final grade: split-tone, vignette, film grain, a touch of chromatic aberration.
const GradeShader = {
  uniforms: { tDiffuse: { value: null }, uSeed: { value: 0 }, uGrain: { value: C.post.grain }, uVig: { value: C.post.vignette }, uFade: { value: 1 }, uDesat: { value: C.desaturate }, uTint: { value: C.redTint }, uGlow: { value: C.post.topGlow }, uSh: { value: new THREE.Color(C.colors.background) }, uMid: { value: new THREE.Color(C.colors.haze) }, uHi: { value: new THREE.Color(C.colors.hazeHot) } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse; uniform float uSeed, uGrain, uVig, uFade, uDesat, uTint, uGlow; uniform vec3 uSh, uMid, uHi; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + uSeed) * 43758.5453); }
    void main(){
      vec2 d = vUv - 0.5; float r2 = dot(d, d);
      vec3 c = vec3(texture2D(tDiffuse, vUv + d * 0.004 * r2).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - d * 0.004 * r2).b);
      float l = dot(c, vec3(0.299, 0.587, 0.114));
      float red = smoothstep(0.04, 0.22, c.r - max(c.g, c.b)); // keep reds, drain everything else
      c = mix(mix(c, vec3(l), uDesat), c, red);
      float L = pow(clamp(l, 0.0, 1.0), 0.72);
      vec3 ramp = L < 0.45 ? mix(uSh, uMid, L / 0.45) : mix(uMid, uHi, (L - 0.45) / 0.55); // maroon -> red -> pink
      c = mix(c, ramp * (0.6 + 0.4 * (1.0 + red)), uTint);
      vec2 gd = (vUv - vec2(0.5, 1.08)) * vec2(1.6, 1.0);                 // top light blooming through the haze
      float glow = exp(-dot(gd, gd) * 3.2);
      c += uGlow * (uMid * glow * 0.9 + uHi * pow(glow, 3.0) * 0.45);
      c *= 1.0 - uVig * smoothstep(0.12, 0.7, r2 * 1.6);
      c += (hash(vUv * 1000.0) - 0.5) * uGrain;
      c *= uFade;
      gl_FragColor = vec4(c, 1.0);
    }`,
};

// Soft round sprite for dust (generated, no files).
const makeSprite = () => {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d")!; const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, "rgba(255,255,255,1)"); grd.addColorStop(0.4, "rgba(255,255,255,0.35)"); grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; return tex;
};

// ---------- geometry ----------
type Piece = { geo: THREE.BufferGeometry; centre: THREE.Vector3; radius: number; size: number };

const useStatue = () => {
  const raw = useLoader(STLLoader, staticFile(C.model));
  return useMemo(() => {
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
      for (let v = 0; v < Vn; v++) { p.push(p[v * 3] - n[v * 3] * th, p[v * 3 + 1] - n[v * 3 + 1] * th, p[v * 3 + 2] - n[v * 3 + 2] * th); n.push(-n[v * 3], -n[v * 3 + 1], -n[v * 3 + 2]); o.push(...NO); cr.push(1); }
      for (let t = 0; t < triN; t++) ix.push(ix[t * 3] + Vn, ix[t * 3 + 2] + Vn, ix[t * 3 + 1] + Vn);
      const ec = new Map<string, number>();
      for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) { const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`; ec.set(key, (ec.get(key) ?? 0) + 1); }
      for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) {
        const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`;
        if (ec.get(key) !== 1) continue;
        const A = new THREE.Vector3(p[a * 3], p[a * 3 + 1], p[a * 3 + 2]), B = new THREE.Vector3(p[b * 3], p[b * 3 + 1], p[b * 3 + 2]);
        const Ai = new THREE.Vector3(p[(a + Vn) * 3], p[(a + Vn) * 3 + 1], p[(a + Vn) * 3 + 2]), Bi = new THREE.Vector3(p[(b + Vn) * 3], p[(b + Vn) * 3 + 1], p[(b + Vn) * 3 + 2]);
        const wn = new THREE.Vector3().subVectors(Ai, A).cross(new THREE.Vector3().subVectors(B, A)).normalize();
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
  }, [raw]);
};

// Ballistic flight from the boom (in story time): outward, upward kick, one bounce, rest on the floor.
const flight = (key: string, start: THREE.Vector3, from: THREE.Vector3, restY: number, s: number, landScale = 1) => {
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

// ---------- post ----------
const Post: React.FC<{ focus: number; bloom: number; seed: number; fade: number }> = ({ focus, bloom, seed, fade }) => {
  const { gl, scene, camera, size } = useThree();
  const passes = useMemo(() => {
    const c = new EffectComposer(gl); c.setPixelRatio(1); c.setSize(size.width, size.height);
    c.addPass(new RenderPass(scene, camera));
    const ao = new GTAOPass(scene, camera, size.width, size.height);
    ao.updateGtaoMaterial({ radius: C.post.ao.radius, distanceExponent: 1, thickness: C.post.ao.thickness, scale: 1, samples: 16, distanceFallOff: 1 });
    ao.blendIntensity = C.post.ao.blend; c.addPass(ao);
    const bokeh = new BokehPass(scene, camera, { focus: 2.5, aperture: C.post.dof.aperture, maxblur: C.post.dof.maxblur }); c.addPass(bokeh);
    const bl = new UnrealBloomPass(new THREE.Vector2(size.width, size.height), C.post.bloom.strength, C.post.bloom.radius, C.post.bloom.threshold); c.addPass(bl);
    c.addPass(new OutputPass());
    const grade = new ShaderPass(GradeShader); c.addPass(grade);
    return { c, bokeh, bl, grade };
  }, [gl, scene, camera, size.width, size.height]);
  (passes.bokeh.uniforms as Record<string, { value: number }>).focus.value = focus;
  passes.bl.strength = bloom;
  passes.grade.uniforms.uSeed.value = seed;
  passes.grade.uniforms.uFade.value = fade;
  useFrame(() => passes.c.render(), 1);
  return null;
};

const Env: React.FC = () => {
  const { gl, scene } = useThree();
  useMemo(() => {
    // Reflection world that matches the cove: dark maroon all round, one big soft pink glow overhead
    // (no rectangular studio panels, which showed up as white squares on the wet paint).
    const s = new THREE.Scene();
    s.add(new THREE.Mesh(new THREE.SphereGeometry(10, 64, 32), new THREE.ShaderMaterial({
      side: THREE.BackSide,
      uniforms: { uBg: { value: new THREE.Color(C.colors.background) }, uHaze: { value: new THREE.Color(C.colors.haze) }, uHot: { value: new THREE.Color(C.colors.hazeHot) } },
      vertexShader: "varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
      fragmentShader: "uniform vec3 uBg, uHaze, uHot; varying vec3 vD; void main(){ vec3 d = normalize(vD); float top = smoothstep(0.2, 1.0, d.y); gl_FragColor = vec4(uBg + uHaze * top * 1.5 + uHot * pow(top, 4.0) * 2.5, 1.0); }",
    })));
    const pm = new THREE.PMREMGenerator(gl); scene.environment = pm.fromScene(s, 0.02).texture; scene.environmentIntensity = C.light.env * 4;
  }, [gl, scene]);
  return null;
};

// Infinite cove: a huge inside-out sphere. Its horizon colour equals the fog colour, so the floor
// and the backdrop meet with no visible line; a soft red haze glows behind the top light.
const Cove: React.FC<{ on: number }> = ({ on }) => {
  const mat = useMemo(() => new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uOn: { value: 0 }, uBg: { value: new THREE.Color(C.colors.background) }, uFog: { value: new THREE.Color(C.colors.fog) },
      uHaze: { value: new THREE.Color(C.colors.haze) }, uHot: { value: new THREE.Color(C.colors.hazeHot) },
      uDir: { value: new THREE.Vector3(...C.cove.hazeDir).normalize() }, uSize: { value: C.cove.hazeSize } },
    vertexShader: "varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
    fragmentShader: `uniform float uOn, uSize; uniform vec3 uBg, uFog, uHaze, uHot, uDir; varying vec3 vD;
      void main(){
        vec3 d = normalize(vD);
        vec3 c = uFog;                                                 // one flat colour = the floor's far colour (infinite background)
        float g = max(dot(d, uDir), 0.0);
        float halo = exp(-(1.0 - g) / (uSize * 0.5));
        float above = smoothstep(0.02, 0.45, d.y);                     // no haze at the horizon: floor and backdrop meet invisibly
        c += (uHaze * halo * 0.0) * above * uOn; // no visible glow: lights are seen only on the statue
        gl_FragColor = vec4(c, 1.0);
      }`,
  }), []);
  mat.uniforms.uOn.value = on;
  return <mesh material={mat} renderOrder={-10}><sphereGeometry args={[C.cove.radius, 64, 32]} /></mesh>;
};


const Scene: React.FC<{ t: number; frame: number }> = ({ t, frame }) => {
  const { stump, pieces, samples, topY, headCentre } = useStatue();
  const { camera } = useThree();
  const s = storyTime(t);
  const L = C.light;

  const u = useMemo<Uniforms>(() => ({
    uFlow: { value: 0 }, uTopY: { value: topY }, uCap: { value: PA.capDepth }, uStreaks: { value: PA.streaks }, uThick: { value: PA.thickness },
    uPaint: { value: new THREE.Color(C.colors.paint) }, uVein: { value: new THREE.Color(C.colors.vein) }, uCrack: { value: new THREE.Color(C.colors.crack) },
    uCrackW: { value: -1 }, uCrackFront: { value: 99 }, uCrackI: { value: 0 },
  }), [topY]);
  const floorU = useMemo<Uniforms>(() => ({ uPool: { value: 0 }, uHalfW: { value: P.w / 2 }, uHalfD: { value: P.d / 2 }, uFloorA: { value: C.post.reflector.floorOpacity }, uFadeA: { value: C.cove.floorFadeStart }, uFadeB: { value: C.cove.floorFadeEnd }, uFogC: { value: new THREE.Color(C.colors.fog) }, uPaint: { value: new THREE.Color(C.colors.paint) }, uSplats: { value: Array.from({ length: MAX_SPLATS }, () => new THREE.Vector4()) } }), []);
  const marble = useMemo(() => makeMarble(C.colors.marble, true, u), [u]);
  const inner = useMemo(() => { const m = makeMarble(C.colors.marble, true, u); m.polygonOffset = true; m.polygonOffsetFactor = 2; m.polygonOffsetUnits = 2; return m; }, [u]);
  const mats = useMemo(() => [marble, inner], [marble, inner]);
  const plinthMat = useMemo(() => makeMarble(C.colors.plinth, false, u), [u]);
  const floorMat = useMemo(() => makeFloor(floorU), [floorU]);
  const plinthGeo = useMemo(() => {
    const g = new RoundedBoxGeometry(P.w, Math.max(P.h, 0.01), P.d, 3, P.bevel); g.translate(0, P.h / 2, 0);
    g.setAttribute("aOrig", g.attributes.position.clone());
    g.setAttribute("aCrack", new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count).fill(1), 1));
    return g;
  }, []);
  const mirror = useMemo(() => {
    const r = new Reflector(new THREE.PlaneGeometry(40, 40), { textureWidth: C.post.reflector.size, textureHeight: Math.round(C.post.reflector.size * 0.5625), color: new THREE.Color(C.post.reflector.tint) });
    r.rotation.x = -Math.PI / 2; r.position.y = -0.001; return r;
  }, []);
  const sprite = useMemo(() => makeSprite(), []);

  // --- paint ---
  u.uFlow.value = PA.speed * Math.pow(Math.max(0, t - T.paintStart), PA.slowdown);
  const pool = PA.poolMax * (1 - Math.exp(-Math.max(0, t - PA.floorReach) / (PA.poolGrow / 3)));
  floorU.uPool.value = pool;

  // --- cracks: spread down from the crown, glow, flash at the boom, fade as pieces fly ---
  const crackK = smooth(T.crackStart, T.boom, t);
  u.uCrackW.value = t < T.crackStart ? -1 : F.crackWidth * (0.3 + 0.7 * crackK);
  u.uCrackFront.value = topY + 0.02 - crackK * 1.2;
  u.uCrackI.value = (t < T.crackStart ? 0 : C.crackGlow * (0.3 + 0.7 * crackK)) * (t > T.boom ? Math.exp(-(t - T.boom) * 1.2) : 1);
  inner.visible = t >= T.crackStart;

  // --- pieces ---
  const tremor = t > T.crackStart && t < T.boom ? F.tremor * crackK : 0;
  const pieceStates = pieces.map((p, i) => {
    const restY = Math.max(0.03, p.radius * 0.45);
    const f = flight(`pc${i}`, p.centre, headCentre, restY, s);
    if (tremor > 0) f.pos.add(new THREE.Vector3(Math.sin(t * 61 + i) * tremor, Math.sin(t * 53 + i * 2) * tremor * 0.5, Math.cos(t * 57 + i) * tremor));
    const sp = new THREE.Vector3(R(`w1${i}`) - 0.5, R(`w2${i}`) - 0.5, R(`w3${i}`) - 0.5).multiplyScalar(7);
    const rot = new THREE.Euler(sp.x * f.tau, sp.y * f.tau, sp.z * f.tau);
    return { ...f, rot };
  });
  const splats = floorU.uSplats.value as THREE.Vector4[];
  const big = pieces.map((p, i) => ({ p, i })).sort((a, b) => b.p.size - a.p.size).slice(0, MAX_SPLATS);
  big.forEach(({ p, i }, k) => {
    const st = pieceStates[i];
    if (!st.landed) { splats[k].set(0, 0, 0, 0); return; }
    const r = (F.splatRadius[0] + (F.splatRadius[1] - F.splatRadius[0]) * R(`sp${i}`)) * Math.min(1, p.radius * 6);
    splats[k].set(st.land.x, st.land.z, r * easeOut((s - st.landS) / 0.25), i + 1);
  });

  // --- chips (instanced) ---
  const chips = useMemo(() => {
    const m = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), new THREE.MeshStandardMaterial({ roughness: 0.4 }), C.particles.chips);
    m.castShadow = true;
    for (let i = 0; i < C.particles.chips; i++) m.setColorAt(i, new THREE.Color(R(`cc${i}`) < 0.4 ? C.colors.paint : C.colors.marble));
    return m;
  }, []);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  for (let i = 0; i < C.particles.chips; i++) {
    const start = samples[i % samples.length];
    const sz = 0.004 + R(`cs${i}`) * 0.012;
    const f = flight(`ch${i}`, start, headCentre, sz, s, 1.15);
    dummy.position.copy(f.pos);
    dummy.rotation.set(f.tau * 9 * R(`cr1${i}`), f.tau * 9 * R(`cr2${i}`), 0);
    dummy.scale.setScalar(s > T.boom ? sz : 0);
    dummy.updateMatrix(); chips.setMatrixAt(i, dummy.matrix);
  }
  chips.instanceMatrix.needsUpdate = true;

  // --- splash droplets where the biggest pieces land in the paint ---
  const splashN = C.particles.splashPieces * C.particles.splashPerPiece;
  const splash = useMemo(() => new THREE.InstancedMesh(new THREE.SphereGeometry(1, 10, 8), new THREE.MeshPhysicalMaterial({ color: C.colors.paint, roughness: 0.05, clearcoat: 1 }), splashN), [splashN]);
  big.slice(0, C.particles.splashPieces).forEach(({ i }, k) => {
    const st = pieceStates[i];
    for (let j = 0; j < C.particles.splashPerPiece; j++) {
      const id = k * C.particles.splashPerPiece + j, a = (j / C.particles.splashPerPiece) * Math.PI * 2 + R(`sa${id}`);
      const dt = st.landed ? s - st.landS : -1;
      if (dt < 0 || dt > 0.6) { dummy.scale.setScalar(0); }
      else {
        const v = 0.35 + R(`sv${id}`) * 0.5, up = 0.8 + R(`su${id}`) * 1.0;
        dummy.position.set(st.land.x + Math.cos(a) * v * dt, Math.max(0, up * dt - 0.5 * 6 * dt * dt), st.land.z + Math.sin(a) * v * dt);
        dummy.scale.setScalar(0.007 * (1 - dt / 0.6) + 0.002);
      }
      dummy.rotation.set(0, 0, 0); dummy.updateMatrix(); splash.setMatrixAt(id, dummy.matrix);
    }
  });
  splash.instanceMatrix.needsUpdate = true;

  // --- falling paint drops: from the jaw onto the plinth, then off the plinth edge to the floor ---
  const drops = useMemo(() => new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 10), new THREE.MeshPhysicalMaterial({ color: C.colors.paint, roughness: 0.04, clearcoat: 1 }), PA.drops), []);
  for (let i = 0; i < PA.drops; i++) {
    const fromJaw = !P.show || i < PA.drops / 2;
    const ts = fromJaw ? 1.6 + i * 0.2 + R(`dt${i}`) * 0.1 : PA.floorReach - 0.3 + (i - PA.drops / 2) * 0.35 + R(`dt${i}`) * 0.15;
    const a = R(`da${i}`) * Math.PI * 2;
    const x0 = fromJaw ? Math.cos(a) * 0.16 : (R(`dx${i}`) - 0.5) * P.w, z0 = fromJaw ? 0.12 + Math.sin(a) * 0.06 : P.d / 2 + 0.004;
    const y0 = fromJaw ? P.h + 0.12 : P.h - 0.05, yEnd = fromJaw ? P.h : 0.0;
    const dt = t - ts, y = y0 - 0.5 * 9 * dt * dt;
    if (dt < 0 || y < yEnd || t > T.boom + 0.3) dummy.scale.setScalar(0);
    else { const v = 9 * dt; dummy.position.set(x0, y, z0); dummy.scale.set(0.009, 0.009 + v * 0.006, 0.009); }
    dummy.rotation.set(0, 0, 0); dummy.updateMatrix(); drops.setMatrixAt(i, dummy.matrix);
  }
  drops.instanceMatrix.needsUpdate = true;

  // --- dust: a burst from the statue at the boom + motes floating in the light beam ---
  const dust = useMemo(() => {
    const n = C.particles.dust + C.particles.motes;
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(new Float32Array(n * 4), 4));
    const m = new THREE.PointsMaterial({ size: 0.05, map: sprite, transparent: true, depthWrite: false, vertexColors: true, blending: THREE.AdditiveBlending, sizeAttenuation: true });
    return new THREE.Points(g, m);
  }, [sprite]);
  const dpos = dust.geometry.attributes.position as THREE.BufferAttribute, dcol = dust.geometry.attributes.color as THREE.BufferAttribute;
  for (let i = 0; i < C.particles.dust; i++) {
    const st = samples[(i * 7) % samples.length];
    const dt = s - T.boom;
    const dir = new THREE.Vector3(st.x - headCentre.x, st.y - headCentre.y, st.z - headCentre.z).normalize();
    const sp = 0.3 + R(`ds${i}`) * 0.9, k = 1 - Math.exp(-Math.max(0, dt) * 1.5);
    dpos.setXYZ(i, st.x + dir.x * sp * k, st.y + dir.y * sp * k * 0.6 - 0.05 * Math.max(0, dt), st.z + dir.z * sp * k);
    const a = dt < 0 ? 0 : 0.35 * Math.exp(-dt * 0.9) * (0.5 + R(`da2${i}`));
    dcol.setXYZW(i, 0.6, 0.57, 0.54, a * 0.5);
  }
  const keyOn = smooth(T.lightsOn[0], T.lightsOn[1], t);
  for (let j = 0; j < C.particles.motes; j++) {
    const i = C.particles.dust + j;
    const x = -1.6 + R(`mx${j}`) * 3.2, y = 0.1 + R(`my${j}`) * 1.6, z = -1.8 + R(`mz${j}`) * 2.4; // stay around/behind the statue, never at the lens
    dpos.setXYZ(i, x + Math.sin(t * 0.3 + j) * 0.05, y + ((t * 0.04 + R(`mv${j}`)) % 1) * 0.15, z + Math.cos(t * 0.25 + j) * 0.05);
    dcol.setXYZW(i, 1, 0.75, 0.75, 0.035 * keyOn * (0.4 + R(`ma${j}`)));
  }
  dpos.needsUpdate = true; dcol.needsUpdate = true;

  // --- camera: three shots, each a slow eased drift, plus tremor/shake; dips to black at the cuts ---
  const shots = C.camera.shots;
  const shot = shots.find((sh) => t >= sh.t0 && t < sh.t1) ?? shots[shots.length - 1];
  const sk = easeInOut((t - shot.t0) / (shot.t1 - shot.t0)) * 0.85 + ((t - shot.t0) / (shot.t1 - shot.t0)) * 0.15;
  const cp = new THREE.Vector3(...shot.pos0).lerp(new THREE.Vector3(...shot.pos1), sk);
  const cl = new THREE.Vector3(...shot.look0).lerp(new THREE.Vector3(...shot.look1), sk);
  const bt = t - T.boom;
  const shake = (bt > 0 ? C.camera.boomShake * Math.exp(-bt * 3) : 0) + tremor * 0.8;
  cp.add(new THREE.Vector3(Math.sin(t * 23) * shake, Math.sin(t * 29 + 1) * shake, Math.sin(t * 19 + 2) * shake * 0.5));
  camera.position.copy(cp);
  (camera as THREE.PerspectiveCamera).fov = shot.fov; (camera as THREE.PerspectiveCamera).updateProjectionMatrix();
  camera.lookAt(cl);
  const dip = C.camera.dip;
  let fade = smooth(0, 0.6, t); // first frames rise from black
  for (const sh of shots.slice(1)) { const d = Math.abs(t - sh.t0); if (d < dip) fade = Math.min(fade, d / dip); }
  fade = Math.min(fade, 1 - smooth(C.output.durationInSeconds - 0.5, C.output.durationInSeconds, t));
  const focus = cp.distanceTo(t < T.boom + 1.5 ? (shot === shots[0] ? new THREE.Vector3(0.05, 0.6, 0.3) : headCentre) : new THREE.Vector3(0, 0.15, 0));
  const bloom = C.post.bloom.strength + (bt > 0 ? C.post.bloom.boomFlash * Math.exp(-bt * 6) : 0);

  return (
    <>
      <Env />
      <color attach="background" args={[C.colors.background]} />
      <fogExp2 attach="fog" args={[C.colors.fog, C.cove.fogDensity]} />
      <Cove on={keyOn} />
      {/* omni lights (C4D-style): placed out of shot, only their light is seen */}
      <pointLight position={L.key.position} intensity={L.key.intensity * keyOn} color={C.colors.key} decay={2} castShadow
        shadow-mapSize-width={1024} shadow-mapSize-height={1024} shadow-bias={-0.0004} shadow-normalBias={0.02} />
      <pointLight position={L.fill.position} intensity={L.fill.intensity * keyOn} color={C.colors.key} decay={2} />
      <pointLight position={L.rimA.position} intensity={L.rimA.intensity * keyOn} color={C.colors.rimA} decay={2} />
      <pointLight position={L.rimB.position} intensity={L.rimB.intensity * keyOn} color={C.colors.rimB} decay={2} />
      <pointLight position={[0.2, 0.7, 1.4]} intensity={L.bounce * clamp(pool / PA.poolMax)} color={C.colors.paint} decay={2} distance={4} />

      <primitive object={mirror} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow material={floorMat}><planeGeometry args={[40, 40]} /></mesh>
      {P.show ? <mesh geometry={plinthGeo} material={plinthMat} castShadow receiveShadow /> : null}
      <mesh geometry={stump} material={mats} castShadow receiveShadow />
      {pieces.map((p, i) => <mesh key={i} geometry={p.geo} material={mats} position={pieceStates[i].pos} rotation={pieceStates[i].rot} castShadow receiveShadow />)}
      <primitive object={chips} />
      <primitive object={splash} />
      <primitive object={drops} />
      <primitive object={dust} />
      <Post focus={focus} bloom={bloom} seed={frame * 0.137} fade={fade} />
    </>
  );
};

export const PaintedStatue: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: C.colors.background }}>
      <ThreeCanvas width={width} height={height} shadows="soft"
        gl={{ antialias: true, preserveDrawingBuffer: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: C.light.exposure }}
        camera={{ fov: C.camera.shots[0].fov, near: 0.05, far: 60, position: C.camera.shots[0].pos0 }}>
        <Scene t={frame / fps} frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
