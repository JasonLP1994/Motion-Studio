// CultureJacked "CONTENT HOUSE" tee graphic. Hand-built SVG, rendered to a
// transparent 4500x5400 PNG with Playwright. All words and colours live in CONFIG.
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('playwright');
import fs from 'node:fs';
import path from 'node:path';

const CONFIG = {
  top: '10 DOWNING STREET',
  head1: 'CONTENT',
  head2: 'HOUSE',
  bottom: 'LESS GOVERNING. MORE CONTENT.',
  badge: 'VERIFIED',
  flags: ['LIVE', '10TV', 'POD'],
  red: '#C8102E',
  navy: '#14234B',
  cream: '#F3E6C8',
  ink: '#0B0B0D',
  out: process.argv[2] || 'renders/tshirt/content-house_raw.png',
};
const {red: R, navy: N, cream: C, ink: K} = CONFIG;
const fontUrl = 'file://' + path.resolve('public/fonts/anton-latin-400-normal.woff2');
const serifUrl = 'file://' + path.resolve('public/fonts/Cinzel.ttf');

// deterministic random
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

const burst = (cx, cy, r1, r2, n, rot = 0, jitter = 0) => {
  let d = '';
  for (let i = 0; i < n * 2; i++) {
    const a = rot + (i / (n * 2)) * Math.PI * 2;
    const r = (i % 2 ? r1 : r2) * (1 + (rnd() - 0.5) * jitter);
    d += `${i ? 'L' : 'M'}${(cx + Math.cos(a) * r).toFixed(1)} ${(cy + Math.sin(a) * r).toFixed(1)}`;
  }
  return d + 'Z';
};
const roughCircle = (cx, cy, r, n = 180, amp = 6) => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rr = r + (rnd() - 0.5) * amp + (i % 23 === 0 ? -amp * 2.2 : 0);
    d += `${i ? 'L' : 'M'}${(cx + Math.cos(a) * rr).toFixed(1)} ${(cy + Math.sin(a) * rr).toFixed(1)}`;
  }
  return d + 'Z';
};
// outlined tube (arms, sleeves, poles)
const tube = (d, w, fill, ow = 9) =>
  `<path d="${d}" fill="none" stroke="${K}" stroke-width="${w + ow * 2}" stroke-linecap="round" stroke-linejoin="round"/>` +
  `<path d="${d}" fill="none" stroke="${fill}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
const flash = (x, y, s) =>
  `<g transform="translate(${x} ${y}) scale(${s})"><path d="${burst(0, 0, 22, 70, 9, rnd())}" fill="${C}" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>` +
  `<path d="${burst(0, 0, 10, 30, 9, rnd())}" fill="${R}"/></g>`;

// a hand holding a phone up to film, screen toward viewer (local origin = phone centre)
const phoneHand = (x, y, rot, s, label = 'REC', sleeve = N) => `
<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
  ${tube('M0 150 L0 250', 92, sleeve)}
  <rect x="-52" y="118" width="104" height="36" rx="6" fill="${C}" stroke="${K}" stroke-width="7"/>
  <path d="M-58 40 C-64 92 -42 128 0 132 C42 130 62 98 58 52 L56 36 Z" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M-30 100 C-10 112 14 112 32 100" fill="none" stroke="${K}" stroke-width="4"/>
  <rect x="-50" y="-92" width="100" height="184" rx="16" fill="${K}" stroke="${K}" stroke-width="7"/>
  <rect x="-41" y="-80" width="82" height="160" rx="9" fill="${C}"/>
  <rect x="-41" y="40" width="82" height="40" fill="url(#dotN)"/>
  <circle cx="-22" cy="-58" r="8" fill="${R}"/>
  <text x="-8" y="-49" font-family="Anton" font-size="24" fill="${K}">${label}</text>
  <path d="M0 -8 C-14 -26 -38 -10 -22 8 L0 28 L22 8 C38 -10 14 -26 0 -8Z" fill="${R}" stroke="${K}" stroke-width="5"/>
  <ellipse cx="52" cy="-28" rx="17" ry="13" fill="${C}" stroke="${K}" stroke-width="6"/>
  <ellipse cx="54" cy="-2" rx="17" ry="13" fill="${C}" stroke="${K}" stroke-width="6"/>
  <ellipse cx="54" cy="24" rx="17" ry="13" fill="${C}" stroke="${K}" stroke-width="6"/>
  <ellipse cx="-50" cy="14" rx="14" ry="30" transform="rotate(-14 -50 14)" fill="${C}" stroke="${K}" stroke-width="6"/>
