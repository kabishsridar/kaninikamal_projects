🔹 Packaging as Executable

Once your code works, run:

pip install pyinstaller pillow cairosvg svgwrite tkinterweb

Cairosvg creates library conflicts

pip install pyinstaller svgwrite tkinterweb

Then create the executable:

pyinstaller --onefile --noconsole your_file.py


👉 On Windows: The .exe will be inside dist/your_file.exe.
👉 On Linux/Mac: You’ll get a binary you can run directly.

⚡ Now you can write text → save as SVG → open any SVG → view inside Tkinter.