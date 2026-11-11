// Painted statue that breaks apart (cinematic v2).
// A real marble scan: lights fade up through haze, thick glossy paint pours and drips, molten cracks
// spread, then a slow-motion explosion with chips, dust and splashes into a paint pool on a
// mirror-polished floor. GTAO + depth of field + bloom + film grade.
// Deterministic: everything is computed from frame / fps. The single useFrame below only takes over
// rendering (composer.render()) once per Remotion frame; it animates nothing.
import React, { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useFrame, useLoader, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { Reflector } from "three/examples/jsm/objects/Reflector.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { BokehPass } from "three/examples/jsm/postprocessing/BokehPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { RectAreaLightUniformsLib } from "three/examples/jsm/lights/RectAreaLightUniformsLib.js";
import { statueConfig as C } from "./config";

RectAreaLightUniformsLib.init(); // enables invisible softbox (area) lights on physical materials

import { clamp, easeInOut, easeOut, smooth, R, P, F, PA, T, storyTime, buildStatue, flight } from "./fracture";

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
  const m = new THREE.MeshPhysicalMaterial({ color: colour, roughness: 0.33, clearcoat: 0.3, clearcoatRoughness: 0.45, side: THREE.DoubleSide,
    sheen: 0.5, sheenRoughness: 0.55, sheenColor: new THREE.Color("#FFD6CC") }); // sheen: soft light at grazing edges, a cheap stand-in for light inside marble
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, u);
    // scene 3: a wind-swept dissolve turns the rubble to dust, left to right
    shader.vertexShader = "uniform float uDust;\nvarying vec3 vDw;\n" + shader.vertexShader.replace("#include <project_vertex>", "#include <project_vertex>\nvDw = (modelMatrix * vec4(transformed, 1.0)).xyz;");
    shader.fragmentShader = "uniform float uDust;\nvarying vec3 vDw;\n" + shader.fragmentShader.replace("#include <clipping_planes_fragment>", "#include <clipping_planes_fragment>\nif (uDust > 0.0) { float hd = fract(sin(dot(floor(vDw * 420.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453); if (vDw.x * 0.4 + 0.5 + (hd - 0.5) * 0.35 < uDust * 1.5 - 0.25) discard; }");
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
      .replace("#include <normal_fragment_maps>", "#include <normal_fragment_maps>\nvec3 dp = vOrig.y > -5.0 ? vOrig : vDw;\nvec3 pore = vec3(n3(dp * 210.0), n3(dp * 210.0 + 7.1), n3(dp * 210.0 + 13.7)) - 0.5;\nvec3 chis = vec3(n3(dp * vec3(38.0, 90.0, 38.0)), n3(dp * vec3(38.0, 90.0, 38.0) + 3.3), n3(dp * vec3(38.0, 90.0, 38.0) + 5.9)) - 0.5;\nvec3 rip = vec3(n3(dp * 26.0 + 2.0), 0.0, n3(dp * 26.0 + 9.0)) - vec3(0.5, 0.0, 0.5);\nnormal = normalize(normal + (pore * 0.16 + chis * 0.1) * (1.0 - pm) + rip * 0.08 * pm); // marble pores + chisel, gentle ripple in the paint")
      .replace("#include <lights_physical_fragment>", "#include <lights_physical_fragment>\nmaterial.clearcoat = mix(material.clearcoat, 1.0, pm);\nmaterial.clearcoatRoughness = mix(material.clearcoatRoughness, 0.05, pm); // wet glossy layer on the paint only")
      .replace("#include <emissivemap_fragment>", "#include <emissivemap_fragment>\ntotalEmissiveRadiance += uCrack * cg * uCrackI;")
      .replace("#include <dithering_fragment>", "#include <dithering_fragment>\nif (any(isnan(gl_FragColor.rgb)) || any(isinf(gl_FragColor.rgb))) gl_FragColor.rgb = vec3(0.0);\ngl_FragColor.rgb = min(gl_FragColor.rgb, vec3(3.0)); // guard: bad normals on crack seams made glowing blobs");
  };
  m.customProgramCacheKey = () => `marble6-${veins}`;
  return m;
};

