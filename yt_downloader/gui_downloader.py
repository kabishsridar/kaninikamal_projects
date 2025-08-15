import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

def choose_folder():
    folder = filedialog.askdirectory(title="Select Download Folder")
    download_folder_var.set(folder)

def get_formats():
    url = url_var.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL first.")
        return
    try:
        result = subprocess.run(
            ["yt-dlp", "-F", url],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        formats_text.delete("1.0", tk.END)
        formats_text.insert(tk.END, result.stdout)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def is_playlist(url):
    parsed = urlparse(url)
    return "list=" in parsed.query

def download():
    url = url_var.get().strip()
    folder = download_folder_var.get().strip()
    fmt = format_code_var.get().strip() or "18"
    playlist_range = playlist_range_var.get().strip()
    audio_only = audio_only_var.get()

    if not url or not folder:
        messagebox.showerror("Error", "Please provide both URL and destination folder.")
        return

    command = ["yt-dlp", "-o", os.path.join(folder, "%(title)s.%(ext)s")]

    if audio_only:
        command.extend(["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3"])
    else:
        command.extend(["-f", fmt])

    if playlist_range:
        command.extend(["--playlist-items", playlist_range])

    command.append(url)

    try:
        subprocess.run(command)
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def check_playlist():
    url = url_var.get().strip()
    if is_playlist(url):
        playlist_frame.pack(fill="x", pady=5)
    else:
        playlist_frame.forget()

# --- UI Setup ---
root = tk.Tk()
root.title("YouTube Downloader (yt-dlp)")
root.geometry("800x600")

# URL input
tk.Label(root, text="YouTube URL:").pack(anchor="w", padx=10, pady=2)
url_var = tk.StringVar()
tk.Entry(root, textvariable=url_var, width=80).pack(padx=10, pady=2)
tk.Button(root, text="Check Playlist", command=check_playlist).pack(pady=2)

# Destination folder
tk.Label(root, text="Destination Folder:").pack(anchor="w", padx=10, pady=2)
download_folder_var = tk.StringVar()
folder_frame = tk.Frame(root)
folder_frame.pack(fill="x", padx=10)
tk.Entry(folder_frame, textvariable=download_folder_var, width=60).pack(side="left", padx=2)
tk.Button(folder_frame, text="Browse", command=choose_folder).pack(side="left", padx=5)

# Format selection
tk.Label(root, text="Format Code (default 18):").pack(anchor="w", padx=10, pady=2)
format_code_var = tk.StringVar(value="18")
format_frame = tk.Frame(root)
format_frame.pack(fill="x", padx=10)
tk.Entry(format_frame, textvariable=format_code_var, width=20).pack(side="left", padx=2)
tk.Button(format_frame, text="Show Formats", command=get_formats).pack(side="left", padx=5)

# Formats output
formats_text = tk.Text(root, height=10)
formats_text.pack(fill="x", padx=10, pady=5)

# Playlist range (hidden unless detected)
playlist_frame = tk.Frame(root)
tk.Label(playlist_frame, text="Playlist Range (e.g., 1-5, leave blank for all):").pack(anchor="w")
playlist_range_var = tk.StringVar()
tk.Entry(playlist_frame, textvariable=playlist_range_var, width=20).pack(anchor="w", padx=5, pady=2)

# Audio-only option
audio_only_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download audio only (MP3)", variable=audio_only_var).pack(anchor="w", padx=10, pady=5)

# Download button
tk.Button(root, text="Download", command=download, bg="green", fg="white").pack(pady=10)

root.mainloop()