</g>`;

const mic = (x, y, rot, label, flagCol) => `
<g transform="translate(${x} ${y}) rotate(${rot})">
  ${tube('M0 40 L0 420', 30, K, 7)}
  <path d="M-14 60 L14 60 L10 90 L-10 90Z" fill="${C}" stroke="${K}" stroke-width="5"/>
  <circle cx="0" cy="0" r="46" fill="${N}" stroke="${K}" stroke-width="8"/>
  <clipPath id="mc${label}"><circle cx="0" cy="0" r="42"/></clipPath>
  <g clip-path="url(#mc${label})" stroke="${C}" stroke-width="3" opacity="1">
    ${[-36, -24, -12, 0, 12, 24, 36].map((v) => `<line x1="${v}" y1="-50" x2="${v + 20}" y2="50"/><line x1="${v}" y1="-50" x2="${v - 20}" y2="50"/>`).join('')}
  </g>
  <path d="M-30 -24 C-20 -38 0 -42 14 -38" fill="none" stroke="${C}" stroke-width="7" stroke-linecap="round"/>
  <g transform="translate(0 112)">
    <path d="M-48 -40 L48 -40 L48 40 L-48 40Z" fill="${flagCol}" stroke="${K}" stroke-width="8"/>
    <path d="M48 -40 L66 -54 L66 26 L48 40Z" fill="${K}" stroke="${K}" stroke-width="6"/>
    <path d="M-48 -40 L-30 -54 L66 -54 L48 -40Z" fill="${C}" stroke="${K}" stroke-width="6"/>
    <text x="0" y="17" text-anchor="middle" font-family="Anton" font-size="46" fill="${flagCol === C ? K : C}">${label}</text>
  </g>
