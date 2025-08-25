import csv
from svgelements import SVG, Rect, Text
import os
from wand.api import library
import wand.color
import wand.image


# Folder and file setup
output_folder = "yt_shorts_svgs"
os.makedirs(output_folder, exist_ok=True)


WIDTH, HEIGHT = 1080, 1920
HALF = HEIGHT // 2

# colors pairs (top, bottom) — will cycle if more groups than colors
COLOR_PAIRS = [
    ("#3498db", "#e74c3c"),  # blue vs red
    ("#1abc9c", "#9b59b6"),  # teal vs purple
    ("#f39c12", "#2ecc71"),  # orange vs green
    ("#34495e", "#e67e22"),  # dark vs orange
]

CSV_FILE = "side_compare.csv"  # expects headers: Group,Language1,Percentage1,Language2,Percentage2

def make_short_svgs(csv_path, question=False):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for idx, row in enumerate(rows):
        group = row.get("Group", f"Group{idx+1}")
        lang1 = row.get("LanguageA", "")
        lang2 = row.get("LanguageB", "")
        if question == False:
            val1 = row.get("ValueA", "")
            val2 = row.get("ValueB", "")
        else:
            val1 = "?"
            val2 = "?"

        top_color, bottom_color = COLOR_PAIRS[idx % len(COLOR_PAIRS)]

        doc = SVG(width=WIDTH, height=HEIGHT)

        # Top half (Language1)
        top_rect = Rect(x=0, y=0, width=WIDTH, height=HALF, fill=top_color, stroke="green", stroke_width=40)
        doc.append(top_rect)
        top_text = Text(f"{lang1} — {val1}%", x=WIDTH/2, y=HALF/2,
                        fill="white", font_size=96, text_anchor="middle", font_family="Horizon", font_weight="bold")
        doc.append(top_text)

        # Bottom half (Language2)
        bot_rect = Rect(0, HALF, WIDTH, HALF, fill=bottom_color, stroke="green", stroke_width=40)
        doc.append(bot_rect)
        bot_text = Text(f"{lang2} — {val2}%", x=WIDTH/2, y=HALF + HALF/2,
                        fill="white", font_size=96, text_anchor="middle", font_family="Horizon", font_weight="bold")
        doc.append(bot_text)

        # Group title (small at very top)
        title = Text(group, x=WIDTH/2, y=80,
                     fill="yellow", font_size=72, text_anchor="middle", font_family="Chivo")
        doc.append(title)

        # VS badge centered on the seam
        vs = Text("VS", x=WIDTH/2, y=HALF + 10,
                  fill="yellow", font_size=96, text_anchor="middle", font_family="Chivo", font_weight="bold")
        doc.append(vs)

        # Save SVG (svgelements provides write_xml)
        if question == False:
            filename = f"shorts_{group.strip().replace(' ', '_')}.svg"
            pngname = f"shorts_{group.strip().replace(' ', '_')}.png"
        else:
            filename = f"shorts_{group.strip().replace(' ', '_')}_q.svg"
            pngname = f"shorts_{group.strip().replace(' ', '_')}_q.png"
        
        output_file = os.path.join(output_folder, filename)
        png_file = os.path.join(output_folder, pngname)
        doc.write_xml(output_file)
        print("Created SVG:", output_file)
        
        with wand.image.Image(filename=output_file, resolution=300) as img:
            img.format = 'png'
            img.save(filename=png_file)
            print("Created PNG:", png_file)

if __name__ == "__main__":
    make_short_svgs(CSV_FILE, True)
    make_short_svgs(CSV_FILE)
