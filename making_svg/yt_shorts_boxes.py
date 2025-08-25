import csv
from svgelements import *

# Canvas size for YouTube Shorts (portrait)
WIDTH, HEIGHT = 1080, 1920

# Input CSV (group, language, percentage)
csv_file = "side_compare.csv"

# Read CSV data
data = []
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Number of boxes
n = len(data)
box_height = HEIGHT // n

# Create SVG
svg = SVG(width=WIDTH, height=HEIGHT)

# Colors to alternate between
colors = ["#1abc9c", "#e74c3c"]

for i, row in enumerate(data):
    y = i * box_height
    color = colors[i % len(colors)]
    
    # Draw rectangle (horizontal box)
    rect = Rect(0, y, WIDTH, box_height, fill=color, stroke="white", stroke_width=5)
    svg.append(rect)

    # Text: Group
    text1 = Text(row["Group"], x=WIDTH/2, y=y + box_height/3, 
                 fill="white", font_size=60, text_anchor="middle", font_family="Horizon Bold")
    svg.append(text1)

    # Text: Language + Percentage
    text2 = Text(f"{row['Language']} - {row['Percentage']}%", 
                 x=WIDTH/2, y=y + 2*box_height/3, 
                 fill="white", font_size=80, text_anchor="middle", font_family="Horizon Bold")
    svg.append(text2)

# Save SVG
with open("shorts_languages.svg", "w", encoding="utf-8") as f:
    svg.write_xml(f)

print("SVG created: shorts_languages.svg")