</g>`;

// --- Burnham caricature, local origin = bridge of nose. Global placement via translate.
const burnham = `
<g id="burnham" transform="translate(640 590)">
  <!-- body -->
  <path d="M-70 270 C-160 300 -250 330 -285 420 L-310 760 L310 760 L285 420 C250 330 160 300 70 270Z" fill="${N}" stroke="${K}" stroke-width="10" stroke-linejoin="round"/>
  <path d="M-285 430 C-260 520 -255 640 -262 760 M285 430 C262 520 255 640 262 760" fill="none" stroke="${K}" stroke-width="6"/>
  <rect x="-300" y="460" width="600" height="300" fill="url(#hatchK)" clip-path="url(#bodyClip)"/>
  <path d="M-72 270 L0 500 L72 270Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <!-- lapels -->
  <path d="M-72 272 L-150 330 L-95 400 L-130 430 L0 640 Z" fill="${N}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M72 272 L150 330 L95 400 L130 430 L0 640 Z" fill="${N}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M-128 340 L-100 395 M128 340 L100 395" stroke="${C}" stroke-width="4"/>
  <!-- tie, loosened -->
  <path d="M-28 318 L26 312 L18 352 L-16 356Z" fill="${R}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M-16 354 L18 350 L52 560 L22 610 L-6 560Z" fill="${R}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M-8 400 L30 380 M-2 450 L40 428 M6 500 L46 478" stroke="${C}" stroke-width="7"/>
  <!-- open collar -->
  <path d="M-72 268 L-40 340 L-4 312 L-58 240Z" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M72 268 L44 336 L6 310 L58 240Z" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <!-- neck -->
  <path d="M-62 200 L-66 290 C-30 315 30 315 66 290 L62 200Z" fill="${C}" stroke="${K}" stroke-width="8"/>
  <path d="M-62 236 C-20 272 30 272 64 236 L64 296 C30 315 -30 315 -66 290Z" fill="url(#dotR)"/>
  <!-- ears -->
  <path d="M-130 -18 C-176 -40 -186 40 -162 78 C-148 100 -128 96 -124 74Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M-142 6 C-160 10 -160 50 -146 66" fill="none" stroke="${K}" stroke-width="5"/>
  <path d="M134 -18 C180 -40 190 40 166 78 C152 100 132 96 128 74Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M146 6 C164 10 164 50 150 66" fill="none" stroke="${K}" stroke-width="5"/>
  <!-- face: long, strong squared chin -->
  <path id="faceP" d="M-138 -70 C-144 10 -136 90 -116 150 C-96 212 -60 256 -24 268 L32 268 C70 256 106 212 124 150 C144 90 148 10 140 -70 C130 -130 -130 -130 -138 -70Z" fill="${C}" stroke="${K}" stroke-width="10" stroke-linejoin="round"/>
  <clipPath id="faceClip"><use href="#faceP"/></clipPath>
  <g clip-path="url(#faceClip)">
    <!-- shadow side + jaw (red halftone), deep shadow (navy halftone) -->
    <path d="M88 -80 C110 0 112 90 92 160 C74 216 40 250 10 266 L160 300 L160 -100Z" fill="url(#dotR)"/>
    <path d="M118 -40 C132 40 128 120 104 186 L170 200 L170 -60Z" fill="url(#dotN)"/>
    <path d="M-120 196 C-80 250 -30 262 0 262 C40 262 80 240 110 196 L120 300 L-120 300Z" fill="url(#dotR)"/>
    <ellipse cx="-96" cy="96" rx="38" ry="26" fill="url(#dotRL)"/>
    <ellipse cx="100" cy="96" rx="38" ry="26" fill="url(#dotRL)"/>
    <path d="M-150 -82 C-60 -64 60 -64 150 -82 L150 -40 C60 -26 -60 -26 -150 -40Z" fill="url(#dotR)" opacity="1"/>
  </g>
  <!-- forehead lines (eyebrows raised) -->
  <path d="M-70 -64 C-30 -74 26 -74 70 -64" fill="none" stroke="${K}" stroke-width="5" stroke-linecap="round"/>
  <path d="M-50 -46 C-20 -54 22 -54 52 -46" fill="none" stroke="${K}" stroke-width="4" stroke-linecap="round"/>
  <!-- hair: salt-and-pepper, swept from a side parting -->
  <g transform="translate(0 -60) scale(1 0.8) translate(0 60)">
  <path d="M-146 -20 C-162 -100 -140 -168 -70 -196 C0 -222 104 -210 148 -150 C168 -118 162 -64 148 -26 L136 -58 C128 -92 100 -110 60 -112 C10 -114 -50 -122 -96 -104 C-120 -92 -130 -66 -134 -26Z" fill="${C}" stroke="${K}" stroke-width="10" stroke-linejoin="round"/>
  <path d="M-62 -196 C-10 -232 120 -230 160 -160 C150 -176 110 -186 70 -178 C110 -160 130 -140 138 -112 C112 -150 40 -170 -40 -150 C-56 -170 -62 -184 -62 -196Z" fill="${C}" stroke="${K}" stroke-width="9" stroke-linejoin="round"/>
  <path d="M-146 -20 C-162 -100 -140 -168 -70 -196 L-60 -150 C-100 -130 -128 -90 -134 -26Z" fill="url(#dotN)"/>
  <path d="M136 -58 C128 -92 100 -110 60 -112 C100 -130 136 -120 156 -96 C156 -80 152 -64 148 -26Z" fill="url(#dotN)"/>
  <g fill="none" stroke="${K}" stroke-width="4.5" stroke-linecap="round">
    <path d="M-60 -150 C-20 -168 60 -170 120 -140"/><path d="M-50 -132 C0 -146 70 -146 128 -118"/>
    <path d="M-100 -150 C-110 -130 -122 -100 -128 -60"/><path d="M-80 -174 C-110 -160 -130 -120 -138 -80"/>
    <path d="M10 -196 C60 -204 110 -196 140 -170"/><path d="M-30 -186 C10 -200 50 -200 90 -192"/>
    <path d="M-60 -150 L-66 -196" stroke-width="6"/>
  </g>
  </g>
  <!-- eyebrows: heavy, dark, raised -->
  <path d="M-116 -20 C-96 -54 -58 -64 -20 -56 L-18 -34 C-56 -42 -88 -32 -112 -4Z" fill="${K}"/>
  <path d="M20 -56 C58 -64 98 -54 122 -22 L116 -4 C92 -32 58 -42 22 -34Z" fill="${K}"/>
  <!-- eyes: hooded, squinting into the grin, glancing at the phone -->
  <path d="M-96 6 C-80 -12 -46 -12 -30 4 C-46 14 -80 14 -96 6Z" fill="${C}" stroke="${K}" stroke-width="5"/>
  <path d="M30 4 C46 -12 80 -12 96 6 C80 14 46 14 30 4Z" fill="${C}" stroke="${K}" stroke-width="5"/>
  <circle cx="-72" cy="2" r="10" fill="${K}"/><circle cx="54" cy="2" r="10" fill="${K}"/>
  <circle cx="-75" cy="-1" r="3" fill="${C}"/><circle cx="51" cy="-1" r="3" fill="${C}"/>
  <path d="M-100 8 C-84 -16 -44 -16 -26 4" fill="none" stroke="${K}" stroke-width="11" stroke-linecap="round"/>
  <path d="M26 4 C44 -16 84 -16 100 8" fill="none" stroke="${K}" stroke-width="11" stroke-linecap="round"/>
  <path d="M-102 -8 C-84 -30 -44 -30 -24 -12" fill="none" stroke="${K}" stroke-width="4.5"/>
  <path d="M24 -12 C44 -30 84 -30 102 -8" fill="none" stroke="${K}" stroke-width="4.5"/>
  <path d="M-92 18 C-74 30 -50 30 -34 18 M34 18 C50 30 74 30 92 18" fill="none" stroke="${K}" stroke-width="4"/>
  <path d="M-104 0 L-122 -8 M-106 10 L-124 14 M-102 20 L-116 32 M104 0 L122 -8 M106 10 L124 14 M102 20 L116 32" stroke="${K}" stroke-width="4" stroke-linecap="round"/>
  <!-- nose: long, straight -->
  <path d="M6 -26 C18 20 26 52 34 74 C40 92 26 104 10 100 C2 108 -18 106 -24 94 C-34 84 -26 72 -16 70" fill="none" stroke="${K}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 6 C20 40 30 62 34 74 C30 70 22 74 18 84 L18 20Z" fill="url(#dotR)"/>
  <circle cx="-8" cy="92" r="5" fill="${K}"/><circle cx="16" cy="92" r="5" fill="${K}"/>
  <!-- smile creases -->
  <path d="M-30 86 C-66 98 -90 112 -98 132" fill="none" stroke="${K}" stroke-width="7" stroke-linecap="round"/>
  <path d="M36 86 C72 98 96 112 104 130" fill="none" stroke="${K}" stroke-width="7" stroke-linecap="round"/>
  <!-- wide camera-ready grin -->
  <path d="M-90 132 C-50 124 56 124 96 130 C84 168 46 186 3 186 C-40 186 -78 168 -90 132Z" fill="${K}"/>
  <path d="M-80 134 C-40 128 46 128 86 133 C82 154 -76 156 -80 134Z" fill="${C}"/>
  <path d="M-46 172 C-20 160 24 160 50 172 C30 182 -26 182 -46 172Z" fill="${R}"/>
  <g stroke="${K}" stroke-width="4"><line x1="-52" y1="131" x2="-51" y2="151"/><line x1="-24" y1="130" x2="-23" y2="153"/><line x1="4" y1="130" x2="4" y2="154"/><line x1="32" y1="130" x2="32" y2="153"/><line x1="60" y1="131" x2="59" y2="151"/></g>
  <path d="M-90 132 C-50 124 56 124 96 130 C84 168 46 186 3 186 C-40 186 -78 168 -90 132Z" fill="none" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M-102 122 C-110 134 -108 146 -100 152 M106 120 C114 132 112 144 104 150" fill="none" stroke="${K}" stroke-width="6" stroke-linecap="round"/>
  <path d="M-44 204 C-16 214 22 214 50 204" fill="none" stroke="${K}" stroke-width="5" stroke-linecap="round"/>
  <path d="M-46 240 C-20 254 26 254 50 240" fill="none" stroke="${K}" stroke-width="4" stroke-linecap="round"/>
  <path d="M0 250 C3 258 7 258 9 250" fill="none" stroke="${K}" stroke-width="4" stroke-linecap="round"/>