// ROME letter mask: white letters on black, drawn with the Cinzel font once it has loaded.
const RM = C.rome;
const romeCanvas = typeof document !== "undefined" ? document.createElement("canvas") : null;
const romeTex = romeCanvas ? new THREE.CanvasTexture(romeCanvas) : new THREE.Texture();
let romeAspect = 0.3; // height / width of the word, set when drawn
const drawRome = () => {
  if (!romeCanvas) return;
  const W = 2048, H = 640; romeCanvas.width = W; romeCanvas.height = H;
  const g = romeCanvas.getContext("2d")!;
  g.fillStyle = "#000"; g.fillRect(0, 0, W, H);
  g.font = `${RM.weight} 440px CinzelLocal`; g.textAlign = "center"; g.textBaseline = "middle";
  const m = g.measureText(RM.text); const scale = Math.min(1, (W * 0.92) / m.width);
  g.save(); g.translate(W / 2, H / 2 + 20); g.scale(scale, 1);
  g.fillStyle = "#fff"; g.letterSpacing = "30px"; g.fillText(RM.text, 0, 0); g.restore();
  romeAspect = H / W;
  romeTex.anisotropy = 8; romeTex.needsUpdate = true;
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
      .replace("#include <common>", `#include <common>\nvarying vec3 vW;\nuniform float uPool, uHalfW, uHalfD, uFloorA, uFadeA, uFadeB, uCarve, uStream, uFill, uRomeW, uRomeA;\nuniform vec2 uRomeC;\nuniform float uStreamX[4];\nuniform float uDrain;\nuniform sampler2D uRome;\nuniform vec3 uPaint, uFogC;\nfloat romeAt(vec2 xz){ vec2 q = (xz - uRomeC) / vec2(uRomeW, uRomeW * uRomeA) + 0.5; if (q.x < 0.0 || q.x > 1.0 || q.y < 0.0 || q.y > 1.0) return 0.0; return texture2D(uRome, vec2(q.x, 1.0 - q.y)).r; }\nuniform vec4 uSplats[${MAX_SPLATS}];\n${NOISE}`)
      .replace("#include <color_fragment>", `#include <color_fragment>
        vec2 q = abs(vW.xz) - vec2(uHalfW, uHalfD);
        float dBox = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
        float edge = (fbm(vec3(vW.xz * 2.2, 1.0)) - 0.5) * 0.9 * uPool + (n3(vec3(vW.xz * 9.0, 4.0)) - 0.5) * 0.04;
        float pm = (uPool > 0.0) ? 1.0 - smoothstep(-0.008, 0.008, dBox - uPool * (0.75 + 0.5 * fbm(vec3(normalize(vW.xz + 1e-4) * 1.7, 2.0))) - edge) : 0.0;
        for (int i = 0; i < ${MAX_SPLATS}; i++) { vec4 s = uSplats[i]; if (s.z <= 0.0) continue;
          float d = length(vW.xz - s.xy) + (n3(vec3(vW.xz * 18.0, s.w)) - 0.5) * s.z * 0.5;
          pm = max(pm, 1.0 - smoothstep(s.z - 0.006, s.z + 0.006, d)); }
        // carved ROME: grooves in the floor; as the paint settles it drains off the flat floor and stays in the letters
        // carved ROME (scene 2): empty grooves first, then rivulets run from the pool and the liquid fills each letter
        float Lm = romeAt(vW.xz) * uCarve;
        float e = 0.004; vec2 gr = uCarve * vec2(romeAt(vW.xz + vec2(e, 0.0)) - romeAt(vW.xz - vec2(e, 0.0)), romeAt(vW.xz + vec2(0.0, e)) - romeAt(vW.xz - vec2(0.0, e)));
        float wall = clamp(length(gr), 0.0, 1.0);
        float litWall = clamp(dot(gr, normalize(vec2(-0.6, -0.8))), -1.0, 1.0);
        float hW = uRomeW * uRomeA;                                         // word box depth
        float zTop = uRomeC.y - hW * 0.3;                                   // where the rivulets reach the letters
        float st = 0.0;
        for (int k = 0; k < 4; k++) {
          float fk = float(k);
          float xc = uRomeC.x + uStreamX[k] + 0.022 * sin(vW.z * 13.0 + fk * 2.1);
          float z0 = mix(uRomeC.y - 0.45, zTop - 0.01, uDrain);   // the tail follows the last of the liquid in
          float z1 = mix(z0, zTop, clamp(uStream * 1.2 - fk * 0.06, 0.0, 1.0));
          float w = 0.024 + 0.008 * sin(vW.z * 29.0 + fk * 3.0) + 0.01 * smoothstep(z1 - 0.05, z1, vW.z); // bulging tip
          st = max(st, (1.0 - smoothstep(w * 0.55, w, abs(vW.x - xc))) * step(z0, vW.z) * (1.0 - smoothstep(z1 - 0.006, z1, vW.z)));
        }
        st *= uCarve * (1.0 - smoothstep(0.75, 0.98, uDrain));        // the last of each rivulet soaks into the letter
        float qy = clamp((vW.z - (uRomeC.y - hW * 0.5)) / hW, 0.0, 1.0);    // 0 = top of the word, 1 = bottom
        float front = uFill * 1.3 - 0.15 + (fbm(vec3(vW.xz * 7.0, 3.0)) - 0.5) * 0.18;
        float filled = Lm * (1.0 - smoothstep(front - 0.02, front, qy));
        float men = Lm * (smoothstep(front - 0.06, front - 0.02, qy) - smoothstep(front - 0.02, front, qy)); // glossy leading edge
        pm = max(pm * (1.0 - Lm), max(st, filled));
        vec3 floorC = diffuseColor.rgb * (1.0 - 0.6 * Lm);                 // empty groove: deeper, darker
        diffuseColor.rgb = mix(floorC, uPaint * (1.0 + 0.7 * filled), pm);
        diffuseColor.rgb *= 1.0 - 0.85 * wall;                             // shadowed carved edges
        diffuseColor.rgb += uPaint * max(litWall, 0.0) * 1.4;              // lit lip of the cut
        diffuseColor.rgb += uPaint * men * 1.6;
        diffuseColor.a = mix(uFloorA, 1.0, pm);`)
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.04, pm);")
      // infinite floor: with distance the floor turns into exactly the cove's horizon colour (opaque, unlit)
      .replace("#include <lights_fragment_end>", "#include <lights_fragment_end>\nreflectedLight.directSpecular = vec3(0.0); // never show the lights in the pool")
      .replace("#include <fog_fragment>", "#include <fog_fragment>\nfloat far0 = smoothstep(uFadeA, uFadeB, length(vW.xz));\ngl_FragColor = vec4(mix(gl_FragColor.rgb, uFogC, far0), mix(gl_FragColor.a, 1.0, far0));");
  };
  m.customProgramCacheKey = () => "paint-floor7";
  return m;
};

