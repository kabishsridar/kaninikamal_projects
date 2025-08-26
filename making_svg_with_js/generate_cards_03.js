const fs = require('fs');
const path = require('path');
const parse = require('csv-parse/sync').parse;
const opentype = require('opentype.js');

const dir = "./yt_shorts_svgs";
if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}


const WIDTH = 1080;
const HEIGHT = 1920;
const BORDER_RADIUS = 64;
const BORDER_WIDTH = 20;
const CARD_PADDING_X = 120;  // increased padding from edges
const CARD_PADDING_Y = 60;   // top/bottom padding
const BAR_WIDTH = 550;       // smaller bars
const BAR_HEIGHT = 32;       // shorter bars
const BAR_GAP = 54;
const BAR_X = CARD_PADDING_X + 150; // bring bars more inward
const BAR_START_Y = 510;
const COLOR_PAIRS = [
  "#4caf50","#2196f3","#ff9800","#009688","#e91e63","#9c27b0","#607d8b","#fbc02d"
];

// --- FONT FILES ---
const FONT_PATH = path.resolve('fonts/calibri.ttf');
const BOLD_FONT_PATH = path.resolve('fonts/Chivo-Bold.ttf'); // ensure you have this

function getLanguageDesc(lang) {
  const desc = {
    Python: [
      "Python is widely appreciated for its clear syntax.",
      "Excellent for web, automation, AI and data tasks.",
      "Huge supportive community and rich libraries.",
      "Perfect language for beginners and experts alike."
    ],
    JavaScript: [
      "JavaScript powers interactive web experiences.",
      "Versatile language for both frontend and backend.",
      "Runs everywhere: browsers, servers, and tools.",
      "Large community and evolving frameworks."
    ],
    Java: [
      "Java is robust and widely used in enterprise apps.",
      "Reliable performance and cross-platform support.",
      "Strong for Android, backend, and big data.",
      "Decades of documentation and community wisdom."
    ],
    "C++": [
      "C++ delivers speed and high control for hardware.",
      "Key for systems, games, and performance apps.",
      "Complex, powerful, and widely used in industry.",
      "Strong legacy, but steeper learning curve."
    ],
    "C#": [
      "C# is leading for Windows and .NET development.",
      "Modern features and solid object-orientation.",
      "Great for games, web, and desktop apps.",
      "Strong support by Microsoft ecosystem."
    ],
    Go: [
      "Go focuses on simplicity and concurrency.",
      "Popular for cloud, networking, and microservices.",
      "Efficient, fast, and statically typed.",
      "Favored by many tech companies for performance."
    ],
    Rust: [
      "Rust ensures memory safety and performance.",
      "Systems programming without compromise.",
      "Gaining popularity in web, cloud, and OS tools.",
      "Loved for reliability and modern syntax."
    ],
    Kotlin: [
      "Kotlin is now key for modern Android apps.",
      "Concise syntax with full Java compatibility.",
      "Enables fast, maintainable mobile development.",
      "Officially supported by Google."
    ],
    Typescript: [
      "TypeScript builds on JavaScript with static types.",
      "Great for scalable, error-resistant web apps.",
      "Tools and frameworks embrace TypeScript.",
      "Balances flexibility and safety."
    ],
    Swift: [
      "Swift is Apple's modern language for iOS/macOS.",
      "Safe, expressive, with easy-to-read syntax.",
      "Powerful for mobile, desktop, and services.",
      "Vibrant ecosystem and official support."
    ]
  };
  return desc[lang] || ["Popular language.", "Widely used for multiple domains.", "Strong support and reliability.", "Ideal for modern development."];
}

function svgTextAsCenteredPath(text, font, fontSize, boxCenterX, boxCenterY, color) {
  const pathObj = font.getPath(text, 0, 0, fontSize);
  const bbox = pathObj.getBoundingBox();
  const textWidth = bbox.x2 - bbox.x1;
  const textHeight = bbox.y2 - bbox.y1;
  const textCenterX = bbox.x1 + textWidth / 2;
  const textCenterY = bbox.y1 + textHeight / 2;
  const dx = boxCenterX - textCenterX;
  const dy = boxCenterY - textCenterY;
  pathObj.commands.forEach(cmd => {
    if ('x' in cmd) cmd.x += dx;
    if ('y' in cmd) cmd.y += dy;
    if ('x1' in cmd) cmd.x1 += dx;
    if ('y1' in cmd) cmd.y1 += dy;
    if ('x2' in cmd) cmd.x2 += dx;
    if ('y2' in cmd) cmd.y2 += dy;
  });
  return `<path d="${pathObj.toPathData()}" fill="${color}" />`;
}

