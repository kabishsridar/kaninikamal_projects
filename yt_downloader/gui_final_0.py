import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import sys

def run_command(command):
    """Run a command and handle multiple encodings safely."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True
        )
        try:
            return result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return result.stdout.decode("cp1252", errors="replace")
    except subprocess.CalledProcessError as e:
        try:
            return e.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return e.stdout.decode("cp1252", errors="replace")

def show_formats():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Warning", "Please enter a video URL.")
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Fetching available formats...\n")

    def worker():
        formats_output = run_command(["yt-dlp", "-F", url])
        output_text.insert(tk.END, formats_output + "\n")

    threading.Thread(target=worker, daemon=True).start()

def download_video():
    url = url_entry.get().strip()
    fmt = format_entry.get().strip()
    if not url or not fmt:
        messagebox.showwarning("Warning", "Please enter both URL and format code.")
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Downloading format {fmt}...\n")

    def worker():
        process = subprocess.Popen(
            ["yt-dlp", "-f", fmt, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in process.stdout:
            try:
                decoded_line = line.decode("utf-8")
            except UnicodeDecodeError:
                decoded_line = line.decode("cp1252", errors="replace")
            output_text.insert(tk.END, decoded_line)
            output_text.see(tk.END)

    threading.Thread(target=worker, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("YouTube Downloader (yt-dlp GUI)")

tk.Label(root, text="Video URL:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text="Format Code (from list):").pack()
format_entry = tk.Entry(root, width=10)
format_entry.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Show Formats", command=show_formats).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Download", command=download_video).pack(side=tk.LEFT, padx=5)

output_text = scrolledtext.ScrolledText(root, width=80, height=20)
output_text.pack()

root.mainloop()