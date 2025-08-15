import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import re

# Run command and stream output to the log box
def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True, encoding='utf-8', errors='replace'
    )
    for line in process.stdout:
        log_box.insert(tk.END, line)
        log_box.see(tk.END)
    process.wait()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def check_formats():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a video or playlist URL")
        return
    log_box.delete(1.0, tk.END)
    threading.Thread(
        target=run_command,
        args=(f'yt-dlp -F "{url}"',),
        daemon=True
    ).start()

def start_download():
    url = url_entry.get().strip()
    folder = folder_entry.get().strip()
    fmt = format_entry.get().strip() or "18"
    if not url:
        messagebox.showerror("Error", "Please enter a video or playlist URL")
        return
    if not folder:
        messagebox.showerror("Error", "Please select a destination folder")
        return

    log_box.delete(1.0, tk.END)

    # Check if it's a playlist
    check_cmd = f'yt-dlp --flat-playlist --print "%(playlist_count)s" "{url}"'
    result = subprocess.run(check_cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
    playlist_count = result.stdout.strip()

    download_cmd = f'yt-dlp -f {fmt} -o "{folder}/%(title)s.%(ext)s" "{url}"'

    if playlist_count.isdigit() and int(playlist_count) > 1:
        rng = range_entry.get().strip()
        if rng:
            download_cmd = f'yt-dlp -f {fmt} --playlist-items {rng} -o "{folder}/%(title)s.%(ext)s" "{url}"'
        else:
            messagebox.showinfo("Playlist Detected", f"This is a playlist with {playlist_count} videos. Downloading all.")

    else:
        messagebox.showinfo("Single Video", "This is a single video.")

    threading.Thread(
        target=run_command,
        args=(download_cmd,),
        daemon=True
    ).start()

# Tkinter UI setup
root = tk.Tk()
root.title("YouTube Downloader (yt-dlp)")
root.geometry("700x500")

tk.Label(root, text="YouTube URL:").pack(anchor="w")
url_entry = tk.Entry(root, width=80)
url_entry.pack(fill="x")

tk.Label(root, text="Destination Folder:").pack(anchor="w")
folder_entry = tk.Entry(root, width=80)
folder_entry.pack(side="left", fill="x", expand=True)
tk.Button(root, text="Browse", command=browse_folder).pack(side="right")

tk.Label(root, text="Format Code (default 18):").pack(anchor="w")
format_entry = tk.Entry(root, width=10)
format_entry.pack(anchor="w")

tk.Label(root, text="Playlist Range (e.g., 1-5):").pack(anchor="w")
range_entry = tk.Entry(root, width=10)
range_entry.pack(anchor="w")

tk.Button(root, text="Show Formats", command=check_formats).pack(anchor="w", pady=5)
tk.Button(root, text="Download", command=start_download).pack(anchor="w", pady=5)

log_box = scrolledtext.ScrolledText(root, height=15)
log_box.pack(fill="both", expand=True)

root.mainloop()
