import re
import xml.etree.ElementTree as ET
from pathlib import Path

import xml.etree.ElementTree as ET

def create_kdenlive_title(
    text: str,
    filename: str,
    width: int = 1920,
    height: int = 1080,
    font: str = "Segoe UI",
    font_size: int = 150,
    font_color=(255, 255, 0, 255),  # RGBA
    outline: int = 6,
    outline_color=(0, 0, 0, 255),
    x: int = 782,
    y: int = 322,
    duration: int = 1000
):
    root = ET.Element("kdenlivetitle", {
        "LC_NUMERIC": "C",
        "duration": str(duration),
        "height": str(height),
        "out": str(duration),
        "width": str(width)
    })

    item = ET.SubElement(root, "item", {"type": "QGraphicsTextItem", "z-index": "0"})

    # Position
    position = ET.SubElement(item, "position", {"x": str(x), "y": str(y)})
    ET.SubElement(position, "transform").text = "1,0,0,0,1,0,0,0,1"

    # Content
    content_attrs = {
        "alignment": "1",
        "box-height": "200",
        "box-width": "423",
        "font": font,
        "font-color": ",".join(map(str, font_color)),
        "font-italic": "0",
        "font-outline": str(outline),
        "font-outline-color": ",".join(map(str, outline_color)),
        "font-pixel-size": str(font_size),
        "font-underline": "0",
        "font-weight": "400",
        "letter-spacing": "0",
        "line-spacing": "0",
        "shadow": "0;#64000000;3;3;3",
        "tab-width": "80",
        "typewriter": "0;2;1;0;0"
    }
    ET.SubElement(item, "content", content_attrs).text = text

    # Viewport + background
    ET.SubElement(root, "startviewport", {"rect": "0,0,0,0"})
    ET.SubElement(root, "endviewport", {"rect": "0,0,0,0"})
    ET.SubElement(root, "background", {"color": "0,0,0,0"})

    # Write file
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


# Example usage
create_kdenlive_title("Tested", "subtitle.kdenlivetitle")


if __name__ == "__main__":
# Example usage
    create_kdenlive_title("Your Title", "sample1.kdenlivetitle")