function makeShortSvgs(csvFilePath) {
  const csvContent = fs.readFileSync(csvFilePath, 'utf8');
  const rows = parse(csvContent, {columns: true, skip_empty_lines: true});
  const font = opentype.loadSync(FONT_PATH);
  const boldFont = opentype.loadSync(BOLD_FONT_PATH);

  const traitNames = [
    "Readability",
    "Writability",
    "Reliability",
    "Maintainability",
    "Security",
    "Compatibility",
    "Compliance",
    "Community"
  ];

  rows.forEach((row, idx) => {
    // Gradient background and border
    const grad = `
      <defs>
        <linearGradient id="bg-gradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8B5E3C"/>
          <stop offset="100%" stop-color="#3C8B5E"/>
        </linearGradient>
      </defs>
    `;
    const cardBorder = `
      <rect x="${BORDER_WIDTH/2}" y="${BORDER_WIDTH/2}" 
            width="${WIDTH-BORDER_WIDTH}" height="${HEIGHT-BORDER_WIDTH}" 
            rx="${BORDER_RADIUS}" fill="none" stroke="#fff" stroke-width="${BORDER_WIDTH}" />
    `;

    // Title and logo
    const titlePath = svgTextAsCenteredPath(row.Language, font, 76, WIDTH/2, 150, "#fff");
    const logoSvg = `<image href="./lang_logos/${row.Language}" x="${WIDTH/2-80}" y="235" width="160" height="160" />`;

    // Trait bars, narrowed and inward
    let bars = '';
    traitNames.forEach((trait, i) => {
      const key = trait.replace(' ', '_');
      const score = parseInt(row[key], 10) || 1;
      const actualBarWidth = Math.floor((score/10) * BAR_WIDTH);
      const barY = BAR_START_Y + i * BAR_GAP;
      bars += 
        `<text x="${BAR_X-30}" y="${barY+BAR_HEIGHT-8}" font-size="32" font-family="Chivo-Bold, sans-serif" font-weight="bold" fill="#F5F5F5" text-anchor="end">${trait}</text>
        <rect x="${BAR_X}" y="${barY}" width="${BAR_WIDTH}" height="${BAR_HEIGHT}" rx="14" fill="#222" opacity="0.35" />
        <rect x="${BAR_X}" y="${barY}" width="${actualBarWidth}" height="${BAR_HEIGHT}" rx="14" fill="${COLOR_PAIRS[i]}" />
        <text x="${BAR_X+BAR_WIDTH+16}" y="${barY+BAR_HEIGHT-8}" font-size="34" font-family="Chivo-Bold, sans-serif" font-weight="bold" fill="#fff" text-anchor="start">${score}</text>\n`;
    });

    // Description below bars, tucked in (smaller font, padding)
    const descStartY = BAR_START_Y + traitNames.length * BAR_GAP + 40;
    const descLines = getLanguageDesc(row.Language).map(
      (line, i) => `
        <text x="${WIDTH/2}" y="${descStartY + i * 45}"
              text-anchor="middle"
              font-size="42"
              font-family="Chivo-Bold, sans-serif"
              font-weight="bold"
              fill="#fff"
              style="text-shadow:0px 2px 12px #333; text-wrap:balance;">
          ${line}
        </text>`
    ).join('\n');

    // SVG
    const svgContent = `
<svg viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  ${grad}
  <rect width="100%" height="100%" fill="url(#bg-gradient)" />
  ${cardBorder}
  <g>
    ${titlePath}
    ${logoSvg}
    ${bars}
    ${descLines}
  </g>
</svg>
    `;

    const outFile = path.join(dir, `${row.Language.replace(/[^a-z0-9]/gi,"_")}.svg`);
    fs.writeFileSync(outFile, svgContent, 'utf8');
  });

  console.log('SVG cards created: neat border, non-overlapping ratings/description.');
}

makeShortSvgs('language_ratings.csv');