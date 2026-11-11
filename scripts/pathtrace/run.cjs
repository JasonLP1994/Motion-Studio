// Render one path-traced still: node scripts/pathtrace/run.cjs <shot: macro|break|rome> <spp> <out.png> [extra query]
// Bundles scripts/pathtrace/stills.ts with esbuild, serves it with public/ (models, fonts), runs headless
// Chromium on SwiftShader (no GPU here) and saves the canvas once <spp> samples per pixel have accumulated.
const http = require("http"), fs = require("fs"), path = require("path"), os = require("os");
const { chromium } = require("playwright");
const esbuild = require("esbuild");
const [shot = "macro", spp = "64", out = `pt-${shot}.png`, extra = ""] = process.argv.slice(2);
const root = path.resolve(__dirname, "../.."), pub = path.join(root, "public");
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "pt-"));
esbuild.buildSync({ entryPoints: [path.join(__dirname, "stills.ts")], bundle: true, format: "esm", outfile: path.join(tmp, "bundle.js"), logLevel: "warning" });
fs.writeFileSync(path.join(tmp, "index.html"), '<!doctype html><html><body style="margin:0;background:#000"><script type="module" src="bundle.js"></script></body></html>');
const types = { ".js": "text/javascript", ".html": "text/html", ".ttf": "font/ttf" };
const srv = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split("?")[0]); const f = [path.join(tmp, u === "/" ? "index.html" : u), path.join(pub, u)].find((x) => fs.existsSync(x) && fs.statSync(x).isFile());
  if (!f) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "Content-Type": types[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(r);
});
const stamp = () => new Date().toISOString().slice(11, 19);
srv.listen(0, async () => {
  const b = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on("console", (m) => console.log("console:", m.text().slice(0, 400))); p.on("pageerror", (e) => console.log("pageerror:", e.message.slice(0, 400)));
  await p.goto(`http://localhost:${srv.address().port}/?shot=${shot}&spp=${spp}${extra ? "&" + extra : ""}`);
  await p.waitForFunction("window.ready === true || window.failed", null, { timeout: 0 });
  console.log(stamp(), await p.evaluate("window.log.join('\\n')"));
  if (await p.evaluate("window.failed")) { await b.close(); srv.close(); process.exit(1); }
  const target = Number(spp);
  let done = 0, shotN = 0;
  while (done < target) {
    const n = Math.min(target - done, done < 4 ? 1 : 8);
    console.log(stamp(), await p.evaluate(`window.runSamples(${n})`)); done += n;
    if (done === 1 || done === 16 || done === 64) { await p.locator("canvas").screenshot({ path: out.replace(/\.png$/, `-${done}spp.png`) }); shotN++; }
  }
  await p.locator("canvas").screenshot({ path: out });
  console.log(stamp(), "saved", out);
  await b.close(); srv.close();
});