</g>`;

// selfie arm (his right, viewer's left) and peace arm (his left, viewer's right), in scene coords
const selfieArm = `
  ${tube('M300 334 L332 690', 12, C, 7)}
  <g transform="translate(296 262) rotate(-8)">
    <rect x="-30" y="58" width="60" height="22" fill="${K}"/>
    <rect x="-58" y="-104" width="116" height="200" rx="18" fill="${K}" stroke="${C}" stroke-width="6"/>
    <rect x="-40" y="-86" width="52" height="64" rx="12" fill="${N}" stroke="${C}" stroke-width="4"/>
    <circle cx="-26" cy="-70" r="10" fill="${K}" stroke="${C}" stroke-width="4"/><circle cx="-2" cy="-70" r="10" fill="${K}" stroke="${C}" stroke-width="4"/><circle cx="-26" cy="-40" r="10" fill="${K}" stroke="${C}" stroke-width="4"/>
    <circle cx="0" cy="-40" r="5" fill="${C}"/>
    <path d="M-30 40 L30 0 M-30 60 L30 20" stroke="${C}" stroke-width="3"/>
  </g>
  ${tube('M410 960 L300 870 L334 720', 96, N)}
  <rect x="290" y="760" width="90" height="34" rx="6" transform="rotate(8 335 777)" fill="${C}" stroke="${K}" stroke-width="7"/>
  <path d="M296 660 C290 700 300 748 336 756 C372 760 384 724 378 690 C374 664 348 650 322 652 Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M300 684 C326 678 352 680 376 690 M300 712 C326 706 352 708 378 716 M304 738 C330 732 352 734 372 742" fill="none" stroke="${K}" stroke-width="5" stroke-linecap="round"/>`;

const peaceArm = `
  ${tube('M880 990 L1010 900 L1052 770', 96, N)}
  <rect x="1006" y="740" width="96" height="34" rx="6" transform="rotate(14 1054 757)" fill="${C}" stroke="${K}" stroke-width="7"/>
  <g transform="translate(1062 690) rotate(14)">
    <path d="M-34 -98 C-46 -100 -52 -90 -48 -76 L-36 -10 L-6 -14 L-20 -88 C-22 -96 -28 -99 -34 -98Z" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M18 -102 C8 -104 0 -96 2 -82 L4 -14 L32 -12 L32 -86 C32 -96 26 -102 18 -102Z" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M-46 -20 C-52 20 -40 54 -4 60 C30 64 50 44 50 10 C50 -10 44 -22 30 -22 L-40 -24Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M-30 0 C-10 -8 14 -8 40 0 M-26 22 C-6 16 18 16 42 24" fill="none" stroke="${K}" stroke-width="5" stroke-linecap="round"/>
    <path d="M-44 -6 C-60 10 -40 34 -14 24" fill="${C}" stroke="${K}" stroke-width="6"/>
    <path d="M20 30 C30 40 40 40 46 30" fill="url(#dotR)"/>
  </g>`;

// Number 10 door, right of centre, behind Burnham
const door = `
<g id="door" transform="translate(40 0)">
  <rect x="700" y="300" width="56" height="840" fill="${C}" stroke="${K}" stroke-width="9"/>
  <rect x="1044" y="300" width="56" height="840" fill="${C}" stroke="${K}" stroke-width="9"/>
  <rect x="700" y="300" width="56" height="840" fill="url(#dotN)"/>
  <path d="M700 300 L700 286 L1100 286 L1100 300" fill="${C}" stroke="${K}" stroke-width="9"/>
  <path d="M756 300 A144 144 0 0 1 1044 300 Z" fill="${C}" stroke="${K}" stroke-width="9"/>
  <path d="M780 300 A120 120 0 0 1 1020 300 Z" fill="${K}"/>
  <g stroke="${C}" stroke-width="5">${[0.12, 0.26, 0.4, 0.5, 0.6, 0.74, 0.88].map((t) => { const a = Math.PI * (1 + t); return `<line x1="900" y1="300" x2="${(900 + Math.cos(a) * 118).toFixed(1)}" y2="${(300 + Math.sin(a) * 118).toFixed(1)}"/>`; }).join('')}</g>
  <path d="M840 300 A60 60 0 0 1 960 300" fill="none" stroke="${C}" stroke-width="5"/>
  <rect x="756" y="300" width="288" height="840" fill="${K}" stroke="${K}" stroke-width="9"/>
  <g fill="none" stroke="${C}" stroke-width="5">
    <rect x="782" y="330" width="236" height="150"/><rect x="782" y="510" width="104" height="250"/><rect x="914" y="510" width="104" height="250"/>
    <rect x="782" y="790" width="104" height="300"/><rect x="914" y="790" width="104" height="300"/>
  </g>
  <text x="900" y="452" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="104" fill="${C}">10</text>
  <circle cx="900" cy="560" r="30" fill="${C}" stroke="${K}" stroke-width="5"/>
  <path d="M888 552 L894 548 L898 556 M912 552 L906 548 L902 556 M892 572 C898 578 904 578 910 572" fill="none" stroke="${K}" stroke-width="4"/>
  <path d="M876 590 C876 616 924 616 924 590" fill="none" stroke="${C}" stroke-width="8"/>