// Final grade: split-tone, vignette, film grain, a touch of chromatic aberration.
const GradeShader = {
  uniforms: { tDiffuse: { value: null }, uSeed: { value: 0 }, uGrain: { value: C.post.grain }, uVig: { value: C.post.vignette }, uFade: { value: 1 }, uDesat: { value: C.desaturate }, uTint: { value: C.redTint }, uGlow: { value: C.post.topGlow }, uTime: { value: 0 }, uSmoke: { value: C.post.smoke.amount }, uSmokeScale: { value: C.post.smoke.scale }, uSmokeSpeed: { value: C.post.smoke.speed }, uCam: { value: new THREE.Vector2() }, uSmokeC: { value: new THREE.Color(C.post.smoke.color).convertLinearToSRGB() }, uSh: { value: new THREE.Color(C.colors.background) }, uMid: { value: new THREE.Color(C.colors.haze) }, uHi: { value: new THREE.Color(C.colors.hazeHot) } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse; uniform float uSeed, uGrain, uVig, uFade, uDesat, uTint, uGlow, uTime, uSmoke, uSmokeScale, uSmokeSpeed; uniform vec2 uCam; uniform vec3 uSmokeC; uniform vec3 uSh, uMid, uHi; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + uSeed) * 43758.5453); }
    // smoke near the lens: domain-warped value noise, drifting slowly (pure function of time)
    float h3(vec3 p){ p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
    float vn(vec3 x){ vec3 i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(mix(h3(i), h3(i + vec3(1,0,0)), f.x), mix(h3(i + vec3(0,1,0)), h3(i + vec3(1,1,0)), f.x), f.y),
                 mix(mix(h3(i + vec3(0,0,1)), h3(i + vec3(1,0,1)), f.x), mix(h3(i + vec3(0,1,1)), h3(i + vec3(1,1,1)), f.x), f.y), f.z); }
    float fbm3(vec3 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 5; i++){ s += a * vn(p); p = p * 2.03 + 11.7; a *= 0.5; } return s; }
    float smoke(vec2 uv, float depth){
      vec3 p = vec3(uv * vec2(1.78, 1.0) * uSmokeScale * depth + uCam * depth, uTime * 0.07);
      p.x -= uTime * uSmokeSpeed * depth; p.y += uTime * uSmokeSpeed * 0.35;
      vec3 w = vec3(fbm3(p + vec3(3.1, 0.0, 0.0)), fbm3(p + vec3(0.0, 7.4, 1.3)), 0.0);
      float n = fbm3(p + w * 1.6);
      return smoothstep(0.38, 0.8, n);
    }
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
      // two smoke layers (near + far) for parallax; lit from above, see-through
      float sNear = smoke(vUv, 1.0), sFar = smoke(vUv + 0.37, 1.8);
      float lit = 0.55 + 0.45 * smoothstep(0.0, 1.0, vUv.y);
      float sa = clamp(sNear * 0.75 + sFar * 0.45, 0.0, 1.0) * uSmoke;
      c = mix(c, uSmokeC * lit, sa); // grade runs in display space, so the smoke colour is sRGB
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
const useStatue = () => {
  const raw = useLoader(STLLoader, staticFile(C.model));
  return useMemo(() => buildStatue(raw), [raw]);
};


