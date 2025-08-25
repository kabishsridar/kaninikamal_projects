import os
from svgelements import SVG, Rect, Text

# Folder and file setup
output_folder = "yt_shorts_svgs"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "group1.svg")

# Create SVG drawing
svg = SVG(width=1080, height=1920)

# Background
rect = Rect(x=0, y=0, width=1080, height=1920, fill="white")
svg.append(rect)

# Box with thick border
box = Rect(
    x=100, y=300, width=880, height=200,
    fill="lightblue",
    stroke="green",      # must define stroke color
    stroke_width=25      # now this will show
)
svg.append(box)

# Add sample text
text = Text("Group A: Python vs Java", x=150, y=420, font_size=60, fill="black")
svg.append(text)

# Save the SVG

svg.write_xml(output_file)

print(f"SVG saved at {output_file}")
