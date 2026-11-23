const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1700, height: 3400 } });
  await p.goto('file://' + __dirname + '/decals.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  for (const id of ['A','B','C','D']) await (await p.$('#'+id)).screenshot({ path: __dirname + '/decal_' + id + '.png', omitBackground: true });
  await b.close(); })();