// ---------- post ----------
const Post: React.FC<{ focus: number; aperture: number; bloom: number; seed: number; fade: number; time: number; cam: [number, number] }> = ({ focus, aperture, bloom, seed, fade, time, cam }) => {
  const { gl, scene, camera, size } = useThree();
  const passes = useMemo(() => {
    const rt = new THREE.WebGLRenderTarget(size.width, size.height, { samples: 4, type: THREE.HalfFloatType }); // 4x MSAA: smooth edges
    const c = new EffectComposer(gl, rt); c.setPixelRatio(1); c.setSize(size.width, size.height);
    c.addPass(new RenderPass(scene, camera));
    const ao = new GTAOPass(scene, camera, size.width, size.height);
    ao.updateGtaoMaterial({ radius: C.post.ao.radius, distanceExponent: 1, thickness: C.post.ao.thickness, scale: 1, samples: 32, distanceFallOff: 1 });
    ao.blendIntensity = C.post.ao.blend; c.addPass(ao);
    const bokeh = new BokehPass(scene, camera, { focus: 2.5, aperture: C.post.dof.aperture, maxblur: C.post.dof.maxblur }); c.addPass(bokeh);
    const bl = new UnrealBloomPass(new THREE.Vector2(size.width, size.height), C.post.bloom.strength, C.post.bloom.radius, C.post.bloom.threshold); c.addPass(bl);
    c.addPass(new OutputPass());
    const grade = new ShaderPass(GradeShader); c.addPass(grade);
    return { c, bokeh, bl, grade };
  }, [gl, scene, camera, size.width, size.height]);
  (passes.bokeh.uniforms as Record<string, { value: number }>).focus.value = focus;
  (passes.bokeh.uniforms as Record<string, { value: number }>).aperture.value = aperture;
  passes.bl.strength = bloom;
  passes.grade.uniforms.uSeed.value = seed;
  passes.grade.uniforms.uFade.value = fade;
  passes.grade.uniforms.uTime.value = time;
  passes.grade.uniforms.uCam.value.set(cam[0], cam[1]);
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
      fragmentShader: "uniform vec3 uBg, uHaze, uHot; varying vec3 vD; void main(){ vec3 d = normalize(vD); float top = smoothstep(0.2, 1.0, d.y); vec3 sb = normalize(vec3(0.8, 0.55, -0.4)); float strip = smoothstep(0.93, 0.985, dot(d, sb)); gl_FragColor = vec4(uBg + uHaze * top * 1.5 + uHot * pow(top, 4.0) * 0.35 + uHot * strip * 6.0, 1.0); }",
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
    uCrackW: { value: -1 }, uCrackFront: { value: 99 }, uCrackI: { value: 0 }, uDust: { value: 0 },
  }), [topY]);
  const floorU = useMemo<Uniforms>(() => ({ uPool: { value: 0 }, uHalfW: { value: P.w / 2 }, uHalfD: { value: P.d / 2 }, uFloorA: { value: C.post.reflector.floorOpacity }, uFadeA: { value: C.cove.floorFadeStart }, uFadeB: { value: C.cove.floorFadeEnd }, uFogC: { value: new THREE.Color(C.colors.fog) }, uCarve: { value: 0 }, uDrain: { value: 0 }, uStream: { value: 0 }, uFill: { value: 0 }, uStreamX: { value: RM.streams }, uRome: { value: romeTex }, uRomeC: { value: new THREE.Vector2(...RM.centre) }, uRomeW: { value: RM.width }, uRomeA: { value: 0.3125 }, uPaint: { value: new THREE.Color(C.colors.paint) }, uSplats: { value: Array.from({ length: MAX_SPLATS }, () => new THREE.Vector4()) } }), []);
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
  const drainK = smooth(C.scene3.drain[0], C.scene3.drain[1], t); // the pool drains into ROME
  floorU.uPool.value = pool * (1 - 0.95 * drainK);
  floorU.uDrain.value = drainK;
  floorU.uCarve.value = t >= RM.carveFrom ? 1 : 0; // the carving only exists in scene 2 (switches on during the dip to black)
  floorU.uStream.value = smooth(RM.streamT[0], RM.streamT[1], t);
  floorU.uFill.value = smooth(RM.fillT[0], RM.fillT[1], t);
  floorU.uRomeA.value = romeAspect;

  // --- cracks: spread down from the crown, glow, flash at the boom, fade as pieces fly ---
  const crackK = smooth(T.crackStart, T.boom, t);
  u.uCrackW.value = t < T.crackStart ? -1 : F.crackWidth * (0.3 + 0.7 * crackK);
  u.uCrackFront.value = topY + 0.02 - crackK * 1.2;
  u.uCrackI.value = (t < T.crackStart ? 0 : C.crackGlow * (0.3 + 0.7 * crackK)) * (t > T.boom ? Math.exp(-(t - T.boom) * 1.2) : 1);
  inner.visible = t >= T.boom - 0.05; // piece insides only once it breaks (they poke through slightly while still whole)

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
    splats[k].set(st.land.x, st.land.z, r * easeOut((s - st.landS) / 0.25) * (1 - smooth(C.scene3.drain[0], C.scene3.drain[1], t)), i + 1);
  });

  // --- chips (instanced) ---
  const S3 = C.scene3;
  const dustK = clamp((t - S3.dust[0]) / (S3.dust[1] - S3.dust[0]));
  u.uDust.value = dustK;
  const sweptAt = (x: number, jitter: number) => clamp((x * 0.4 + 0.75 + (jitter - 0.5) * 0.35) / 1.5); // dust progress when the wind reaches x
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
    dummy.scale.setScalar(s > T.boom && dustK <= sweptAt(f.pos.x, R(`cj${i}`)) ? sz : 0);
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

  // --- ash: each piece breaks into dust as the wind passes, and the dust blows away ---
  const ash = useMemo(() => {
    const n = S3.ashCount, g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(new Float32Array(n * 4), 4));
    const m = new THREE.PointsMaterial({ size: S3.ashSize, map: sprite, transparent: true, depthWrite: false, vertexColors: true, sizeAttenuation: true });
    const pts = new THREE.Points(g, m); pts.frustumCulled = false; return pts;
  }, [sprite]);
  {
    const ap = ash.geometry.getAttribute("position") as THREE.BufferAttribute, ac = ash.geometry.getAttribute("color") as THREE.BufferAttribute;
    for (let i = 0; i < S3.ashCount; i++) {
      const j = Math.floor(R(`aj${i}`) * pieces.length), pr = pieces[j].radius * 0.75;
      const p0 = pieceStates[j].pos.clone().add(new THREE.Vector3((R(`ax${i}`) - 0.5) * 2 * pr, R(`ay${i}`) * pr * 0.8, (R(`az${i}`) - 0.5) * 2 * pr));
      const tRel = S3.dust[0] + sweptAt(p0.x, R(`aw${i}`)) * (S3.dust[1] - S3.dust[0]);
      const dt = t - tRel;
      if (dt < 0 || t < T.boom) { ap.setXYZ(i, 0, -50, 0); ac.setXYZW(i, 0, 0, 0, 0); continue; }
      const sp = 0.5 + R(`as${i}`);
      const wx = S3.wind[0] * sp * (dt + 0.35 * dt * dt), wz = S3.wind[1] * sp * dt;
      const swirl = 0.04 * Math.sin(dt * 2.3 + i) * dt;
      ap.setXYZ(i, p0.x + wx, p0.y + S3.lift * sp * dt + swirl, p0.z + wz + 0.04 * Math.cos(dt * 1.9 + i) * dt);
      const pink = R(`ac${i}`) < 0.75;
      const a = 0.95 * Math.exp(-dt * 0.7) * smooth(0, 0.12, dt);
      ac.setXYZW(i, pink ? 0.95 : 0.55, pink ? 0.8 : 0.05, pink ? 0.76 : 0.08, a);
    }
    ap.needsUpdate = true; ac.needsUpdate = true;
  }

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
  camera.up.set(0, shot.topDown ? 0 : 1, shot.topDown ? -1 : 0); // bird's-eye shots keep the word upright
  camera.lookAt(cl);
  const dip = C.camera.dip;
  let fade = smooth(0, 0.6, t); // first frames rise from black
  for (const sh of shots.slice(1)) { const dd = sh.dip ?? dip, d = Math.abs(t - sh.t0); if (d < dd) fade = Math.min(fade, d / dd); }
  fade = Math.min(fade, 1 - smooth(C.output.durationInSeconds - 0.5, C.output.durationInSeconds, t));
  const focus = cp.distanceTo(shot.focus ? new THREE.Vector3(...shot.focus) : t < T.boom + 1.5 ? (shot === shots[0] ? new THREE.Vector3(0.05, 0.6, 0.3) : headCentre) : new THREE.Vector3(0, 0.15, 0));
  const bloom = C.post.bloom.strength + (bt > 0 ? C.post.bloom.boomFlash * Math.exp(-bt * 6) : 0);

  return (
    <>
      <Env />
      <color attach="background" args={[C.colors.background]} />
      <fogExp2 attach="fog" args={[C.colors.fog, C.cove.fogDensity]} />
      <Cove on={keyOn} />
      {/* omni lights (C4D-style): placed out of shot, only their light is seen */}
      <pointLight position={L.key.position} intensity={L.key.intensity * keyOn} color={C.colors.key} decay={2} castShadow
        shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-bias={-0.0004} shadow-normalBias={0.02} />
      {/* invisible softbox for long glossy highlights on the wet paint (area lights render no geometry) */}
      <rectAreaLight position={L.softbox.position} width={L.softbox.size[0]} height={L.softbox.size[1]} intensity={L.softbox.intensity * keyOn}
        color={C.colors.key} onUpdate={(self: THREE.RectAreaLight) => self.lookAt(...L.softbox.target)} />
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
      <primitive object={ash} />
      <Post focus={focus} aperture={shot.aperture ?? C.post.dof.aperture} bloom={bloom} seed={frame * 0.137} fade={fade} time={t} cam={[cp.x * 0.25 + cp.z * 0.1, cp.y * 0.2]} />
    </>
  );
};

export const PaintedStatue: React.FC = () => {
  const frame = useCurrentFrame();
  const [fontHandle] = useState(() => delayRender("Loading the Cinzel font for ROME"));
  useEffect(() => {
    new FontFace("CinzelLocal", `url(${staticFile(RM.font)})`, { weight: String(RM.weight) }).load()
      .then((f) => { document.fonts.add(f); drawRome(); continueRender(fontHandle); })
      .catch((err) => { console.error(err); drawRome(); continueRender(fontHandle); });
  }, [fontHandle]);
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
