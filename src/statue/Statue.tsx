// Painted statue that breaks apart. A real marble scan on a plinth: glossy paint runs down it and
// pools on the floor, cracks open and pieces fall into the paint. GTAO ambient occlusion, soft
// shadows, image-based light and a paint-coloured floor bounce (GI look).
// Deterministic: everything is computed from frame / fps. The one useFrame below only takes over
// rendering (composer.render()) once per Remotion frame; it animates nothing.
import React, { useMemo } from "react";
import { AbsoluteFill, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useFrame, useLoader, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { statueConfig as C } from "./config";

const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const P = C.statue.plinth, F = C.fracture, PA = C.paint;

// ---------- shared GLSL ----------
const NOISE = /* glsl */ `
float h1(float n){ return fract(sin(n) * 43758.5453); }
float n1(float x){ float i = floor(x), f = fract(x); return mix(h1(i), h1(i + 1.0), f * f * (3.0 - 2.0 * f)); }
float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float n3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h3(i), h3(i+vec3(1,0,0)), f.x), mix(h3(i+vec3(0,1,0)), h3(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i+vec3(0,0,1)), h3(i+vec3(1,0,1)), f.x), mix(h3(i+vec3(0,1,1)), h3(i+vec3(1,1,1)), f.x), f.y), f.z); }
float fbm(vec3 p){ float a = 0.5, s = 0.0; for (int i = 0; i < 4; i++) { s += a * n3(p); p *= 2.03; a *= 0.5; } return s; }
`;

// Paint mask on the statue/plinth from the vertex's REST world position (vOrig), so paint sticks to
// pieces after they break off. topY = crown height; flow = distance the drip front has travelled.
const PAINT_MASK = /* glsl */ `
float paintMask(vec3 p, float topY, float flow, float cap){
  if (flow <= 0.0) return 0.0;
  float ang = atan(p.z, p.x);
  float streak = 0.25 + 0.75 * n1(ang * uStreaks + 3.1) * (0.6 + 0.4 * n1(ang * uStreaks * 2.7 + 9.0));
  float front = topY - min(flow, cap) - max(flow - cap, 0.0) * (0.08 + 1.5 * pow(streak, 2.2));
  float wobble = (n3(p * 9.0) - 0.5) * 0.025;
  return smoothstep(front - 0.006, front + 0.006, p.y + wobble);
}
`;

type Uniforms = Record<string, { value: unknown }>;

// MeshPhysicalMaterial with marble veins + paint, driven by uniforms set every frame.
const makeMarble = (colour: string, veins: boolean, uniforms: Uniforms) => {
  const m = new THREE.MeshPhysicalMaterial({ color: colour, roughness: 0.38, clearcoat: 0.25, clearcoatRoughness: 0.5, side: THREE.DoubleSide });
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nattribute vec3 aOrig;\nvarying vec3 vOrig;")
      .replace("#include <begin_vertex>", "#include <begin_vertex>\nvOrig = aOrig;");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vOrig;\nuniform float uFlow, uTopY, uCap, uStreaks;\nuniform vec3 uPaint, uVein;\n${NOISE}\n${PAINT_MASK}`)
      .replace("#include <color_fragment>", `#include <color_fragment>
        ${veins ? "float v = abs(sin(vOrig.x * 9.0 + fbm(vOrig * 6.0) * 6.0)); diffuseColor.rgb = mix(diffuseColor.rgb, uVein, (1.0 - smoothstep(0.0, 0.18, v)) * 0.35);" : ""}
        float pm = paintMask(vOrig, uTopY, uFlow, uCap);
        diffuseColor.rgb = mix(diffuseColor.rgb, uPaint, pm);`)
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.1, pm);");
  };
  m.customProgramCacheKey = () => `marble-${veins}`;
  return m;
};

// Floor: paint pools spreading from the plinth edge, plus splats where pieces land.
const MAX_SPLATS = 24;
const makeFloor = (uniforms: Uniforms) => {
  const m = new THREE.MeshStandardMaterial({ color: C.colors.floor, roughness: 0.42, metalness: 0.0 });
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vW;")
      .replace("#include <worldpos_vertex>", "#include <worldpos_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vW;\nuniform float uPool, uHalfW, uHalfD;\nuniform vec3 uPaint;\nuniform vec4 uSplats[${MAX_SPLATS}];\n${NOISE}`)
      .replace("#include <color_fragment>", `#include <color_fragment>
        vec2 q = abs(vW.xz) - vec2(uHalfW, uHalfD);
        float dBox = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
        float edge = (fbm(vec3(vW.xz * 2.2, 1.0)) - 0.5) * 0.9 * uPool + (n3(vec3(vW.xz * 9.0, 4.0)) - 0.5) * 0.04;
        float pm = (uPool > 0.0) ? 1.0 - smoothstep(-0.008, 0.008, dBox - uPool * (0.75 + 0.5 * fbm(vec3(normalize(vW.xz + 1e-4) * 1.7, 2.0))) - edge) : 0.0;
        for (int i = 0; i < ${MAX_SPLATS}; i++) {
          vec4 s = uSplats[i];
          if (s.z <= 0.0) continue;
          float d = length(vW.xz - s.xy) + (n3(vec3(vW.xz * 18.0, s.w)) - 0.5) * s.z * 0.5;
          pm = max(pm, 1.0 - smoothstep(s.z - 0.006, s.z + 0.006, d));
        }
        diffuseColor.rgb = mix(diffuseColor.rgb, uPaint, pm);`)
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.06, pm);");
  };
  m.customProgramCacheKey = () => "paint-floor";
  return m;
};

