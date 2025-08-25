import base64

# Paths
font_path = r"D:\inkscape_projects\kanini_kamal_data\fonts\Horizon-updated\horizon.otf"
svg_path = ".\yt_shorts_svgs\shorts_Hobbyists_q.svg"
output_svg_path = "output_with_font.svg"

# 1. Encode the font to base64
with open(font_path, "rb") as f:
    font_base64 = base64.b64encode(f.read()).decode("utf-8")

# 2. Prepare the style block with embedded font
style_block = f"""
<style type="text/css">
  @font-face {{
    font-family: 'Horizon';
    src: url('data:font/opentype;base64,{font_base64}') format('opentype');
  }}
  text {{
    font-family: 'Horizon';
  }}
</style>
"""

# 3. Load SVG and inject the style at the top (after <svg ...>)
with open(svg_path, "r", encoding="utf-8") as f:
    svg_content = f.read()

# Insert style after the first <svg ...> tag
if "<style" in svg_content:
    # Replace existing style
    import re
    svg_content = re.sub(r"<style.*?</style>", style_block, svg_content, flags=re.S)
else:
    # Insert right after <svg ...>
    svg_content = svg_content.replace(">", ">" + style_block, 1)

# 4. Save updated SVG
with open(output_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"✅ Updated SVG saved as {output_svg_path}")
