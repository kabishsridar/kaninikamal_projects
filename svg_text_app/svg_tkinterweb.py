import tkinter as tk
from tkinter import filedialog, colorchooser, font, messagebox
from tkinterweb import HtmlFrame
import svgwrite


class SVGTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SVG Text Editor & Viewer (tkinterweb)")

        # ---------- Model (state) ----------
        self.text_value = tk.StringVar(value="Hello SVG")
        self.font_family = tk.StringVar(value="Arial")
        self.font_size = tk.IntVar(value=48)
        self.font_color = "#111111"

        # ---------- Controls ----------
        row = 0
        tk.Label(root, text="Text").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        tk.Entry(root, textvariable=self.text_value, width=40).grid(row=row, column=1, columnspan=3, sticky="ew", padx=6, pady=4)

        row += 1
        tk.Label(root, text="Font").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        families = sorted(font.families())
        tk.OptionMenu(root, self.font_family, *families).grid(row=row, column=1, sticky="ew", padx=6, pady=4)

        tk.Label(root, text="Size").grid(row=row, column=2, sticky="e", padx=6, pady=4)
        tk.Spinbox(root, from_=8, to=200, textvariable=self.font_size, width=6).grid(row=row, column=3, sticky="w", padx=6, pady=4)

        row += 1
        tk.Button(root, text="Pick Color", command=self.choose_color).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        self.color_swatch = tk.Label(root, text=self.font_color, bg=self.font_color, fg="#fff", width=12)
        self.color_swatch.grid(row=row, column=1, sticky="w", padx=6, pady=4)

        tk.Button(root, text="Save as SVG", command=self.save_svg).grid(row=row, column=2, sticky="e", padx=6, pady=4)
        tk.Button(root, text="Open SVG", command=self.open_svg).grid(row=row, column=3, sticky="w", padx=6, pady=4)

        # ---------- Preview (big) ----------
        row += 1
        self.preview = HtmlFrame(root, horizontal_scrollbar="auto", vertical_scrollbar="auto")
        self.preview.grid(row=row, column=0, columnspan=4, sticky="nsew", padx=6, pady=6)

        # Make the preview stretch
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(row, weight=1)

        # Live updates
        self.text_value.trace_add("write", lambda *args: self.update_preview())
        self.font_family.trace_add("write", lambda *args: self.update_preview())
        self.font_size.trace_add("write", lambda *args: self.update_preview())

        # Initial render
        self.update_preview()

    # ---------- Helpers ----------
    def choose_color(self):
        rgb, hex_code = colorchooser.askcolor(initialcolor=self.font_color, title="Pick text color")
        if hex_code:
            self.font_color = hex_code
            self.color_swatch.config(bg=self.font_color, text=self.font_color)
            self.update_preview()

    def build_svg_string(self, width=900, height=400):
        """
        Build an SVG with centered text using svgwrite.
        We keep it simple so it renders consistently across viewers.
        """
        dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"), profile="tiny")
        # Background (optional, helps visibility)
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill="white"))

        # Centered text: use text_anchor + dominant-baseline to center
        dwg.add(dwg.text(
            self.text_value.get(),
            insert=(width / 2, height / 2),
            fill=self.font_color,
            font_size=self.font_size.get(),
            font_family=self.font_family.get(),
            text_anchor="middle",
            # dominant_baseline="middle"
        ))
        return dwg.tostring()

    def update_preview(self):
        # Wrap the SVG in minimal HTML so tkinterweb can render it
        svg = self.build_svg_string()
        html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0; background:#e9ecef;">
{svg}
</body>
</html>"""
        try:
            self.preview.load_html(html)
        except Exception as e:
            messagebox.showerror("Preview error", str(e))

    def save_svg(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg")]
        )
        if not path:
            return
        try:
            svg = self.build_svg_string()
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            messagebox.showinfo("Saved", f"SVG saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def open_svg(self):
        path = filedialog.askopenfilename(
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            # Let tkinterweb render the existing SVG file directly
            self.preview.load_file(path)
        except Exception as e:
            messagebox.showerror("Open error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")  # nice large default window
    app = SVGTextApp(root)
    root.mainloop()
