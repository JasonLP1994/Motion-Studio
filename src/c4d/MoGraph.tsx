// Cinema 4D-style MoGraph demo in Remotion: a cloner grid of rounded clay cubes, a glossy sphere
// effector that rolls through it, a spring "delay effector" response and a closing shockwave.
// Deterministic: every value is a pure function of frame / fps (no useFrame, no clock).
import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { c4dConfig as C } from "./config";

const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const smooth = (x: number) => ((x = clamp(x)), x * x * (3 - 2 * x));

const S = C.sphere;
const curve = new THREE.CatmullRomCurve3(S.path.map(([x, z]) => new THREE.Vector3(x, 0, z)), false, "centripetal");

// Sphere centre on the floor plane at time t (x, z) and its height.
const spherePos = (t: number) => {
  if (t < S.rollStart) {
    const p = curve.getPointAt(0);
    let y: number;
    const rest = S.radius + C.grid.baseHeight; // the sphere sits on top of the resting tiles
    if (t < S.land) y = rest + (S.dropFrom - rest) * (1 - Math.pow(t / S.land, 2)); // gravity-like fall
    else { const u = (t - S.land) / (S.bounce.until - S.land); y = rest + 4 * S.bounce.height * u * (1 - u); }
    return { x: p.x, z: p.z, y };
  }
  const u = easeInOut((t - S.rollStart) / (S.rollEnd - S.rollStart));
  const p = curve.getPointAt(clamp(u));
  return { x: p.x, z: p.z, y: S.radius + C.grid.baseHeight };
};

// Rolling rotation: integrate travelled distance along the path (sampled, deterministic).
const sphereRotation = (t: number) => {
  const q = new THREE.Quaternion();
  const steps = Math.ceil(clamp(t - S.rollStart, 0, 99) * 60);
  let prev = spherePos(S.rollStart);
  for (let i = 1; i <= steps; i++) {
    const cur = spherePos(Math.min(t, S.rollStart + i / 60));
    const dx = cur.x - prev.x, dz = cur.z - prev.z, d = Math.hypot(dx, dz);
    if (d > 1e-6) q.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(dz / d, 0, -dx / d), d / S.radius));
    prev = cur;
  }
  return q;
};

// Raw effector strength for a cube at (x, z) at time t (0..1+).
const target = (x: number, z: number, t: number) => {
  const p = spherePos(t - C.effector.lag);
  const E = C.effector;
  const contact = clamp(1 - (p.y - S.radius - C.grid.baseHeight) / 0.35); // reacts only on (near) contact
  const d = Math.hypot(x - p.x, z - p.z);
  // bow wave: a ring of cubes rises around the sphere; cubes right underneath are pressed down
  const ringOn = 1 - smooth((t - S.rollEnd) / E.ringFade); // ring sinks back once the sphere has stopped
  let v = contact * (ringOn * Math.exp(-Math.pow((d - E.ringRadius) / E.ringWidth, 2)) - E.press * (1 - smooth(d / (S.radius * 1.1))));
  const R = C.ripple;
  if (t > R.start) {
    const r = (t - R.start) * R.speed, dc = Math.hypot(x, z);
    v += R.amount * Math.exp(-Math.pow((dc - r) / R.width, 2)) * Math.exp(-(t - R.start) / R.decay);
  }
  return v;
};

// Delay effector: convolve the target's recent history with a damped-spring impulse response.
const kernel = (() => {
  const { omega: w, damping: z, window } = C.spring, dt = 1 / 120, n = Math.round(window / dt);
  const wd = w * Math.sqrt(1 - z * z);
  const k = Array.from({ length: n }, (_, i) => Math.exp(-z * w * i * dt) * Math.sin(wd * i * dt));
  const sum = k.reduce((a, b) => a + b, 0);
  return { dt, k: k.map((v) => v / sum) };
})();
const springy = (x: number, z: number, t: number) => {
  let v = 0;
  for (let i = 0; i < kernel.k.length; i++) v += kernel.k[i] * target(x, z, t - i * kernel.dt);
  return v;
};

const colLow = new THREE.Color(C.palette.clayLow), colMid = new THREE.Color(C.palette.clayMid), colHigh = new THREE.Color(C.palette.clayHigh);
const heightColour = (h: number) => (h < 0.5 ? colLow.clone().lerp(colMid, h / 0.5) : colMid.clone().lerp(colHigh, (h - 0.5) / 0.5));

