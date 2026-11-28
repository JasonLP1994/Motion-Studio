"""Phillips Digital showreel timeline: places the 30 projects on the music's measured hits.
Writes src/showreel/timeline.json (frames at 30 fps), which src/showreel/Showreel.tsx plays.
Edit PROJECTS (names, disciplines, best seconds) or SECTIONS here, then re-run:
  tools/ai-venv/bin/python scripts/showreel/make_timeline.py
Hits come from audio/skinned-audiomachine.mp3 (low-band peaks); re-detect with --detect.
"""
import json, sys, subprocess
import numpy as np

FPS = 30
MUSIC = "audio/skinned-audiomachine.mp3"
# id, conformed file (public/showreel/<file>.mp4), name, discipline, build in-point s, peak in-point s
PROJECTS = [
    ("samurai", "samurai-intro-v3", "SAMURAI INTRO", "3D / CHARACTER", 5.8, 13.8),
    ("statue", "painted-statue-v1", "PAINTED STATUE", "3D / CINEMATIC", 1.0, 13.4),
    ("ooze", "shoe-slime-local-hq-v2", "OOZE", "3D / PRODUCT", 5.0, 18.4),
    ("nightwire", "Nightwire-Visor-Glass-v12", "NIGHTWIRE", "HUD / COMPOSITING", 13.4, 9.4),
    ("preview", "phillips-digital-preview-v2", "SIGNAL PREVIEW", "3D / TYPE", 0.6, 6.4),
    ("novachip", "novachip-v2", "NOVACHIP", "3D / PRODUCT LAUNCH", 3.6, 7.0),
    ("laser", "Laser-Grid-Reveal", "LASER GRID", "3D / SYNTHWAVE", 0.8, 9.8),
    ("lostdata", "lost-data-v1", "LOST DATA", "GLITCH / AUTOMOTIVE", 9.0, 2.6),
    ("redglitch", "red-glitch-v1", "RED GLITCH", "GLITCH / AUTOMOTIVE", 11.0, 4.6),
    ("dance", "dance-break-v1", "DANCE BREAK", "3D / CHARACTER", 2.8, 7.4),
    ("grillz", "grillz-anim-v1", "GRILLZ", "3D / POP ART", 7.6, 3.0),
    ("mutant", "mutant-cover-v1b", "MUTANT COVER", "3D / EDITORIAL", 0.8, 8.4),
    ("pd01", "pd01-v2", "PD-01", "HUD / ANIME TITLES", 10.2, 6.4),
    ("choir", "Signal-Choir-Broadcast", "SIGNAL CHOIR", "ILLUSTRATION / POSTERS", 0.4, 13.0),
    ("kingz", "kingz-v4", "KINGZ", "TYPE / MIXED MEDIA", 7.8, 3.4),
    ("graffiti", "graffiti-flip-v1", "GRAFFITI FLIP", "KINETIC TYPE", 5.0, 2.4),
    ("symbols", "kinetic-symbols-v2", "KINETIC SYMBOLS", "KINETIC TYPE", 0.1, 3.8),
    ("gold", "gold-case-v2", "GOLD CASE", "3D / LIQUID", 8.8, 9.6),
    ("ruby", "rubyred-film-v1", "RUBYRED", "3D / JEWELLERY", 0.2, 11.8),
    ("train", "suno-train-v3", "SUNO TRAIN", "3D / GRAFFITI", 3.4, 14.2),
    ("pixel", "pixel-sneaker-loop-v1", "PIXEL SNEAKER", "PIXEL / LOOP", 6.6, 2.0),
    ("flat", "flat2d-phillips-digital-v11", "FLAT WORLD", "2D / ILLUSTRATION", 4.6, 8.2),
    ("flatred", "flat2d-phillips-digital-v4", "FLAT RED", "2D / ILLUSTRATION", 8.2, 4.6),
    ("popzoom", "popzoom-phillips-digital-v1", "POP ZOOM", "2D / ILLUSTRATION", 9.2, 3.4),
    ("aqua", "Phillips-Digital-Aqua-YouTube", "AQUA", "3D / MASCOT", 1.4, 6.0),
    ("jason", "Jason_Intro_Kinetic_v2", "JASON INTRO", "KINETIC INFOGRAPHICS", 25.0, 40.0),
    ("pe", "phillips-english-intro", "PHILLIPS ENGLISH", "BRAND / TYPE", 0.4, 3.4),
    ("meetings", "PE_Confident_Meetings_1080p", "CONFIDENT MEETINGS", "EDIT / CAPTIONS", 38.2, 53.6),
    ("popout", "popout-lyric-v4", "POP OUT", "LYRIC VIDEO", 9.2, 16.8),
    ("globe", "snow-globe-full-v1", "SNOW GLOBE", "3D / SEASONAL", 4.0, 8.8),
]
P = {p[0]: dict(id=p[0], file=p[1], name=p[2], disc=p[3], build=p[4], peak=p[5], n=i + 1) for i, p in enumerate(PROJECTS)}

SIGNAL = [("preview", 0.4), ("statue", 1.0), ("nightwire", 13.3)]          # slow tease before the drop
BUILD = ["novachip", "laser", "ooze", "lostdata", "pixel", "mutant", "pd01", "dance", "grillz", "choir", "graffiti", "kingz",
         "symbols", "popout", "train", "gold", "ruby", "aqua", "flat", "popzoom", "flatred", "jason", "meetings", "pe"]
