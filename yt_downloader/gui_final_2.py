import os
import re
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse, parse_qs

# -------- Helpers --------

def is_playlist(url: str) -> bool:
    try:
        q = parse_qs(urlparse(url).query)
        return 'list' in q and bool(q['list'])
    except Exception:
        return False

def yt_run_stream(cmd_args, line_cb, done_cb):
    """
    Run yt-dlp with streamed stdout in a background thread.
    line_cb: called in main thread via .after with each output line.
    done_cb: called in main thread when process exits (returncode).
    """
    def worker():
        try:
            proc = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace'
            )
            for line in proc.stdout:
                app.after(0, line_cb, line.rstrip('\n'))
            proc.wait()
            app.after(0, done_cb, proc.returncode)
        except Exception as e:
            app.after(0, line_cb, f"[error] {e}")
            app.after(0, done_cb, 1)
    threading.Thread(target=worker, daemon=True).start()

# -------- App --------

class YTDLPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader (yt-dlp)")
        self.geometry("900x600")
        self.minsize(820, 520)

        # Grid weights (responsive)
        self.grid_rowconfigure(3, weight=1)   # log area grows
        self.grid_columnconfigure(0, weight=1)

        # URL row
        frm_url = ttk.Frame(self)
        frm_url.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        frm_url.grid_columnconfigure(1, weight=1)

        ttk.Label(frm_url, text="YouTube URL:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_url = tk.StringVar()
        self.ent_url = ttk.Entry(frm_url, textvariable=self.var_url)
        self.ent_url.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm_url, text="Check", command=self.on_check_url).grid(row=0, column=2, padx=(8,0))

        self.var_kind = tk.StringVar(value="")
        self.lbl_kind = ttk.Label(self, textvariable=self.var_kind, foreground="#125")
        self.lbl_kind.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="w")

        # Destination + format row
        frm_opts = ttk.Frame(self)
        frm_opts.grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        for c in (1, 4):
            frm_opts.grid_columnconfigure(c, weight=1)

        # Folder
        ttk.Label(frm_opts, text="Destination:").grid(row=0, column=0, sticky="w")
        self.var_folder = tk.StringVar()
        self.ent_folder = ttk.Entry(frm_opts, textvariable=self.var_folder)
        self.ent_folder.grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(frm_opts, text="Browse", command=self.on_browse).grid(row=0, column=2, padx=(0, 12))

        # Format
        ttk.Label(frm_opts, text="Format code:").grid(row=0, column=3, sticky="e")
        self.var_fmt = tk.StringVar(value="18")
        self.ent_fmt = ttk.Entry(frm_opts, width=10, textvariable=self.var_fmt)
        self.ent_fmt.grid(row=0, column=4, sticky="w", padx=(6, 0))
        ttk.Button(frm_opts, text="Show Formats", command=self.on_show_formats).grid(row=0, column=5, padx=(12, 0))

        # Playlist range (shown only when playlist)
        frm_range = ttk.Frame(self)
        frm_range.grid(row=2, column=0, padx=12, pady=(42, 0), sticky="ew")  # placeholder space; hidden by default
        self.frm_range = frm_range
        for c in (1,):
            frm_range.grid_columnconfigure(c, weight=1)
        ttk.Label(frm_range, text="Playlist range (e.g., 1-5 or 1,3,7):").grid(row=0, column=0, sticky="w")
        self.var_range = tk.StringVar()
        self.ent_range = ttk.Entry(frm_range, width=20, textvariable=self.var_range)
        self.ent_range.grid(row=0, column=1, sticky="w", padx=(6, 0))
        frm_range.grid_remove()  # hidden initially

        # Log / output
        frm_log = ttk.Frame(self)
        frm_log.grid(row=3, column=0, padx=12, pady=6, sticky="nsew")
        frm_log.grid_rowconfigure(0, weight=1)
        frm_log.grid_columnconfigure(0, weight=1)

        self.txt = tk.Text(frm_log, wrap="word")
        self.txt.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(frm_log, orient="vertical", command=self.txt.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.txt.configure(yscrollcommand=yscroll.set)

        # Progress row
        frm_prog = ttk.Frame(self)
        frm_prog.grid(row=4, column=0, padx=12, pady=(0, 6), sticky="ew")
        frm_prog.grid_columnconfigure(0, weight=1)
        self.prog = ttk.Progressbar(frm_prog, mode="determinate", maximum=100)
        self.prog.grid(row=0, column=0, sticky="ew")
        self.var_prog = tk.StringVar(value="")
        ttk.Label(frm_prog, textvariable=self.var_prog, width=16).grid(row=0, column=1, padx=(8,0))

        # Action buttons
        frm_btns = ttk.Frame(self)
        frm_btns.grid(row=5, column=0, padx=12, pady=(0, 12), sticky="e")
        self.btn_download = ttk.Button(frm_btns, text="Download", command=self.on_download)
        self.btn_download.grid(row=0, column=0, padx=(0, 8))
        self.btn_stop = ttk.Button(frm_btns, text="Stop", command=self.on_stop, state="disabled")
        self.btn_stop.grid(row=0, column=1)

        # runtime state
        self._current_proc = None

    # ------- UI callbacks -------

    def on_browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.var_folder.set(folder)

    def on_check_url(self):
        url = self.var_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if is_playlist(url):
            self.var_kind.set("This is a playlist.")
            self.frm_range.grid()  # show playlist range row
        else:
            self.var_kind.set("This is a video.")
            self.frm_range.grid_remove()

    def on_show_formats(self):
        url = self.var_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        self._reset_progress("Fetching formats...")
        self._append_log("[info] Running: yt-dlp -F URL\n")

        def on_line(line):
            self._append_log(line)

        def on_done(rc):
            if rc == 0:
                self._set_progress_text("Formats fetched.")
            else:
                self._set_progress_text("Failed to fetch formats.")
            self._unlock_buttons()

        self._lock_buttons()
        yt_run_stream(["yt-dlp", "-F", url], on_line, on_done)

    def on_download(self):
        url = self.var_url.get().strip()
        folder = self.var_folder.get().strip()
        fmt = (self.var_fmt.get().strip() or "18")
        rng = self.var_range.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not folder:
            messagebox.showerror("Error", "Please choose a destination folder.")
            return

        out_tpl = os.path.join(folder, "%(title)s.%(ext)s")

        cmd = ["yt-dlp", "-o", out_tpl]
        # default format
        cmd += ["-f", fmt]
        # playlist items if provided
        if rng:
            cmd += ["--playlist-items", rng]
        cmd += [url]

        self._reset_progress("Starting download...")
        self._append_log(f"[info] Running: {' '.join(cmd)}\n")

        pct_regex = re.compile(r'(\d{1,3}(?:\.\d+)?)%')
        self.btn_download.config(state="disabled")
        self.btn_stop.config(state="normal")

        def on_line(line):
            # Update progress bar if a % appears
            m = pct_regex.search(line)
            if m:
                try:
                    pct = float(m.group(1))
                    pct = max(0.0, min(100.0, pct))
                    self.prog['value'] = pct
                    self.var_prog.set(f"{pct:.1f}%")
                except ValueError:
                    pass
            self._append_log(line)

        def on_done(rc):
            if rc == 0:
                self._set_progress_text("Done.")
                self.prog['value'] = 100
                self.var_prog.set("100.0%")
                messagebox.showinfo("Success", "Download complete!")
            else:
                self._set_progress_text("Download failed.")
                messagebox.showerror("Error", "Download failed.")
            self._unlock_buttons()

        # run
        self._lock_buttons()
        yt_run_stream(cmd, on_line, on_done)

    def on_stop(self):
        try:
            if self._current_proc and self._current_proc.poll() is None:
                self._current_proc.terminate()
        except Exception:
            pass

    # ------- small UI helpers -------

    def _append_log(self, text):
        self.txt.insert("end", text + ("\n" if not text.endswith("\n") else ""))
        self.txt.see("end")

    def _reset_progress(self, msg=""):
        self.txt.delete("1.0", "end")
        self.prog['value'] = 0
        self.var_prog.set("")
        if msg:
            self._set_progress_text(msg)

    def _set_progress_text(self, msg):
        self.var_prog.set(msg)

    def _lock_buttons(self):
        self.btn_download.config(state="disabled")
        self.btn_stop.config(state="normal")

    def _unlock_buttons(self):
        self.btn_download.config(state="normal")
        self.btn_stop.config(state="disabled")


# create and run
app = YTDLPApp()
app.mainloop()
