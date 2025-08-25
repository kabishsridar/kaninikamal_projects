const fs = require('fs');
const path = require('path');
const parse = require('csv-parse/sync').parse;
const opentype = require('opentype.js');
const sharp = require('sharp');

// create folder if not exists
const dir = "./yt_shorts_svgs";

if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

// --- SETTINGS ---
const WIDTH = 1080;
const HEIGHT = 1920;
const HALF = HEIGHT / 2;
const COLOR_PAIRS = [
    ["#3498db", "#e74c3c"],
    ["#1abc9c", "#9b59b6"],
    ["#f39c12", "#2ecc71"],
    ["#34495e", "#e67e22"]
];

// --- FONT FILES ---
const FONT_PATH = path.resolve('fonts/calibri.ttf'); // supply your .ttf file here


function svgTextAsPath(text, font, fontSize, x, y, color, weight='normal') {
    // opentype.js font weight handling is by use of appropriate font file
    const pathObj = font.getPath(text, x, y, fontSize);
    return `<path d="${pathObj.toPathData()}" fill="${color}" />`;
}

function svgTextAsCenteredPath(text, font, fontSize, boxCenterX, boxCenterY, color) {
    const pathObj = font.getPath(text, 0, 0, fontSize); // Start path at origin
    const bbox = pathObj.getBoundingBox();

    // Calculate the center of the bounding box
    const textWidth = bbox.x2 - bbox.x1;
    const textHeight = bbox.y2 - bbox.y1;
    const textCenterX = bbox.x1 + textWidth / 2;
    const textCenterY = bbox.y1 + textHeight / 2;

    // Desired center is boxCenterX/Y, so shift accordingly
    const dx = boxCenterX - textCenterX;
    const dy = boxCenterY - textCenterY;

    // Move each command in pathObj by dx/dy
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


function makeShortSvgs(csvFilePath, question = false) {
    // Parse CSV
    const csvContent = fs.readFileSync(csvFilePath, 'utf8');
    const rows = parse(csvContent, {columns: true, skip_empty_lines: true});

    const font = opentype.loadSync(FONT_PATH);
    const fontChivo = opentype.loadSync('./fonts/Chivo-Bold.ttf');
    const fontHorizon = opentype.loadSync('./fonts/horizon.otf');
    rows.forEach((row, idx) => {
        const group = row["Group"] || `Group${idx+1}`;
        const lang1 = row["LanguageA"] || "";
        const lang2 = row["LanguageB"] || "";
        let val1, val2;
        if (!question) {
            val1 = row["ValueA"] || "";
            val2 = row["ValueB"] || "";
        } else {
            val1 = "?";
            val2 = "?";
        }
        const [topColor, bottomColor] = COLOR_PAIRS[idx % COLOR_PAIRS.length];

        // SVG content
        let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}">`;
        // Top half rect
        svg += `<rect x="0" y="0" width="${WIDTH}" height="${HALF}" fill="${topColor}" stroke="green" stroke-width="40"/>`;
        // Top half text as path
        // svg += svgTextAsPath(`${lang1} — ${val1}`, fontHorizon, 144, WIDTH/2, HALF/2, "#fff", "bold");
        svg += svgTextAsCenteredPath(`${lang1} — ${val1}`, fontHorizon, 100, WIDTH/2, HALF/2, "#fff");
        // Bottom half rect
        svg += `<rect x="0" y="${HALF}" width="${WIDTH}" height="${HALF}" fill="${bottomColor}" stroke="green" stroke-width="40"/>`;
        // Bottom half text as path
        // svg += svgTextAsPath(`${lang2} — ${val2}`, fontHorizon, 144, WIDTH/2, HALF + HALF/2, "#fff", "bold");
        svg += svgTextAsCenteredPath(`${lang2} — ${val2}`, fontHorizon, 100, WIDTH/2, HALF + HALF/2, "#fff");
        // Group title
        // svg += svgTextAsPath(group, fontChivo, 96, WIDTH/2, 80, "#ffff00");
        // VS badge
        // svg += svgTextAsPath("VS", font, 120, WIDTH/2, HALF + 10, "#ffff00", "bold");
        svg += svgTextAsCenteredPath(group, fontChivo, 70, WIDTH/2, 80, "#ffff00");
        svg += svgTextAsCenteredPath("VS", fontChivo, 90, WIDTH/2, HALF + 10, "#ffff00");

        svg += `</svg>`;

        // Write SVG
        const safeGroup = group.replace(/ /g, '_');
        const name = question ? `${safeGroup}_q` : safeGroup;
        const svgPath = `./yt_shorts_svgs/shorts_${name}.svg`;
        fs.writeFileSync(svgPath, svg, 'utf8');
        console.log(`✅ Created SVG: ${svgPath}`);

        // Convert SVG to PNG
        const pngPath = `./yt_shorts_svgs/shorts_${name}.png`;
        sharp(Buffer.from(svg)).png().toFile(pngPath)
            .then(() => console.log(`✅ Created PNG: ${pngPath}`))
            .catch(err => console.error("Sharp PNG error", err));
    });
}

// USAGE
const csvFile = process.argv[2] || './side_compare.csv';
makeShortSvgs(csvFile, false);
makeShortSvgs(csvFile, true);