</g>`;

const ringLight = `
<g id="ring">
  <circle cx="640" cy="560" r="236" fill="none" stroke="${K}" stroke-width="66"/>
  <circle cx="640" cy="560" r="236" fill="none" stroke="${C}" stroke-width="44"/>
  <circle cx="640" cy="560" r="236" fill="none" stroke="${K}" stroke-width="5" stroke-dasharray="3 22"/>
</g>`;

const boomMic = `
  ${tube('M1440 96 L740 236', 16, C, 7)}
  <g transform="translate(650 250) rotate(-10)">
    <path d="${burst(0, 0, 44, 54, 40, 0, 0.25).replace(/Z$/, '')}Z" transform="scale(2.1 1)" fill="${N}" stroke="${K}" stroke-width="5" stroke-linejoin="round"/>
    <ellipse cx="0" cy="0" rx="80" ry="30" fill="url(#hatchC)"/>
    <path d="M-60 -22 C-30 -34 20 -34 50 -26" fill="none" stroke="${C}" stroke-width="6" stroke-linecap="round"/>
  </g>`;

const pressCamera = (x, y, rot) => `
<g transform="translate(${x} ${y}) rotate(${rot})">
  ${tube('M60 70 L130 260', 84, R)}
  <rect x="-24" y="-150" width="22" height="90" fill="${K}"/>
  <path d="M-70 -210 C-50 -150 30 -150 50 -210Z" fill="${C}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M-48 -200 C-30 -168 12 -168 28 -200" fill="url(#dotN)"/>
  <rect x="-110" y="-70" width="200" height="130" rx="14" fill="${K}" stroke="${C}" stroke-width="6"/>
  <rect x="-90" y="-92" width="70" height="26" rx="4" fill="${K}" stroke="${C}" stroke-width="5"/>
  <circle cx="-14" cy="-4" r="56" fill="${N}" stroke="${C}" stroke-width="7"/>
  <circle cx="-14" cy="-4" r="34" fill="${K}" stroke="${C}" stroke-width="5"/>
  <circle cx="-26" cy="-16" r="10" fill="${C}"/>
  <rect x="-100" y="-56" width="30" height="100" fill="url(#hatchC)"/>
