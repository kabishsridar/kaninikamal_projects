import re
import os
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

# ---------------- helpers ----------------
def ass_time_to_seconds(ass_time: str) -> float:
    """ASS time format: H:MM:SS.CS  (centiseconds)
    Example: '0:00:03.40' or '00:00:03.40' -> 3.40 seconds
    """
    parts = ass_time.strip().split(":")
    if len(parts) == 3:
        h = int(parts[0])
        m = int(parts[1])
        s_cs = parts[2]
    else:
        raise ValueError("Unexpected ASS time format: " + ass_time)
    s, cs = s_cs.split(".")
    return h * 3600 + m * 60 + int(s) + int(cs) / 100.0


def parse_ass_file(ass_path):
    """Return list of {'start':..., 'end':..., 'text':...} from Dialogue lines."""
    dialogues = []
    # capture start,end and everything after the 9th comma (text)
    dialogue_re = re.compile(r"^Dialogue:\s*\d+,(?P<start>[^,]+),(?P<end>[^,]+),(?:[^,]*,){5}(?P<text>.*)$")
    with open(ass_path, "r", encoding="utf-8") as fh:
        for ln in fh:
            m = dialogue_re.match(ln)
            if not m:
                continue
            text = m.group("text").strip()
            # remove ASS override tags like {\i1} etc.
            text = re.sub(r"\{.*?\}", "", text).strip()
            dialogues.append({
                "start": m.group("start").strip(),
                "end": m.group("end").strip(),
                "text": text
            })
    return dialogues

# ---------------- create title ----------------
def create_kdenlive_title(text, start_time, end_time, fps=30, width=1920, height=1080):
    """
    Create a .kdenlivetitle XML string.

    start_time, end_time: seconds (floats)
    fps: frames per second
    The duration is computed using: round(end*fps) - round(start*fps)
    """
    # compute frames using same rounding as your bash script
    start_frames = int(round(start_time * fps))
    end_frames = int(round(end_time * fps))
    duration_frames = max(end_frames - start_frames, 1)
    out_frame = max(duration_frames - 1, 0)

    root = Element("kdenlivetitle", {
        "LC_NUMERIC": "C",
        "duration": str(duration_frames),
        "out": str(out_frame),
        "width": str(width),
        "height": str(height)
    })

    item = SubElement(root, "item", {"type": "QGraphicsTextItem", "z-index": "0"})
    position = SubElement(item, "position", {"x": str(width // 2 - 400), "y": str(height // 2 - 100)})
    SubElement(position, "transform").text = "1,0,0,0,1,0,0,0,1"

    content_attrs = {
        "alignment": "1",
        "box-height": "200",
        "box-width": "800",
        "font": "Segoe UI",
        "font-color": "255,255,0,255",
        "font-italic": "0",
        "font-outline": "6",
        "font-outline-color": "0,0,0,255",
        "font-pixel-size": "60",
        "font-underline": "0",
        "font-weight": "400",
        "letter-spacing": "0",
        "line-spacing": "0",
        "shadow": "0;#64000000;3;3;3",
        "tab-width": "80",
        "typewriter": "0;2;1;0;0"
    }
    SubElement(item, "content", content_attrs).text = text

    SubElement(root, "startviewport", {"rect": "0,0,0,0"})
    SubElement(root, "endviewport", {"rect": "0,0,0,0"})
    SubElement(root, "background", {"color": "0,0,0,0"})

    xml_str = xml.dom.minidom.parseString(tostring(root)).toprettyxml(indent="  ")
    return xml_str

# ---------------- fixed convert function ----------------
def convert_ass_to_kdenlive(ass_path, output_dir="titles", fps=30.0, width=1920, height=1080):
    """
    Convert ASS -> many .kdenlivetitle files.
    Uses create_kdenlive_title(text, start_time_seconds, end_time_seconds, fps, width, height)
    """
    subs = parse_ass_file(ass_path)
    os.makedirs(output_dir, exist_ok=True)

    for i, sub in enumerate(subs, start=1):
        start_s = ass_time_to_seconds(sub["start"])
        end_s = ass_time_to_seconds(sub["end"])
        xml_str = create_kdenlive_title(sub["text"], start_s, end_s, fps=fps, width=width, height=height)

        out_file = os.path.join(output_dir, f"subtitle_{i:04d}.kdenlivetitle")
        with open(out_file, "w", encoding="utf-8") as fh:
            fh.write(xml_str)

    print(f"Created {len(subs)} title files in '{output_dir}' (fps={fps}, size={width}x{height})")

# ---------------- example ----------------
convert_ass_to_kdenlive("subtitles.ass", 
                        output_dir="Kden_Titles", 
                        fps=30.0, width=1920, height=1080)
