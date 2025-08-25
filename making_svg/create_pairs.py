import csv
import svgwrite

def create_svg_from_csv(csv_file, output_svg):
    dwg = svgwrite.Drawing(output_svg, profile='tiny', size=("800px", "600px"))

    # Colors for contrast (A vs B)
    colors = [("#4CAF50", "#F44336"),  # green vs red
              ("#2196F3", "#FF9800"),  # blue vs orange
              ("#9C27B0", "#03A9F4"),  # purple vs teal
              ("#795548", "#607D8B")]  # brown vs grey

    y_offset = 50
    box_width = 300
    box_height = 60
    padding = 20

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            group = row["Group"]
            lang_a, val_a = row["LanguageA"], row["ValueA"]
            lang_b, val_b = row["LanguageB"], row["ValueB"]

            # Choose contrasting colors by cycling
            color_a, color_b = colors[i % len(colors)]

            # Title: Group name
            dwg.add(dwg.text(group,
                             insert=(padding, y_offset - 10),
                             font_size="18px",
                             font_family="Chivo",
                             font_weight="bold",
                             fill="#000"))

            # Left box
            dwg.add(dwg.rect(insert=(padding, y_offset),
                             size=(box_width, box_height),
                             fill=color_a, rx=10, ry=10))
            dwg.add(dwg.text(f"{lang_a} ({val_a}%)",
                             insert=(padding + 15, y_offset + 35),
                             font_size="16px",
                             font_family="Chivo",
                             fill="#fff"))

            # Right box
            dwg.add(dwg.rect(insert=(2 * padding + box_width, y_offset),
                             size=(box_width, box_height),
                             fill=color_b, rx=10, ry=10))
            dwg.add(dwg.text(f"{lang_b} ({val_b}%)",
                             insert=(2 * padding + box_width + 15, y_offset + 35),
                             font_size="16px",
                             font_family="Chivo",
                             fill="#fff"))

            # Update Y position for next row
            y_offset += box_height + 50

    dwg.save()

# Example usage
create_svg_from_csv("side_compare.csv", "contrasting_boxes.svg")