</g>`;

const unionJack = `
<g id="flagDisc">
  <clipPath id="discClip"><path d="${roughCircle(750, 640, 500, 200, 10)}"/></clipPath>
  <path d="${roughCircle(750, 640, 528, 200, 12)}" fill="${C}" stroke="${K}" stroke-width="10"/>
  <g clip-path="url(#discClip)">
    <g transform="rotate(-9 750 640)">
      <rect x="150" y="40" width="1200" height="1200" fill="${N}"/>
      <path d="M150 140 L1350 1140 M150 1140 L1350 140" stroke="${C}" stroke-width="190"/>
      <path d="M150 116 L750 616 M1350 1164 L750 664 M150 1164 L726 640 M1350 116 L774 640" stroke="${R}" stroke-width="62"/>
      <rect x="150" y="530" width="1200" height="220" fill="${C}"/>
      <rect x="640" y="40" width="220" height="1200" fill="${C}"/>
      <rect x="150" y="572" width="1200" height="136" fill="${R}"/>
      <rect x="682" y="40" width="136" height="1200" fill="${R}"/>
    </g>
    <!-- halftone vignette to the rim and worn print -->
    <path d="${roughCircle(750, 640, 600, 60, 0)} M750 140 m0 0" fill="none"/>
    <circle cx="750" cy="640" r="560" fill="none" stroke="url(#dotNL)" stroke-width="200"/>
    <circle cx="750" cy="640" r="430" fill="none" stroke="url(#dotN)" stroke-width="60"/>
  </g>
  <path d="${roughCircle(750, 640, 500, 200, 10)}" fill="none" stroke="${K}" stroke-width="12"/>
