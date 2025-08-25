import csv
import os
import base64
import re
from svgelements import SVG, Rect, Text
import wand.image
import subprocess

# --- FOLDER & FILE SETUP ---
output_folder = "yt_shorts_svgs"
os.makedirs(output_folder, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
HALF = HEIGHT // 2

# --- COLOR PAIRS (Top/Bottom) ---
COLOR_PAIRS = [
    ("#3498db", "#e74c3c"),  # blue vs red
    ("#1abc9c", "#9b59b6"),  # teal vs purple
    ("#f39c12", "#2ecc71"),  # orange vs green
    ("#34495e", "#e67e22"),  # dark vs orange
]

CSV_FILE = "side_compare.csv"  # expects headers: Group, LanguageA, ValueA, LanguageB, ValueB

# --- FONT EMBEDDING FUNCTION ---
def embed_fonts(svg_content):
    fonts = [
        {
            "name": "Horizon",
            "path": r"D:\inkscape_projects\kanini_kamal_data\fonts\Horizon-updated\horizon.otf",
            "format": "opentype"
        },
        {
            "name": "ChivoBold",
            "path": r"D:\inkscape_projects\kanini_kamal_data\fonts\Chivo\static\Chivo-Bold.ttf",
            "format": "truetype"
        }
    ]

    font_faces = []
    for font in fonts:
        with open(font["path"], "rb") as f:
            font_base64 = base64.b64encode(f.read()).decode("utf-8")

        font_faces.append(f"""
        @font-face {{
            font-family: '{font["name"]}';
            src: url('data:font/{font["format"]};base64,{font_base64}') format('{font["format"]}');
            font-weight: {'bold' if 'Bold' in font["name"] else 'normal'};
        }}
        """)

    style_block = f"""
    <style type="text/css">
        {''.join(font_faces)}
        text {{
            font-family: 'Horizon', 'ChivoBold', sans-serif;
        }}
    </style>
    """

    if "<style" in svg_content:
        svg_content = re.sub(r"<style.*?</style>", style_block, svg_content, flags=re.S)
    else:
        svg_content = svg_content.replace(">", ">" + style_block, 1)

    return svg_content

def outline_text_with_inkscape(input_svg, output_svg):
    cmd = [
        "inkscape",
        input_svg,
        "--export-plain-svg=" + output_svg,
        "--export-text-to-path"
    ]
    subprocess.run(cmd, check=True)

# --- MAIN GENERATOR ---
def make_short_svgs(csv_path, question=False):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for idx, row in enumerate(rows):
        group = row.get("Group", f"Group{idx+1}")
        lang1 = row.get("LanguageA", "")
        lang2 = row.get("LanguageB", "")
        if not question:
            val1 = row.get("ValueA", "")
            val2 = row.get("ValueB", "")
        else:
            val1 = "?"
            val2 = "?"

        top_color, bottom_color = COLOR_PAIRS[idx % len(COLOR_PAIRS)]
        doc = SVG(width=WIDTH, height=HEIGHT)

        # Top half
        doc.append(Rect(x=0, y=0, width=WIDTH, height=HALF, fill=top_color, stroke="green", stroke_width=40))
        doc.append(Text(f"{lang1} — {val1}%", x=WIDTH/2, y=HALF/2,
                        fill="white", font_size=96, text_anchor="middle", font_family="Horizon", font_weight="bold"))

        # Bottom half
        doc.append(Rect(x=0, y=HALF, width=WIDTH, height=HALF, fill=bottom_color, stroke="green", stroke_width=40))
        doc.append(Text(f"{lang2} — {val2}%", x=WIDTH/2, y=HALF + HALF/2,
                        fill="white", font_size=96, text_anchor="middle", font_family="Horizon", font_weight="bold"))

        # Group title
        doc.append(Text(group, x=WIDTH/2, y=80,
                        fill="yellow", font_size=72, text_anchor="middle", font_family="ChivoBold"))

        # VS badge
        doc.append(Text("VS", x=WIDTH/2, y=HALF + 10,
                        fill="yellow", font_size=96, text_anchor="middle", font_family="ChivoBold", font_weight="bold"))

        # Save paths
        if not question:
            filename = f"shorts_{group.strip().replace(' ', '_')}.svg"
            outfile = f"shorts_{group.strip().replace(' ', '_')}_outlined.svg"
            pngname = f"shorts_{group.strip().replace(' ', '_')}.png"
        else:
            filename = f"shorts_{group.strip().replace(' ', '_')}_q.svg"
            outfile = f"shorts_{group.strip().replace(' ', '_')}_q_outlined.svg"
            pngname = f"shorts_{group.strip().replace(' ', '_')}_q.png"

        output_file = os.path.join(output_folder, filename)
        png_file = os.path.join(output_folder, pngname)

        # Write SVG with embedded fonts
        doc.write_xml(output_file)
        # with open(output_file, "r", encoding="utf-8") as f:
        #     svg_data = f.read()
        # svg_data = embed_fonts(svg_data)
        # with open(output_file, "w", encoding="utf-8") as f:
        #     f.write(svg_data)

        print("✅ Created SVG:", output_file)
        
        outline_text_with_inkscape(input_svg=output_file, output_svg=outfile)

        # Convert to PNG
        with wand.image.Image(filename=output_file, resolution=300) as img:
            img.format = 'png'
            img.save(filename=png_file)
            print("✅ Created PNG:", png_file)


if __name__ == "__main__":
    make_short_svgs(CSV_FILE, True)
    make_short_svgs(CSV_FILE)