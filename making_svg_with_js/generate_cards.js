const fs = require('fs');
const path = require('path');
const parse = require('csv-parse/sync').parse;
const opentype = require('opentype.js');
const sharp = require('sharp');

const dir = "./yt_shorts_svgs";
if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

// --- SETTINGS ---
const WIDTH = 1080;
const HEIGHT = 1920;
const BAR_WIDTH = 700;
const BAR_X = 300;
const BAR_START_Y = 500;
const BAR_HEIGHT = 40;
const BAR_GAP = 60;
const COLOR_PAIRS = [
  "#4caf50","#2196f3","#ff9800","#009688","#e91e63","#9c27b0","#607d8b","#fbc02d"
];

// --- FONT FILES ---
const FONT_PATH = path.resolve('fonts/calibri.ttf'); // supply your .ttf file here

function svgTextAsCenteredPath(text, font, fontSize, boxCenterX, boxCenterY, color) {
  const pathObj = font.getPath(text, 0, 0, fontSize); // Start path at origin
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

  const traitNames = [
    "Readability",
    "Writability",
    "Reliability",
    "Maintainability",
    "Security",
    "Compatibility",
    "Standards_Compliance",
    "Community_Support"
  ];

  rows.forEach((row, idx) => {
    // Title text as path
    const titlePath = svgTextAsCenteredPath(row.Language, font, 80, WIDTH/2, 180, "#222");

    // Logo image (SVG as <image> by link)
    const logoSvg = `<image href="${row.SVG_Repo_Link}" x="${WIDTH/2-80}" y="270" width="160" height="160" />`;

    // Draw the trait bars
    let bars = '';
    traitNames.forEach((trait, i) => {
      const score = parseInt(row[trait],10);
      const actualBarWidth = Math.floor((score/10) * BAR_WIDTH);
      const barY = BAR_START_Y + i * BAR_GAP;

      bars += 
        `<text x="${BAR_X-30}" y="${barY+BAR_HEIGHT-12}" font-size="44" fill="#222" text-anchor="end" alignment-baseline="middle">${trait.replace('_', ' ')}</text>
        <rect x="${BAR_X}" y="${barY}" width="${BAR_WIDTH}" height="${BAR_HEIGHT}" rx="18" fill="#eee" />
        <rect x="${BAR_X}" y="${barY}" width="${actualBarWidth}" height="${BAR_HEIGHT}" rx="18" fill="${COLOR_PAIRS[i]}" />
        <text x="${BAR_X+BAR_WIDTH+20}" y="${barY+BAR_HEIGHT-12}" font-size="44" fill="#222">${score}</text>\n`;
    });

    // SVG assembly
    const svgContent = `
<svg viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#fff" />
  ${titlePath}
  ${logoSvg}
  ${bars}
</svg>
`;

    // Write to SVG file
    const outFile = path.join(dir, `${row.Language.replace(/[^a-z0-9]/gi,"_")}.svg`);
    fs.writeFileSync(outFile, svgContent, 'utf8');
    // Optionally, convert to PNG
    // sharp(Buffer.from(svgContent)).toFile(outFile.replace('.svg','.png'));
  });

  console.log('SVGs created for each language');
}

// Usage example
makeShortSvgs('language_ratings.csv');
