// Run first: node scripts/blender/make_glyph_atlas.cjs  (writes public/philips/glyphs.png, used by phillips_ident.py)
// 16x16 glyph atlas (white on black) for the code rain: digits, hex, brackets and symbols in Liberation Mono Bold.
const { chromium } = require("playwright"); const fs = require("fs");
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const font = fs.readFileSync(require("path").join(__dirname, "../../public/fonts/LiberationMono-Bold.ttf")).toString("base64");
  const png = await p.evaluate(async (font) => {
    const f = new FontFace("Mono", `url(data:font/ttf;base64,${font})`); await f.load(); document.fonts.add(f);
    const chars = "0123456789ABCDEF<>/\\{}[]()=+*#$%&;:.,!?^~|_-@pdPD01".split("");
    const c = document.createElement("canvas"); c.width = c.height = 1024; const g = c.getContext("2d");
    g.fillStyle = "#000"; g.fillRect(0, 0, 1024, 1024); g.fillStyle = "#fff"; g.textAlign = "center"; g.textBaseline = "middle"; g.font = "52px Mono";
    for (let i = 0; i < 256; i++) { const x = (i % 16) * 64 + 32, y = Math.floor(i / 16) * 64 + 34; const ch = chars[(i * 7 + (i >> 4)) % chars.length]; g.save(); if (i % 5 === 0) { g.translate(x, y); g.scale(-1, 1); g.fillText(ch, 0, 0); } else g.fillText(ch, x, y); g.restore(); }
    return c.toDataURL("image/png");
  }, font);
  fs.writeFileSync(require("path").join(__dirname, "../../public/philips/glyphs.png"), Buffer.from(png.split(",")[1], "base64")); await b.close(); console.log("ok");
})();
