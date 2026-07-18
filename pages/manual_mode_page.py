"""
Manual Mode Page - User inputs clip timestamps manually without AI.
Supports adding multiple clips at once.
"""

import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

from components.page_layout import PageFooter


class ManualModePage(ctk.CTkFrame):
    """Page for manually defining highlight clips (no AI)"""

    def __init__(self, parent, on_back_callback, on_process_callback):
        super().__init__(parent)
        self.on_back = on_back_callback
        self.on_process = on_process_callback

        self.url_var = ctk.StringVar()
        self.caption_var = ctk.BooleanVar(value=False)
        self.hook_var = ctk.BooleanVar(value=False)

        self.clips = []  # list of dicts: {start, end, title, hook}
        self._row_widgets = []  # list of (frame, dict of widgets) for live editing

        self.create_ui()

    def create_ui(self):
        self.configure(fg_color=("#1a1a1a", "#0a0a0a"))

        from components.page_layout import PageHeader
        header = PageHeader(self, self, show_nav_buttons=True, show_back_button=True,
                            page_title="Manual Mode")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(self, text="Define clips yourself — no AI needed. Add as many clips as you want.",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        # URL input
        url_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray15"), corner_radius=8)
        url_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(url_frame, text="YouTube URL", font=ctk.CTkFont(size=11, weight="bold"),
                     anchor="w").pack(fill="x", padx=12, pady=(8, 3))
        entry_row = ctk.CTkFrame(url_frame, fg_color="transparent")
        entry_row.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkEntry(entry_row, textvariable=self.url_var,
                     placeholder_text="Paste YouTube link...", height=32,
                     border_width=1, border_color=("#3a3a3a", "#2a2a2a"),
                     fg_color=("#1a1a1a", "#0a0a0a")).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(entry_row, text="📋 Paste", width=70, height=32,
                      fg_color=("#3a3a3a", "#2a2a2a"), hover_color=("#4a4a4a", "#3a3a3a"),
                      font=ctk.CTkFont(size=10),
                      command=lambda: self.url_var.set(self.clipboard_get().strip())).pack(side="left")

        # Enhancement options
        options_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray15"), corner_radius=8)
        options_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(options_frame, text="Enhancements",
                     font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 5))

        for label, var, cmd in (
            ("💬 Add Captions", self.caption_var, self._update_caption_text),
            ("🪝 Add Hook Text", self.hook_var, self._update_hook_text),
        ):
            row = ctk.CTkFrame(options_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=(0, 6))
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=10), anchor="w").pack(side="left")
            switch = ctk.CTkSwitch(row, text="OFF", variable=var, width=36, height=18, command=cmd)
            switch.pack(side="right")
            if label.startswith("💬"):
                self.caption_switch = switch
            else:
                self.hook_switch = switch
        ctk.CTkLabel(options_frame, text="(Captions & Hook are free — burned from subtitles, no API needed)",
                     font=ctk.CTkFont(size=9), text_color="gray").pack(anchor="w", padx=12, pady=(0, 8))

        # Clips list (scrollable)
        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkLabel(list_header, text="Clips", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(list_header, text="+ Add Clip", width=100, height=30,
                      fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#2E7AB8", "#16527D"),
                      font=ctk.CTkFont(size=11), command=self.add_clip_row).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Bottom action buttons (pinned to bottom so it's always visible)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 10))

        self.process_btn = ctk.CTkButton(bottom_frame, text="🎬 Process All Clips", height=45,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         command=self.process_all,
                                         fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#2E7AB8", "#16527D"))
        self.process_btn.pack(fill="x")

        footer = PageFooter(self, self)
        footer.pack(side="bottom", fill="x", padx=20, pady=(10, 15))

        self._refresh_list()

    def add_clip_row(self):
        """Add a new empty clip row"""
        self.clips.append({"start": "", "end": "", "title": "", "hook": ""})
        self._refresh_list()

    def _remove_clip(self, index):
        self.clips.pop(index)
        self._refresh_list()

    def _refresh_list(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        self._row_widgets = []

        if not self.clips:
            ctk.CTkLabel(self.list_frame, text="No clips yet. Click '+ Add Clip' to add one.",
                         font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
            return

        for i, clip in enumerate(self.clips):
            card = ctk.CTkFrame(self.list_frame, fg_color=("gray85", "gray20"), corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=12, pady=10)

            # Row 1: Start / End
            t_row = ctk.CTkFrame(content, fg_color="transparent")
            t_row.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(t_row, text="#{}".format(i + 1), font=ctk.CTkFont(size=12, weight="bold"),
                         width=30, anchor="w").pack(side="left")

            ctk.CTkLabel(t_row, text="Start", font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 4))
            start_e = ctk.CTkEntry(t_row, placeholder_text="HH:MM:SS", height=28, width=110,
                                   fg_color=("#2b2b2b", "#1a1a1a"))
            start_e.insert(0, clip.get("start", ""))
            start_e.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(t_row, text="End", font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 4))
            end_e = ctk.CTkEntry(t_row, placeholder_text="HH:MM:SS", height=28, width=110,
                                 fg_color=("#2b2b2b", "#1a1a1a"))
            end_e.insert(0, clip.get("end", ""))
            end_e.pack(side="left", padx=(0, 10))

            ctk.CTkButton(t_row, text="🗑", width=32, height=28,
                          fg_color=("#5a2a2a", "#3a1a1a"), hover_color=("#7a3a3a", "#5a2a2a"),
                          command=lambda idx=i: self._remove_clip(idx)).pack(side="right")

            # Row 2: Title
            title_row = ctk.CTkFrame(content, fg_color="transparent")
            title_row.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(title_row, text="Title", font=ctk.CTkFont(size=10), width=50, anchor="w").pack(side="left")
            title_e = ctk.CTkEntry(title_row, placeholder_text="Clip title", height=28,
                                   fg_color=("#2b2b2b", "#1a1a1a"))
            title_e.insert(0, clip.get("title", ""))
            title_e.pack(side="left", fill="x", expand=True)

            # Row 3: Hook (optional)
            hook_row = ctk.CTkFrame(content, fg_color="transparent")
            hook_row.pack(fill="x")
            ctk.CTkLabel(hook_row, text="Hook", font=ctk.CTkFont(size=10), width=50, anchor="w").pack(side="left")
            hook_e = ctk.CTkEntry(hook_row, placeholder_text="Optional hook text (if Add Hook enabled)",
                                  height=28, fg_color=("#2b2b2b", "#1a1a1a"))
            hook_e.insert(0, clip.get("hook", ""))
            hook_e.pack(side="left", fill="x", expand=True)

            self._row_widgets.append({
                "start": start_e, "end": end_e, "title": title_e, "hook": hook_e
            })

    def _collect_clips(self):
        """Read values from entries back into self.clips"""
        for clip, widgets in zip(self.clips, self._row_widgets):
            clip["start"] = widgets["start"].get().strip()
            clip["end"] = widgets["end"].get().strip()
            clip["title"] = widgets["title"].get().strip()
            clip["hook"] = widgets["hook"].get().strip()

    def process_all(self):
        self._collect_clips()

        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Please paste the YouTube URL first.")
            return

        valid = []
        for idx, clip in enumerate(self.clips, 1):
            start = clip.get("start", "")
            end = clip.get("end", "")
            if not start or not end:
                messagebox.showerror("Incomplete Clip",
                                     "Clip #{} is missing start or end time.".format(idx))
                return
            if not self._is_valid_ts(start) or not self._is_valid_ts(end):
                messagebox.showerror("Invalid Time",
                                     "Clip #{} has an invalid time. Use HH:MM:SS.".format(idx))
                return
            if self._to_sec(end) <= self._to_sec(start):
                messagebox.showerror("Invalid Range",
                                     "Clip #{} end time must be after start time.".format(idx))
                return
            title = clip.get("title") or "Clip {}".format(idx)
            highlight = {
                "start_time": self._normalize(start),
                "end_time": self._normalize(end),
                "title": title,
                "description": title,
                "virality_score": 0,
            }
            if clip.get("hook"):
                highlight["hook_text"] = clip["hook"]
            valid.append(highlight)

        if not valid:
            messagebox.showwarning("No Clips", "Add at least one clip before processing.")
            return

        add_captions = self.caption_var.get()
        add_hook = self.hook_var.get()

        self.on_process(url, valid, add_captions, add_hook)

    # ---------- helpers ----------
    @staticmethod
    def _is_valid_ts(ts):
        parts = ts.split(":")
        if len(parts) != 3:
            return False
        try:
            h, m, s = (int(p) for p in parts)
            return 0 <= m < 60 and 0 <= s < 60 and h >= 0
        except ValueError:
            return False

    @staticmethod
    def _to_sec(ts):
        h, m, s = (int(p) for p in ts.split(":"))
        return h * 3600 + m * 60 + s

    @staticmethod
    def _normalize(ts):
        h, m, s = ts.split(":")
        return "{:02d}:{:02d}:{:02d},000".format(int(h), int(m), int(s))

    def _update_caption_text(self):
        self.caption_switch.configure(text="ON" if self.caption_var.get() else "OFF")

    def _update_hook_text(self):
        self.hook_switch.configure(text="ON" if self.hook_var.get() else "OFF")

    def show_page(self, page_name):
        pass

    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/fharahap85/yt-clipper")
