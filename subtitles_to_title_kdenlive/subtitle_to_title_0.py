import re
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

def ass_time_to_seconds(ass_time: str) -> float:
    """
    ASS time format: h:mm:ss.cs (centiseconds)
    Example: '00:00:03.40' -> 3.40 seconds
    """
    h, m, s_cs = ass_time.split(":")
    s, cs = s_cs.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 100.0


def duration_frames_from_ass(start_str: str, end_str: str, fps: float) -> int:
    """
    Match the Bash rounding:
      duration = round(end * fps) - round(start * fps)
    Ensure at least 1 frame.
    """
    start_sec = ass_time_to_seconds(start_str)
    end_sec = ass_time_to_seconds(end_str)

    start_frames = int(round(start_sec * fps))
    end_frames = int(round(end_sec * fps))

    dur = max(end_frames - start_frames, 1)
    return dur


def parse_ass_file(ass_path):
    """Parse an ASS file and extract subtitle entries (start, end, text)."""
    subs = []
    dialogue_re = re.compile(r"Dialogue: \d+,(.*?),(.*?),(?:.*?,){3}(.*)")
    
    with open(ass_path, "r", encoding="utf-8") as f:
        for line in f:
            m = dialogue_re.match(line)
            if m:
                start, end, text = m.groups()
                # Strip formatting tags like {\i1}, {\an8}, etc.
                text = re.sub(r"\{.*?\}", "", text).strip()
                subs.append({"start": start, "end": end, "text": text})
    return subs


def create_kdenlive_title(text, start_time, end_time, fps=30, width=1920, height=1080):
    """
    Create a valid .kdenlivetitle XML string for Kdenlive.

    Args:
        text (str): The subtitle text.
        start_time (float): Start time in seconds.
        end_time (float): End time in seconds.
        fps (int): Frames per second (default 30).
        width (int): Video width.
        height (int): Video height.
    """
    # Convert duration to frames
    duration_sec = end_time - start_time
    duration_frames = int(round(duration_sec * fps))

    root = Element("kdenlivetitle", {
        "LC_NUMERIC": "C",
        "duration": str(duration_frames),  # duration in frames
        "out": str(duration_frames),       # out must match duration
        "width": str(width),
        "height": str(height),
    })

    item = SubElement(root, "item", {"type": "QGraphicsTextItem", "z-index": "0"})
    position = SubElement(item, "position", {"x": str(width // 2 - 400), "y": str(height // 2 - 100)})
    transform = SubElement(position, "transform")
    transform.text = "1,0,0,0,1,0,0,0,1"

    SubElement(item, "content", {
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
    }).text = text

    SubElement(root, "startviewport", {"rect": "0,0,0,0"})
    SubElement(root, "endviewport", {"rect": "0,0,0,0"})
    SubElement(root, "background", {"color": "0,0,0,0"})

    xml_str = xml.dom.minidom.parseString(tostring(root)).toprettyxml(indent="  ")
    return xml_str


def convert_ass_to_kdenlive(ass_path, output_dir="titles", fps=30.0):
    subs = parse_ass_file(ass_path)
    for i, sub in enumerate(subs, start=1):
        create_kdenlive_title(sub, i, output_dir, fps)


# Example usage:
convert_ass_to_kdenlive("subtitles.ass", 
                        output_dir="titles", 
                        fps=30.0)
