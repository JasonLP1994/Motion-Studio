// Brush-stroke helper: turns any SVG path into a hand-inked line whose width varies like a pen or brush.
// - closed contours: thicker on the shadow side (normals facing away from the light), plus a slow pressure wobble
// - open strokes (folds, strands): taper to a point at both ends
// Deterministic (seeded noise from the path itself), so every render of a frame is identical.
import React from "react";
import { getLength, getPointAtLength, getTangentAtLength } from "@remotion/paths";

const LIGHT = { x: -0.55, y: -0.83 }; // light from the upper left: the opposite side gets the heavy line
const cache = new Map<string, string>();
// line boil: the ink shimmers on twos like hand-drawn animation (3 states, set once per frame by the film)
let BOIL = 0;
export const setBoil = (frame: number) => { BOIL = Math.floor(frame / 2) % 3; };

const hash = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619); return (h >>> 0) / 4294967296; };

export const brushPath = (d: string, w: number, open = false) => {
  const key = `${BOIL}|${w}|${open ? 1 : 0}|${d}`;
  const hit = cache.get(key); if (hit) return hit;
  let L = 0;
  try { L = getLength(d); } catch { return ""; }
  if (!(L > 0)) return "";
  const n = Math.max(14, Math.min(220, Math.round(L / 5)));
  const seed = hash(d) * 6.283 + BOIL * 1.9;
  const left: string[] = [], right: string[] = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, at = Math.min(L - 0.01, t * L);
    const p = getPointAtLength(d, at), tg = getTangentAtLength(d, at);
    if (!p || !tg) continue;
    const nx = -tg.y, ny = tg.x;                       // normal
    const shadow = 0.42 + 1.15 * Math.max(0, -(nx * LIGHT.x + ny * LIGHT.y)); // heavier facing away from the light
    const pressure = 0.78 + 0.24 * Math.sin(t * 9.4 + seed) + 0.1 * Math.sin(t * 23 + seed * 2);
    const taper = open ? Math.pow(Math.sin(Math.PI * t), 0.7) : 1;
    const hw = (w / 2) * (open ? 1 : shadow) * pressure * taper;
    const j = Math.sin(i * 12.9898 + BOIL * 78.233 + seed) * 0.35 * Math.min(1, w / 6); // tiny positional jitter
    left.push(`${(p.x + nx * (hw + j)).toFixed(2)},${(p.y + ny * (hw + j)).toFixed(2)}`);
    right.push(`${(p.x - nx * (hw - j)).toFixed(2)},${(p.y - ny * (hw - j)).toFixed(2)}`);
  }
  const out = `M${left.join(" L")} L${right.reverse().join(" L")} Z`;
  if (cache.size > 4000) cache.clear();
  cache.set(key, out);
  return out;
};

// <Ink d=... /> draws the inked line for a shape (put it right after the shape's fill)
export const Ink: React.FC<{ d: string; w?: number; open?: boolean; col?: string }> = ({ d, w = 7, open = false, col = "#121733" }) => {
  const b = brushPath(d, w, open);
  return b ? <path d={b} fill={col} stroke="none" /> : null;
};