</g>`;

const hearts = [[1170, 590, 1.0], [1130, 500, 0.7]].map(([x, y, s]) =>
  `<path transform="translate(${x} ${y}) scale(${s})" d="M0 -12 C-20 -40 -58 -16 -34 14 L0 44 L34 14 C58 -16 20 -40 0 -12Z" fill="${R}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>`).join('');

const liveBadge = `
<g transform="translate(430 380) rotate(-10)">
  <rect x="-92" y="-38" width="184" height="76" rx="12" fill="${R}" stroke="${K}" stroke-width="9"/>
  <circle cx="-52" cy="0" r="15" fill="${C}"/>
  <text x="18" y="22" text-anchor="middle" font-family="Anton" font-size="60" fill="${C}">LIVE</text>
</g>`;

const verified = `
<g transform="translate(890 770) rotate(-8)">
  <path d="${burst(0, 0, 50, 62, 14, 0)}" fill="${C}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="${burst(0, 0, 40, 50, 14, 0)}" fill="${N}"/>
  <path d="M-20 0 L-5 16 L22 -14" fill="none" stroke="${C}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="0" y="96" text-anchor="middle" font-family="Anton" font-size="30" fill="${C}" stroke="${K}" stroke-width="8" paint-order="stroke" letter-spacing="2">${CONFIG.badge}</text>
</g>`;

const scene = `
<g id="scene" transform="translate(750 650) scale(0.95) translate(-750 -640)">
  <path d="${burst(750, 640, 560, 690, 30, 0.1, 0.12)}" fill="${C}" stroke="${K}" stroke-width="10" stroke-linejoin="round"/>
  <path d="${burst(750, 640, 530, 650, 30, 0.1, 0.0)}" fill="${R}"/>
  <path d="${burst(750, 640, 530, 650, 30, 0.1, 0.0)}" fill="url(#dotNL)" clip-path="url(#outerBurst)"/>
  ${unionJack}
  ${door}
  ${ringLight}
  ${boomMic}
  ${burnham}
  ${mic(520, 900, 16, CONFIG.flags[0], R)}
  ${mic(790, 905, -16, CONFIG.flags[2], N)}
  ${mic(655, 935, 0, CONFIG.flags[1], C)}
  ${selfieArm}
  ${peaceArm}
  ${phoneHand(150, 640, 22, 1.0, 'REC', R)}
  ${phoneHand(230, 990, 34, 0.95, 'LIVE', N)}
  ${phoneHand(1330, 430, -24, 1.0, 'REC', N)}
  ${phoneHand(1340, 790, -30, 0.95, 'LIVE', R)}
  ${pressCamera(1180, 1060, -32)}
  ${hearts}
  ${liveBadge}
  ${verified}
  ${flash(220, 400, 1.0)}
  ${flash(1270, 240, 1.2)}
  ${flash(330, 1100, 0.8)}
</g>`;

// headline blocks; positioned by the fitter at runtime (data-fit = x y w h)
const headline = (txt, y, h) => `
<g data-fit="110 ${y} 1280 ${h}">
  <text font-family="Anton" font-size="300" fill="${K}" stroke="${K}" stroke-width="34" stroke-linejoin="round" transform="translate(22 22)">${txt}</text>
  <text font-family="Anton" font-size="300" fill="${R}" stroke="${R}" stroke-width="10" stroke-linejoin="round" transform="translate(16 16)">${txt}</text>
  <text font-family="Anton" font-size="300" fill="${R}" stroke="${K}" stroke-width="22" stroke-linejoin="round" paint-order="stroke" transform="translate(16 16)">${txt}</text>
  <text font-family="Anton" font-size="300" fill="${C}" stroke="${K}" stroke-width="16" stroke-linejoin="round" paint-order="stroke">${txt}</text>
  <text font-family="Anton" font-size="300" fill="url(#dotNH)" clip-path="url(#lowerHalf)">${txt}</text>
</g>`;

const tornStrip = (y, h, fill, tilt) => {
  let top = '', bot = '';
  const x0 = 140, x1 = 1360;
  let d = `M${x0} ${y}`;
  for (let x = x0; x <= x1; x += 40) d += ` L${x} ${y + (rnd() - 0.5) * 6}`;
  for (let yy = y; yy <= y + h; yy += 14) d += ` L${x1 + (rnd() * 18)} ${yy}`;
  for (let x = x1; x >= x0; x -= 40) d += ` L${x} ${y + h + (rnd() - 0.5) * 6}`;
  for (let yy = y + h; yy >= y; yy -= 14) d += ` L${x0 - (rnd() * 18)} ${yy}`;
  return `<path d="${d}Z" transform="rotate(${tilt} 750 ${y + h / 2})" fill="${fill}" stroke="${K}" stroke-width="10" stroke-linejoin="round"/>`;
};

