from svgelements import SVG, Rect, Text

# Build the SVG container
svg = SVG(width=800, height=600)

# Add elements
rect = Rect(x=50, y=50, width=200, height=100, stroke="black", fill="white")
text = Text("Hello Table", x=60, y=100, font_size=20, fill="black")

svg.append(rect)
svg.append(text)

# Write properly with <svg> root and xmlns
svg.write_xml("table.svg")
