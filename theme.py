"""
theme.py – Bảng màu & helper chung
Trường Đại học Hạ Long
"""
import tkinter as tk
from tkinter import ttk


class Theme:
    PRIMARY       = "#3b5998"
    PRIMARY_DARK  = "#2d4473"
    PRIMARY_LIGHT = "#5b79b8"
    WHITE         = "#ffffff"
    BG            = "#f0f4ff"
    ROW_ALT       = "#e8edf8"
    ROW_HOVER     = "#cfd9f5"
    TEXT_DARK     = "#1a2540"
    TEXT_LIGHT    = "#6b7a9e"
    TEXT_MUTED    = "#a0aec8"
    DANGER        = "#e74c3c"
    DANGER_DARK   = "#c0392b"
    SUCCESS       = "#27ae60"
    BORDER        = "#c5cfe8"
    FONT          = "Segoe UI"

    @classmethod
    def apply_treeview_style(cls, style_name="App.Treeview"):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(style_name,
                        background=cls.WHITE,
                        fieldbackground=cls.WHITE,
                        foreground=cls.TEXT_DARK,
                        rowheight=36,
                        font=(cls.FONT, 10),
                        borderwidth=0)
        style.configure(f"{style_name}.Heading",
                        background=cls.PRIMARY,
                        foreground=cls.WHITE,
                        font=(cls.FONT, 10, "bold"),
                        relief="flat",
                        padding=(8, 10))
        style.map(style_name,
                  background=[("selected", cls.PRIMARY_LIGHT)],
                  foreground=[("selected", cls.WHITE)])
        style.map(f"{style_name}.Heading",
                  background=[("active", cls.PRIMARY_DARK)])
        style.layout(style_name,
                     [(f"{style_name}.treearea", {"sticky": "nswe"})])
        return style_name

    @classmethod
    def make_btn(cls, parent, text, command, variant="primary",
                 padx=12, pady=6):
        presets = {
            "primary": (cls.PRIMARY,      cls.WHITE,      cls.PRIMARY_DARK),
            "outline":  (cls.WHITE,        cls.PRIMARY,    cls.BG),
            "danger":   (cls.DANGER,       cls.WHITE,      cls.DANGER_DARK),
            "ghost":    (cls.BG,           cls.TEXT_DARK,  cls.ROW_HOVER),
        }
        bg, fg, abg = presets.get(variant, presets["primary"])
        ht = 1 if variant == "outline" else 0
        btn = tk.Button(parent, text=text, command=command,
                        font=(cls.FONT, 9, "bold"),
                        bg=bg, fg=fg,
                        activebackground=abg, activeforeground=fg,
                        relief="flat", bd=0, cursor="hand2",
                        padx=padx, pady=pady,
                        highlightthickness=ht,
                        highlightbackground=cls.BORDER)
        btn.bind("<Enter>", lambda e: btn.configure(bg=abg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    @classmethod
    def build_header(cls, master, subtitle, back_cmd=None):
        header = tk.Frame(master, bg=cls.PRIMARY, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        logo = tk.Frame(header, bg=cls.WHITE, width=42, height=42)
        logo.pack(side="left", padx=16, pady=11)
        logo.pack_propagate(False)
        tk.Label(logo, text="HL", font=(cls.FONT, 13, "bold"),
                 bg=cls.WHITE, fg=cls.PRIMARY
                 ).place(relx=.5, rely=.5, anchor="center")

        blk = tk.Frame(header, bg=cls.PRIMARY)
        blk.pack(side="left", pady=8)
        tk.Label(blk, text="TRƯỜNG ĐẠI HỌC HẠ LONG",
                 font=(cls.FONT, 8, "bold"),
                 bg=cls.PRIMARY, fg="#b8c8ec").pack(anchor="w")
        tk.Label(blk, text=subtitle,
                 font=(cls.FONT, 14, "bold"),
                 bg=cls.PRIMARY, fg=cls.WHITE).pack(anchor="w")

        if back_cmd:
            btn = tk.Button(header, text="⬅  Quay lại",
                            font=(cls.FONT, 9),
                            bg=cls.PRIMARY_DARK, fg=cls.WHITE,
                            activebackground=cls.PRIMARY_LIGHT,
                            activeforeground=cls.WHITE,
                            relief="flat", bd=0, cursor="hand2",
                            padx=12, pady=7, command=back_cmd)
            btn.bind("<Enter>",
                     lambda e: btn.configure(bg=cls.PRIMARY_LIGHT))
            btn.bind("<Leave>",
                     lambda e: btn.configure(bg=cls.PRIMARY_DARK))
            btn.pack(side="right", padx=16, pady=16)

    @classmethod
    def build_statusbar(cls, master, status_var):
        bar = tk.Frame(master, bg=cls.PRIMARY_DARK, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Label(bar, textvariable=status_var,
                 bg=cls.PRIMARY_DARK, fg="#b8c8ec",
                 font=(cls.FONT, 8), anchor="w",
                 padx=14).pack(side="left", fill="y")
        tk.Label(bar, text="Trường Đại học Hạ Long  •  Phòng Đào tạo",
                 bg=cls.PRIMARY_DARK, fg="#6b80a8",
                 font=(cls.FONT, 8), anchor="e",
                 padx=14).pack(side="right", fill="y")

    @classmethod
    def make_entry(cls, parent, bg="#ffffff"):
        wrap = tk.Frame(parent, bg=bg,
                        highlightbackground=cls.BORDER,
                        highlightthickness=1)
        entry = tk.Entry(wrap, font=(cls.FONT, 10),
                         bg=bg, fg=cls.TEXT_DARK,
                         relief="flat", bd=0,
                         insertbackground=cls.PRIMARY)
        entry.pack(fill="x", padx=8, ipady=7)
        entry.bind("<FocusIn>",
                   lambda e: wrap.configure(
                       highlightbackground=cls.PRIMARY,
                       highlightthickness=2))
        entry.bind("<FocusOut>",
                   lambda e: wrap.configure(
                       highlightbackground=cls.BORDER,
                       highlightthickness=1))
        return wrap, entry