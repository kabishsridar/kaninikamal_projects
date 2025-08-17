import tkinter as tk
from tkinter import filedialog, colorchooser, font, messagebox
import svgwrite
from PIL import Image, ImageTk
# import cairosvg
import io


class SVGTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SVG Text Generator & Viewer")

        # Default values
        self.text_value = tk.StringVar(value="Hello SVG")
        self.font_family = tk.StringVar(value="Arial")
        self.font_size = tk.IntVar(value=30)
        self.font_color = "#000000"

        # --- UI Setup ---
        tk.Label(root, text="Enter Text:").grid(row=0, column=0, sticky="w")
        tk.Entry(root, textvariable=self.text_value, width=30).grid(row=0, column=1, columnspan=2)

        tk.Label(root, text="Font:").grid(row=1, column=0, sticky="w")
        font_families = list(font.families())
        font_families.sort()
        tk.OptionMenu(root, self.font_family, *font_families).grid(row=1, column=1, sticky="ew")

        tk.Label(root, text="Size:").grid(row=2, column=0, sticky="w")
        tk.Spinbox(root, from_=8, to=150, textvariable=self.font_size, width=5).grid(row=2, column=1, sticky="w")

        tk.Button(root, text="Pick Color", command=self.choose_color).grid(row=3, column=0, pady=5)
        self.color_label = tk.Label(root, text=self.font_color, bg=self.font_color, width=10)
        self.color_label.grid(row=3, column=1)

        tk.Button(root, text="Save as SVG", command=self.save_svg).grid(row=4, column=0, pady=10)
        tk.Button(root, text="Open SVG", command=self.open_svg).grid(row=4, column=1, pady=10)

        # Bigger Preview Area
        self.preview = tk.Canvas(root, width=800, height=400, bg="white")
        self.preview.grid(row=5, column=0, columnspan=3, pady=10)

        self.preview_image = None  # For holding rendered SVG previews

        # Update preview automatically
        self.text_value.trace("w", lambda *args: self.update_preview())
        self.font_family.trace("w", lambda *args: self.update_preview())
        self.font_size.trace("w", lambda *args: self.update_preview())

        self.update_preview()

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")
        if color_code[1]:
            self.font_color = color_code[1]
            self.color_label.config(bg=self.font_color, text=self.font_color)
            self.update_preview()

    def update_preview(self):
        """Draws live text preview on canvas"""
        self.preview.delete("all")
        preview_font = (self.font_family.get(), self.font_size.get())
        self.preview.create_text(
            400, 200,
            text=self.text_value.get(),
            font=preview_font,
            fill=self.font_color
        )

    def save_svg(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".svg",
                                                 filetypes=[("SVG files", "*.svg")])
        if file_path:
            dwg = svgwrite.Drawing(file_path, profile='tiny')
            dwg.add(
                dwg.text(
                    self.text_value.get(),
                    insert=(50, 100),
                    fill=self.font_color,
                    font_size=self.font_size.get(),
                    font_family=self.font_family.get()
                )
            )
            dwg.save()
            messagebox.showinfo("Saved", f"SVG saved at {file_path}")

    def open_svg(self):
        """Open and display an existing SVG"""
        file_path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
        if file_path:
            try:
                # Convert SVG to PNG in memory
                png_data = cairosvg.svg2png(url=file_path)
                image = Image.open(io.BytesIO(png_data))
                image = image.resize((800, 400), Image.LANCZOS)
                self.preview_image = ImageTk.PhotoImage(image)

                # Show on canvas
                self.preview.delete("all")
                self.preview.create_image(0, 0, image=self.preview_image, anchor="nw")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load SVG:\n{e}")
            

if __name__ == "__main__":
    root = tk.Tk()
    app = SVGTextApp(root)
    root.mainloop()