BREAK = [("samurai", 5.8), ("globe", 4.0), ("statue", 12.6)]                 # held shots in the quiet section
PEAK = ["redglitch", "dance", "kingz", "mutant", "graffiti", "nightwire", "grillz", "lostdata", "choir", "ooze", "pd01", "laser",
        "symbols", "train", "gold", "novachip", "popout", "ruby", "pixel", "flat", "preview", "aqua", "popzoom", "statue", "flatred",
        "jason", "meetings", "pe", "globe", "choir", "graffiti", "kingz", "mutant", "grillz", "dance", "symbols"]
SEC = dict(boot=0, signal=5.0, drop=11.94, brk=41.0, rebuild=50.0, peak=53.07, hero=71.07, overload=73.8, logo=78.0, end=84.1)


def hits():
    if "--detect" not in sys.argv:
        return [11.94, 12.80, 13.70, 14.24, 15.66, 16.07, 16.56, 17.15, 17.74, 18.48, 19.16, 19.86, 20.57, 21.30, 21.70, 22.41, 22.91,
                23.31, 24.49, 25.12, 25.53, 26.07, 26.49, 27.00, 27.47, 27.96, 28.71, 29.25, 29.77, 30.25, 30.65, 31.18, 31.82, 32.22,
                32.65, 33.48, 34.01, 34.54, 35.24, 35.77, 36.30, 36.70, 37.18, 38.06, 38.60, 39.00, 39.48, 40.19, 40.89, 53.07, 53.60,
                54.12, 54.65, 55.19, 56.07, 56.59, 57.31, 57.83, 58.37, 58.89, 59.29, 59.78, 60.29, 61.18, 61.71, 62.25, 63.12, 63.66,
                64.54, 65.24, 65.95, 66.66, 67.35, 68.07, 68.78, 69.30, 71.07, 71.47, 71.95, 72.47]
    from scipy import signal
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", MUSIC, "-ac", "1", "-ar", "11025", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); sr = 11025
    lo = signal.sosfilt(signal.butter(4, 150, "low", fs=sr, output="sos"), x); e = np.convolve(lo ** 2, np.ones(int(sr * 0.05)), "same")
    pk, _ = signal.find_peaks(e, distance=int(sr * 0.4), height=e.max() * 0.35)
    return [round(p / sr, 2) for p in pk]


F = lambda t: int(round(t * FPS))
H = hits(); clips = []


def add(pid, a, b, src_in, section, tag=True):
    a, b = int(a), int(b)
    clips.append(dict(project=pid, file=P[pid]["file"], n=P[pid]["n"], name=P[pid]["name"], disc=P[pid]["disc"],
                      from_=a, dur=b - a, srcIn=F(src_in), section=section, tag=tag))


# signal: three slow tease shots, 6-frame dip to black before the drop
s0, s1 = F(SEC["signal"]), F(SEC["drop"]) - 6
edges = np.linspace(s0, s1, len(SIGNAL) + 1).round().astype(int)
for (pid, t), a, b in zip(SIGNAL, edges, edges[1:]): add(pid, a, b, t, "signal")
# build: cut on every second hit from the drop to the breakdown
bh = [F(h) for h in H if SEC["drop"] - 0.01 <= h < SEC["brk"]][::2]
assert len(bh) >= len(BUILD), (len(bh), len(BUILD))
bh = bh[:len(BUILD)] + [F(SEC["brk"])]                                      # last build shot runs to the breakdown
for pid, a, b in zip(BUILD, bh, bh[1:]): add(pid, a, b, P[pid]["build"], "build")
# breakdown: three held shots, then the rebuild glitch shot
edges = np.linspace(F(SEC["brk"]), F(SEC["rebuild"]), len(BREAK) + 1).round().astype(int)
for (pid, t), a, b in zip(BREAK, edges, edges[1:]): add(pid, a, b, t, "break")
add("redglitch", F(SEC["rebuild"]), F(SEC["peak"]) - 12, P["redglitch"]["build"], "rebuild")
# peak: a cut on every hit, samurai hero bang lands on the big hit
ph = [F(h) for h in H if SEC["peak"] - 0.01 <= h < SEC["hero"]] + [F(SEC["hero"])]
for pid, a, b in zip(PEAK, ph, ph[1:]): add(pid, a, b, P[pid]["peak"], "peak", tag=False)
add("samurai", F(SEC["hero"]), F(SEC["overload"]), P["samurai"]["peak"], "hero")
# overload: 2-3 frame flashes through the archive, accelerating, then black
f, k, order = F(SEC["overload"]), 0, [p[0] for p in PROJECTS]
while f < F(SEC["logo"]) - 8:
    d = 4 if f < F(SEC["overload"]) + 45 else (3 if f < F(SEC["overload"]) + 90 else 2)
    pid = order[(k * 7) % 30]; add(pid, f, f + d, P[pid]["peak"] + 0.3, "overload", tag=False); f += d; k += 1

out = dict(fps=FPS, total=F(SEC["end"]), sections={k: F(v) for k, v in SEC.items()}, projects=len(PROJECTS),
           clips=[{("from" if k == "from_" else k): v for k, v in c.items()} for c in clips], hits=[F(h) for h in H])
json.dump(out, open("src/showreel/timeline.json", "w"), indent=1)
shown = {c["project"] for c in clips}
print(f"{len(clips)} clips, {len(shown)}/30 projects, total {out['total']} frames; build slots {len(bh) - 1}, peak slots {len(ph) - 1}")
missing = set(P) - shown
if missing: print("missing:", missing)
