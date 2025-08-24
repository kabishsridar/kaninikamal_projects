import csv
from svgelements import SVG, Rect, Text

def csv_to_svg_plain(csv_path, out_path, cell_w=120, cell_h=40, font_size=14):
    # Read CSV
    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    n_rows = len(rows)
    n_cols = len(rows[0]) if n_rows else 0
    width  = n_cols * cell_w
    height = n_rows * cell_h

    # Root SVG element
    doc = SVG(width=width, height=height)  # root container

    # Build cells + text
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            x = c * cell_w
            y = r * cell_h
            fill = "#f2f2f2" if r == 0 else "#ffffff"

            doc.append(Rect(x=x, y=y, width=cell_w, height=cell_h,
                            stroke="black", fill=fill))
            doc.append(Text(val, x=x + 8, y=y + cell_h/2 + font_size/3,
                            font_size=font_size, fill="#111",
                            font_family="Chivo, normal"))

    # Proper serialization
    doc.write_xml(out_path)          # writes a valid SVG file
    # Or: xml_string = doc.string_xml()  # if you need the XML as a string


def csv_to_svg(csv_path, out_path, cell_w=420, cell_h=60, font_size=18):
    # Read CSV
    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    n_rows = len(rows)
    n_cols = len(rows[0]) if n_rows else 0
    width  = n_cols * cell_w
    height = n_rows * cell_h

    # Root SVG
    doc = SVG(width=width, height=height)

    # Table rendering
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            x = c * cell_w
            y = r * cell_h
            fill = "#f2f2f2" if r == 0 else "#ffffff"

            # Draw cell
            doc.append(Rect(x=x, y=y, width=cell_w, height=cell_h,
                            stroke="black", fill=fill))

            # Choose font depending on column
            if c == 0:  # English column
                font_family = "Chivo, sans-serif"
                font_weight = "normal"
            else:  # Tamil column
                font_family = "Nirmala UI"
                font_weight = "bold"

            # Add text
            doc.append(Text(val, x=x + 10, y=y + cell_h/2 + font_size/3,
                            font_size=font_size, fill="#111",
                            font_family=font_family, font_weight=font_weight))

    # Write out
    doc.write_xml(out_path)


if __name__ == "__main__":
    csv_to_svg("uses_filehandling.csv", "reasons_table.svg")
