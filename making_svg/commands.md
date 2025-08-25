pip install svglib svgelements svgwrite wand  

need to have imageMagick installed https://imagemagick.org/script/download.php#windows

The above is required for writing the svg file to png

Needed to use the @font_face directly into the svg file. Tested it with embedding_font_to_svg.py

Hit a block when realized that fonts are not directly getting linked with the svg files that is being created

Then decided to proceed with javascript alternative