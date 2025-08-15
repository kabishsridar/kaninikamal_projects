import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse
import json

def choose_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Download Folder")
    return folder

def get_formats(video_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "-F", video_url],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        print(result.stdout)
    except Exception as e:
        print(f"Error fetching formats: {e}")

def download_video(url, output_path, format_code, playlist_items=None):
    command = ["yt-dlp", "-f", format_code, "-o", os.path.join(output_path, "%(title)s.%(ext)s")]

    if playlist_items:
        command.extend(["--playlist-items", playlist_items])

    command.append(url)

    try:
        subprocess.run(command)
    except Exception as e:
        print(f"Download failed: {e}")

def is_playlist(url):
    parsed = urlparse(url)
    return "list=" in parsed.query

def main():
    url = input("Enter YouTube video or playlist URL: ").strip()

    # Choose folder
    download_folder = choose_folder()
    if not download_folder:
        print("No folder selected. Exiting.")
        sys.exit()

    # Default format
    format_code = "18"

    # Ask if user wants to see available formats
    see_formats = input("Do you want to review available formats? (y/n): ").lower()
    if see_formats == "y":
        get_formats(url)
        chosen = input(f"Enter format code (default {format_code}): ").strip()
        if chosen:
            format_code = chosen

    playlist_items = None
    if is_playlist(url):
        print("This is a playlist.")
        playlist_range = input("Enter video range to download (e.g., 1-5) or press Enter for all: ").strip()
        if playlist_range:
            playlist_items = playlist_range

    # Extra option for audio only
    audio_only = input("Do you want to download audio only (MP3)? (y/n): ").lower()
    if audio_only == "y":
        format_code = "bestaudio"
        # Post-process to MP3
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", os.path.join(download_folder, "%(title)s.%(ext)s")
        ]
        if playlist_items:
            command.extend(["--playlist-items", playlist_items])
        command.append(url)
        subprocess.run(command)
        return

    # Download video
    download_video(url, download_folder, format_code, playlist_items)
    print("Download complete!")

if __name__ == "__main__":
    main()