// Local studio reflections (no downloads): RoomEnvironment through PMREM.
const Studio: React.FC = () => {
  const { gl, scene } = useThree();
  useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = C.light.envIntensity;
  }, [gl, scene]);
  return null;
};

const Scene: React.FC<{ t: number }> = ({ t }) => {
  const G = C.grid;
  const box = useMemo(() => new RoundedBoxGeometry(G.size, 1, G.size, 4, G.radius), [G.size, G.radius]);
  const cubes = useMemo(() => {
    const out: { x: number; z: number }[] = [];
    const half = ((G.count - 1) * G.spacing) / 2;
    for (let i = 0; i < G.count; i++) for (let j = 0; j < G.count; j++) out.push({ x: -half + i * G.spacing, z: -half + j * G.spacing });
    return out;
  }, [G.count, G.spacing]);
  const sp = spherePos(t), rot = sphereRotation(t);
  const cam = C.camera;
  const ang = THREE.MathUtils.degToRad(cam.orbitFrom + (cam.orbitTo - cam.orbitFrom) * easeInOut(t / cam.orbitEnd));
  const camPos: [number, number, number] = [Math.sin(ang) * cam.distance, cam.height, Math.cos(ang) * cam.distance];
  const { camera } = useThree();
  camera.position.set(...camPos);
  (camera as THREE.PerspectiveCamera).fov = cam.fov;
  (camera as THREE.PerspectiveCamera).updateProjectionMatrix();
  camera.lookAt(...cam.lookAt);
  return (
    <>
      <Studio />
      <color attach="background" args={[C.palette.backdrop]} />
      <ambientLight intensity={C.light.ambient} />
      <directionalLight position={C.light.key} intensity={C.light.keyIntensity} castShadow
        shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-camera-left={-8} shadow-camera-right={8}
        shadow-camera-top={8} shadow-camera-bottom={-8} shadow-bias={-0.0004} />
      {/* seamless sweep: floor, cove, back wall */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, 0, 2]}>
        <planeGeometry args={[60, 26]} />
        <meshStandardMaterial color={C.palette.backdrop} roughness={0.95} />
      </mesh>
      <mesh position={[0, 4, -11]} rotation={[0, 0, Math.PI / 2]} receiveShadow>
        <cylinderGeometry args={[4, 4, 60, 48, 1, true, Math.PI, Math.PI / 2]} />
        <meshStandardMaterial color={C.palette.backdrop} roughness={0.95} side={THREE.BackSide} />
      </mesh>
      <mesh position={[0, 14, -15]} receiveShadow>
        <planeGeometry args={[60, 20]} />
        <meshStandardMaterial color={C.palette.backdrop} roughness={0.95} />
      </mesh>
      {cubes.map((c, i) => {
        const v = clamp(springy(c.x, c.z, t), -0.35, 1.4);
        const h = Math.max(0.06, G.baseHeight + (v >= 0 ? G.maxRise * v : G.baseHeight * v * 2)); // pressed cubes sink, never vanish
        return (
          <mesh key={i} geometry={box} position={[c.x, h / 2, c.z]} scale={[1, h, 1]} castShadow receiveShadow>
            <meshPhysicalMaterial color={heightColour(clamp(v))} roughness={0.55} clearcoat={0.25} clearcoatRoughness={0.6} />
          </mesh>
        );
      })}
      <mesh position={[sp.x, sp.y, sp.z]} quaternion={rot} castShadow>
        <sphereGeometry args={[S.radius, 64, 64]} />
        <meshPhysicalMaterial color={C.palette.sphere} roughness={0.12} clearcoat={1} clearcoatRoughness={0.05} metalness={0.1} />
      </mesh>
    </>
  );
};

export const MoGraph: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: C.palette.backdrop }}>
      <ThreeCanvas width={width} height={height} shadows="soft" gl={{ antialias: true, preserveDrawingBuffer: true, toneMappingExposure: C.light.exposure }}
        camera={{ fov: C.camera.fov, near: 0.1, far: 200, position: [0, C.camera.height, C.camera.distance] }}>
        <Scene t={frame / fps} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