const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1800" viewBox="0 0 1500 1800">
<defs>
  <pattern id="dotR" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="5.5" cy="5.5" r="2.6" fill="${R}"/></pattern>
  <pattern id="dotRL" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="5.5" cy="5.5" r="3.8" fill="${R}"/></pattern>
  <pattern id="dotN" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="5.5" cy="5.5" r="2.7" fill="${N}"/></pattern>
  <pattern id="dotNL" width="13" height="13" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="6.5" cy="6.5" r="4.4" fill="${N}"/></pattern>
  <pattern id="dotNH" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="6" cy="6" r="3.2" fill="${R}"/></pattern>
  <pattern id="hatchK" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><line x1="0" y1="0" x2="0" y2="14" stroke="${K}" stroke-width="4"/></pattern>
  <pattern id="hatchC" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><line x1="0" y1="0" x2="0" y2="12" stroke="${C}" stroke-width="3"/></pattern>
  <clipPath id="bodyClip"><path d="M-285 420 L-310 760 L310 760 L285 420Z"/></clipPath>
  <clipPath id="outerBurst"><path d="M0 0 H1500 V1800 H0Z M750 640 m-560 0 a560 560 0 1 0 1120 0 a560 560 0 1 0 -1120 0Z" clip-rule="evenodd"/></clipPath>
  <clipPath id="lowerHalf" clipPathUnits="objectBoundingBox"><rect x="0" y="0.62" width="1" height="0.4"/></clipPath>
</defs>
${scene}
<!-- top banner -->
<g>
  ${tornStrip(40, 124, N, -2)}
  <g data-fit="230 62 1040 80" data-anchor="1">
    <text font-family="Anton" font-size="100" fill="${C}" letter-spacing="10">${CONFIG.top}</text>
  </g>
  <path d="M190 104 l14 -40 l14 40 l-36 -25 h44z" transform="rotate(-2 750 126)" fill="${R}" stroke="${K}" stroke-width="3"/>
  <path d="M1280 104 l14 -40 l14 40 l-36 -25 h44z" transform="rotate(-2 750 126)" fill="${R}" stroke="${K}" stroke-width="3"/>
</g>
<!-- headline -->
<g transform="rotate(-3 750 1330)">
  ${headline(CONFIG.head1, 1080, 228)}
  ${headline(CONFIG.head2, 1328, 228)}
</g>
<!-- bottom strip -->
<g>
  ${tornStrip(1606, 116, R, 1.5)}
  <g data-fit="200 1628 1100 72"><text font-family="Anton" font-size="100" fill="${C}" letter-spacing="4">${CONFIG.bottom}</text></g>
</g>
</svg>`;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Anton;src:url(${fontUrl}) format('woff2');}
@font-face{font-family:Cinzel;src:url(${serifUrl});font-weight:400 900;}
html,body{margin:0;background:transparent;}svg{display:block}
</style></head><body>${svg}</body></html>`;

const tmp = path.resolve('renders/tshirt/_build.html');
fs.writeFileSync(tmp, html);
const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1500, height: 1800}, deviceScaleFactor: 3});
await page.goto('file://' + tmp);
await page.evaluate(async () => {
  await document.fonts.load('100px Anton');
  await document.fonts.load('700 100px Cinzel');
  await document.fonts.ready;
  for (const g of document.querySelectorAll('[data-fit]')) {
    const [x, y, w, h] = g.dataset.fit.split(' ').map(Number);
    const ref = g.querySelector('text:last-of-type') || g.querySelector('text');
    // measure the front text only (shadow copies are offset)
    const front = [...g.querySelectorAll('text')].find((t) => !t.getAttribute('transform')) || ref;
    const b = front.getBBox();
    const sx = w / b.width, sy = h / b.height;
    g.setAttribute('transform', `translate(${x} ${y}) scale(${sx} ${sy}) translate(${-b.x} ${-b.y})`);
  }
  // keep the top-banner text on the banner tilt
});
await page.screenshot({path: CONFIG.out, omitBackground: true, fullPage: false});
await browser.close();
console.log('wrote', CONFIG.out);