// ---------- geometry: statue placed on the plinth, split into stump + pieces ----------
type Piece = { geo: THREE.BufferGeometry; centre: THREE.Vector3; radius: number; size: number; rank: number };

const useStatue = () => {
  const raw = useLoader(STLLoader, staticFile(C.model));
  return useMemo(() => {
    const g0 = raw.clone();
    g0.deleteAttribute("normal");
    const g = mergeVertices(g0, 1e-5);
    g.computeVertexNormals();
    // orient around the scan's own centre, then sit its lowest point on the plinth, centred
    g.center();
    g.applyMatrix4(new THREE.Matrix4().compose(new THREE.Vector3(), new THREE.Quaternion().setFromEuler(new THREE.Euler(C.statue.rotX, C.statue.rotY, C.statue.rotZ, "YXZ")), new THREE.Vector3().setScalar(C.statue.height)));
    g.computeBoundingBox();
    const b0 = g.boundingBox!;
    g.translate(-(b0.min.x + b0.max.x) / 2, P.h - b0.min.y, -(b0.min.z + b0.max.z) / 2);
    g.computeBoundingBox();
    const bb = g.boundingBox!;
    const pos = g.attributes.position as THREE.BufferAttribute, nor = g.attributes.normal as THREE.BufferAttribute, idx = g.index!;
    const triCount = idx.count / 3;
    const cutY = bb.min.y + (bb.max.y - bb.min.y) * F.cutFraction;
    // triangle centroids
    const cen = new Float32Array(triCount * 3);
    for (let t = 0; t < triCount; t++) for (let k = 0; k < 3; k++) { const v = idx.getX(t * 3 + k); cen[t * 3] += pos.getX(v) / 3; cen[t * 3 + 1] += pos.getY(v) / 3; cen[t * 3 + 2] += pos.getZ(v) / 3; }
    // Voronoi-style seeds from centroids above the cut (seeded)
    const upper: number[] = []; for (let t = 0; t < triCount; t++) if (cen[t * 3 + 1] >= cutY) upper.push(t);
    const seeds: THREE.Vector3[] = [];
    for (let i = 0; i < F.pieces; i++) { const t = upper[Math.floor(random(`${F.seed}-s${i}`) * upper.length)]; seeds.push(new THREE.Vector3(cen[t * 3], cen[t * 3 + 1], cen[t * 3 + 2])); }
    const owner = new Int32Array(triCount);
    for (let t = 0; t < triCount; t++) {
      if (cen[t * 3 + 1] < cutY) { owner[t] = -1; continue; }
      let best = 0, bd = Infinity;
      for (let i = 0; i < seeds.length; i++) { const dx = cen[t * 3] - seeds[i].x, dy = (cen[t * 3 + 1] - seeds[i].y) * 0.8, dz = cen[t * 3 + 2] - seeds[i].z; const d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; best = i; } }
      owner[t] = best;
    }
    const build = (sel: (t: number) => boolean, centre?: THREE.Vector3) => {
      const map = new Map<number, number>(); const p: number[] = [], n: number[] = [], o: number[] = [], ix: number[] = [];
      for (let t = 0; t < triCount; t++) if (sel(t)) for (let k = 0; k < 3; k++) {
        const v = idx.getX(t * 3 + k); let id = map.get(v);
        if (id === undefined) { id = p.length / 3; map.set(v, id); const x = pos.getX(v), y = pos.getY(v), z = pos.getZ(v); o.push(x, y, z); p.push(x - (centre?.x ?? 0), y - (centre?.y ?? 0), z - (centre?.z ?? 0)); n.push(nor.getX(v), nor.getY(v), nor.getZ(v)); }
        ix.push(id);
      }
      // Solid stone: an inner shell offset along -normal plus side walls on the open (broken) edges.
      // Inner/wall vertices get aOrig far below the scene, so the break shows fresh, unpainted marble.
      const th = F.thickness, V = p.length / 3, triN = ix.length / 3, outerCount = ix.length;
      const NO_PAINT = [0, -10, 0];
      for (let v = 0; v < V; v++) {
        p.push(p[v * 3] - n[v * 3] * th, p[v * 3 + 1] - n[v * 3 + 1] * th, p[v * 3 + 2] - n[v * 3 + 2] * th);
        n.push(-n[v * 3], -n[v * 3 + 1], -n[v * 3 + 2]); o.push(...NO_PAINT);
      }
      for (let t = 0; t < triN; t++) ix.push(ix[t * 3] + V, ix[t * 3 + 2] + V, ix[t * 3 + 1] + V);
      const edgeCount = new Map<string, number>();
      for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) { const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`; edgeCount.set(key, (edgeCount.get(key) ?? 0) + 1); }
      for (let t = 0; t < triN; t++) for (let e = 0; e < 3; e++) {
        const a = ix[t * 3 + e], b = ix[t * 3 + (e + 1) % 3]; const key = a < b ? `${a}_${b}` : `${b}_${a}`;
        if (edgeCount.get(key) !== 1) continue;
        const A = new THREE.Vector3(p[a * 3], p[a * 3 + 1], p[a * 3 + 2]), B = new THREE.Vector3(p[b * 3], p[b * 3 + 1], p[b * 3 + 2]);
        const Ai = new THREE.Vector3(p[(a + V) * 3], p[(a + V) * 3 + 1], p[(a + V) * 3 + 2]), Bi = new THREE.Vector3(p[(b + V) * 3], p[(b + V) * 3 + 1], p[(b + V) * 3 + 2]);
        const wn = new THREE.Vector3().subVectors(Ai, A).cross(new THREE.Vector3().subVectors(B, A)).normalize();
        const base = p.length / 3;
        for (const q of [A, B, Bi, Ai]) { p.push(q.x, q.y, q.z); n.push(wn.x, wn.y, wn.z); o.push(...NO_PAINT); }
        ix.push(base, base + 3, base + 1, base + 1, base + 3, base + 2);
      }
      const bg = new THREE.BufferGeometry();
      bg.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); bg.setAttribute("normal", new THREE.Float32BufferAttribute(n, 3)); bg.setAttribute("aOrig", new THREE.Float32BufferAttribute(o, 3)); bg.setIndex(ix);
      bg.addGroup(0, outerCount, 0); // outer, painted surface
      bg.addGroup(outerCount, ix.length - outerCount, 1); // inner stone + break walls (shown once cracking starts)
      return bg;
    };
    const stump = build((t) => owner[t] === -1);
    const pieces: Piece[] = [];
    for (let i = 0; i < seeds.length; i++) {
      const tris: number[] = []; for (let t = 0; t < triCount; t++) if (owner[t] === i) tris.push(t);
      if (tris.length < 8) continue;
      const c = new THREE.Vector3(); for (const t of tris) c.add(new THREE.Vector3(cen[t * 3], cen[t * 3 + 1], cen[t * 3 + 2])); c.divideScalar(tris.length);
      const set = new Set(tris);
      const geo = build((t) => set.has(t), c);
      geo.computeBoundingSphere();
      pieces.push({ geo, centre: c, radius: geo.boundingSphere!.radius, size: tris.length, rank: 0 });
    }
    // release order: top first, with seeded jitter
    const order = pieces.map((p, i) => ({ i, k: p.centre.y + random(`${F.seed}-o${i}`) * 0.25 })).sort((a, b) => b.k - a.k);
    order.forEach((o, r) => (pieces[o.i].rank = r / Math.max(1, order.length - 1)));
    return { stump, pieces, topY: bb.max.y, bb };
  }, [raw]);
};

// Deterministic fall: crack gap, then a ballistic arc outward, one damped bounce, rest.
const pieceState = (p: Piece, i: number, t: number) => {
  const out = new THREE.Vector3(p.centre.x, 0, p.centre.z);
  if (out.lengthSq() < 1e-6) out.set(random(`${F.seed}-dx${i}`) - 0.5, 0, random(`${F.seed}-dz${i}`) - 0.5);
  out.normalize().applyAxisAngle(new THREE.Vector3(0, 1, 0), (random(`${F.seed}-a${i}`) - 0.5) * 0.8);
  const crack = clamp((t - F.crackStart) / (F.breakStart - F.crackStart));
  const pos = p.centre.clone().addScaledVector(new THREE.Vector3(p.centre.x, p.centre.y - (P.h + 0.5), p.centre.z).normalize(), F.crackGap * easeOut(crack) * (0.5 + random(`${F.seed}-g${i}`)));
  const rot = new THREE.Euler((random(`${F.seed}-r1${i}`) - 0.5) * 0.04 * crack, 0, (random(`${F.seed}-r2${i}`) - 0.5) * 0.04 * crack);
  const release = F.breakStart + (F.breakEnd - F.breakStart) * Math.pow(p.rank, 0.85);
  const dt = t - release;
  let landed = false, landT = 0, land = new THREE.Vector3();
  if (dt > 0) {
    const restY = Math.max(0.03, p.radius * 0.45);
    const drop = Math.max(0.05, pos.y - restY);
    const T = Math.sqrt((2 * drop) / F.gravity);
    const R0 = Math.hypot(pos.x, pos.z);
    const Rl = F.landMin + (F.landMax - F.landMin) * random(`${F.seed}-l${i}`);
    const vh = Math.max(0.15, (Rl - R0) / T);
    const tau = Math.min(dt, T);
    const start = pos.clone();
    pos.x = start.x + out.x * vh * tau; pos.z = start.z + out.z * vh * tau;
    pos.y = start.y - 0.5 * F.gravity * tau * tau;
    const spin = new THREE.Vector3(random(`${F.seed}-w1${i}`) - 0.5, random(`${F.seed}-w2${i}`) - 0.5, random(`${F.seed}-w3${i}`) - 0.5).multiplyScalar(9);
    const spinT = tau + (dt > T ? Math.min(dt - T, 0.35) * (1 - Math.min(dt - T, 0.35) / 0.7) : 0);
    rot.set(rot.x + spin.x * spinT, spin.y * spinT, rot.z + spin.z * spinT);
    if (dt > T) {
      landed = true; landT = release + T;
      const b = dt - T, Tb = 2 * Math.sqrt((2 * F.bounce * drop * 0.25) / F.gravity);
      if (b < Tb) { const u = b / Tb; pos.y = restY + 4 * F.bounce * drop * 0.25 * u * (1 - u); }
      else pos.y = restY;
      const slide = easeOut(Math.min(b, 0.6) / 0.6) * 0.12;
      pos.x += out.x * slide; pos.z += out.z * slide;
      land = new THREE.Vector3(start.x + out.x * vh * T, 0, start.z + out.z * vh * T);
    }
  }
  return { pos, rot, landed, landT, land };
};

// GTAO + output pass, rendered once per Remotion frame (no animation here).
const Post: React.FC = () => {
  const { gl, scene, camera, size } = useThree();
  const composer = useMemo(() => {
    const c = new EffectComposer(gl);
    c.setPixelRatio(1);
    c.setSize(size.width, size.height);
    c.addPass(new RenderPass(scene, camera));
    const ao = new GTAOPass(scene, camera, size.width, size.height);
    ao.updateGtaoMaterial({ radius: C.ao.radius, distanceExponent: 1, thickness: C.ao.thickness, scale: 1, samples: 16, distanceFallOff: C.ao.distanceFallOff });
    ao.blendIntensity = C.ao.blend;
    c.addPass(ao);
    c.addPass(new OutputPass());
    return c;
  }, [gl, scene, camera, size.width, size.height]);
  useFrame(() => composer.render(), 1);
  return null;
};

const Env: React.FC = () => {
  const { gl, scene } = useThree();
  useMemo(() => { const pm = new THREE.PMREMGenerator(gl); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = C.light.env; }, [gl, scene]);
  return null;
};

const Scene: React.FC<{ t: number }> = ({ t }) => {
  const { stump, pieces, topY } = useStatue();
  const { camera } = useThree();
  const uniforms = useMemo<Uniforms>(() => ({ uFlow: { value: 0 }, uTopY: { value: topY }, uCap: { value: PA.capDepth }, uStreaks: { value: PA.streaks }, uPaint: { value: new THREE.Color(C.colors.paint) }, uVein: { value: new THREE.Color(C.colors.vein) } }), [topY]);
  const floorU = useMemo<Uniforms>(() => ({ uPool: { value: 0 }, uHalfW: { value: P.w / 2 }, uHalfD: { value: P.d / 2 }, uPaint: { value: new THREE.Color(C.colors.paint) }, uSplats: { value: Array.from({ length: MAX_SPLATS }, () => new THREE.Vector4(0, 0, 0, 0)) } }), []);
  const marble = useMemo(() => makeMarble(C.colors.marble, true, uniforms), [uniforms]);
  const inner = useMemo(() => { const m = makeMarble(C.colors.marble, true, uniforms); m.polygonOffset = true; m.polygonOffsetFactor = 2; m.polygonOffsetUnits = 2; return m; }, [uniforms]);
  const statueMats = useMemo(() => [marble, inner], [marble, inner]);
  const plinthMat = useMemo(() => makeMarble(C.colors.plinth, false, uniforms), [uniforms]);
  const floorMat = useMemo(() => makeFloor(floorU), [floorU]);
  const plinthGeo = useMemo(() => {
    const g = new THREE.BoxGeometry(P.w, P.h, P.d, 1, 1, 1); g.translate(0, P.h / 2, 0);
    g.setAttribute("aOrig", g.attributes.position.clone());
    return g;
  }, []);

  inner.visible = t >= F.crackStart; // the break's inner stone only exists once it cracks
  // paint flow and pool
  const flow = PA.speed * Math.pow(Math.max(0, t - PA.start), PA.slowdown);
  uniforms.uFlow.value = flow;
  const poolT = Math.max(0, t - PA.floorReach);
  const pool = PA.poolMax * (1 - Math.exp(-poolT / (PA.poolGrow / 3)));
  floorU.uPool.value = pool;

  // pieces
  const states = pieces.map((p, i) => pieceState(p, i, t));
  const splats = floorU.uSplats.value as THREE.Vector4[];
  const big = pieces.map((p, i) => ({ p, i })).sort((a, b) => b.p.size - a.p.size).slice(0, MAX_SPLATS);
  big.forEach(({ p, i }, k) => {
    const s = states[i];
    if (!s.landed) { splats[k].set(0, 0, 0, 0); return; }
    const grow = easeOut((t - s.landT) / 0.35);
    const r = (C.fracture.splatRadius[0] + (C.fracture.splatRadius[1] - C.fracture.splatRadius[0]) * random(`${F.seed}-sp${i}`)) * Math.min(1, p.radius * 6);
    splats[k].set(s.land.x, s.land.z, r * grow, i + 1);
  });

  // camera: slow push, then ease back to reveal the floor
  const k = easeInOut(t / C.output.durationInSeconds);
  const lerp3 = (a: number[], b: number[]) => a.map((v, j) => v + (b[j] - v) * k) as [number, number, number];
  camera.position.set(...lerp3(C.camera.from.pos, C.camera.to.pos));
  (camera as THREE.PerspectiveCamera).fov = C.camera.fov;
  (camera as THREE.PerspectiveCamera).updateProjectionMatrix();
  camera.lookAt(...lerp3(C.camera.from.look, C.camera.to.look));

  const L = C.light;
  return (
    <>
      <Env />
      <color attach="background" args={[C.colors.background]} />
      <fog attach="fog" args={[C.colors.background, 7, 16]} />
      <spotLight position={L.key.position} intensity={L.key.intensity} angle={L.key.angle} penumbra={L.key.penumbra} decay={2} castShadow
        shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-bias={-0.0002} shadow-normalBias={0.02} target-position={[0, 1.2, 0]} />
      <pointLight position={L.rim.position} intensity={L.rim.intensity} color={C.colors.rim} decay={2} />
      {/* GI look: the pink pool bounces light up onto the statue */}
      <pointLight position={[0.2, 0.05, 1.7]} intensity={L.bounce * clamp(pool / PA.poolMax)} color={C.colors.paint} decay={2} distance={4} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow material={floorMat}>
        <planeGeometry args={[40, 40]} />
      </mesh>
      <mesh geometry={plinthGeo} material={plinthMat} castShadow receiveShadow />
      <mesh geometry={stump} material={statueMats} castShadow receiveShadow />
      {pieces.map((p, i) => (
        <mesh key={i} geometry={p.geo} material={statueMats} position={states[i].pos} rotation={states[i].rot} castShadow receiveShadow />
      ))}
      <Post />
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
        camera={{ fov: C.camera.fov, near: 0.05, far: 60, position: C.camera.from.pos }}>
        <Scene t={frame / fps} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
