"""Search and download free PBR materials from ambientCG (CC0: free for any use, no sign-up, no credit needed).
  Search:   tools/ai-venv/bin/python scripts/textures/ambientcg.py search "painted bricks" [--limit 12]
  Download: tools/ai-venv/bin/python scripts/textures/ambientcg.py get PaintedBricks001 [--res 2K-JPG]
  Preview:  tools/ai-venv/bin/python scripts/textures/ambientcg.py sheet <out.jpg> ID [ID ...]
Downloads go to tools/textures/<ID>/ (git-ignored) with the maps unzipped: Color, NormalGL, Roughness,
Displacement, AmbientOcclusion (some sets also Metalness/Opacity). Blender wants the NormalGL map.
"""
import argparse, io, json, os, sys, urllib.request, urllib.parse, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEST = os.path.join(ROOT, "tools", "textures")
API = "https://ambientcg.com/api/v2/full_json"
UA = {"User-Agent": "motion-studio-texture-fetch"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def search(q, limit):
    url = f"{API}?type=Material&q={urllib.parse.quote(q)}&limit={limit}&include=downloadData,tagData"
    for a in json.loads(fetch(url)).get("foundAssets", []):
        res = [d["attribute"] for d in a.get("downloadFolders", {}).get("default", {}).get("downloadFiletypeCategories", {}).get("zip", {}).get("downloads", [])]
        print(f"{a['assetId']:<22} {a.get('displayName', ''):<28} tags: {', '.join(a.get('tags', [])[:6])}  sizes: {', '.join(r for r in res if r.endswith('JPG'))}")


def get(asset, res):
    out = os.path.join(DEST, asset); os.makedirs(out, exist_ok=True)
    if any(f.endswith((".jpg", ".png")) for f in os.listdir(out)):
        print("already installed:", out); return out
    data = fetch(f"https://ambientcg.com/get?file={asset}_{res}.zip")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if n.lower().endswith((".jpg", ".png")) and "/" not in n:
                z.extract(n, out)
    with open(os.path.join(out, "LICENSE.txt"), "w") as f:
        f.write(f"{asset} from ambientCG (https://ambientcg.com/a/{asset}), CC0 1.0 Universal: public domain, free for any use.\n")
    print("installed", asset, "->", out); [print("  ", f) for f in sorted(os.listdir(out))]
    return out


def sheet(out, ids):
    from PIL import Image, ImageDraw
    tiles = []
    for a in ids:
        d = os.path.join(DEST, a); col = [f for f in os.listdir(d) if "_Color" in f][0]
        im = Image.open(os.path.join(d, col)).convert("RGB").resize((480, 480)); ImageDraw.Draw(im).text((8, 8), a, fill=(255, 255, 0)); tiles.append(im)
    s = Image.new("RGB", (480 * len(tiles), 480)); [s.paste(t, (i * 480, 0)) for i, t in enumerate(tiles)]; s.save(out); print("sheet", out)


ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["search", "get", "sheet"]); ap.add_argument("args", nargs="+")
ap.add_argument("--limit", type=int, default=12); ap.add_argument("--res", default="2K-JPG")
a = ap.parse_args()
if a.cmd == "search": search(" ".join(a.args), a.limit)
elif a.cmd == "get": [get(x, a.res) for x in a.args]
else: sheet(a.args[0], a.args[1:])
