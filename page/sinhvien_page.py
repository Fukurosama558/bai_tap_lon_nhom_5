import tkinter as tk
from tkinter import messagebox, ttk
from model.sinhvien import SinhvienModel
from theme import Theme


class SinhvienPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.sv = SinhvienModel("data/sinhvien.csv",
                                ['id','hoten','sdt','diachi','lop','tuoi'])
        self._hovered = None
        self.config()
        self.view()
        self.load_data()

    def config(self):
        self.master.title("Quản lý Sinh viên – Trường Đại học Hạ Long")
        self.master.geometry("1100x600")
        self.master.minsize(800, 500)
        self.master.resizable(True, True)
        self.master.configure(bg=Theme.BG)

    def view(self):
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self._build_statusbar()

    def _build_header(self):
        Theme.build_header(self.master, "Danh sách Sinh viên")

    def _build_toolbar(self):
        bar = tk.Frame(self.master, bg=Theme.WHITE,
                       highlightbackground=Theme.BORDER,
                       highlightthickness=1)
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=Theme.WHITE)
        left.pack(side="left", padx=14, pady=9)

        self.count_var = tk.StringVar(value="0 sinh viên")
        tk.Label(left, textvariable=self.count_var,
                 font=(Theme.FONT, 9, "bold"),
                 bg=Theme.PRIMARY_LIGHT, fg=Theme.WHITE,
                 padx=10, pady=4).pack(side="left", padx=(0, 10))

        Theme.make_btn(left, "＋  Thêm sinh viên",
                       self.create_sv, "primary").pack(side="left", padx=3)
        Theme.make_btn(left, "⟳  Làm mới",
                       self.load_data, "outline").pack(side="left", padx=3)

        # Tìm kiếm
        sf = tk.Frame(bar, bg=Theme.WHITE)
        sf.pack(side="right", padx=14, pady=9)
        sw = tk.Frame(sf, bg=Theme.BG,
                      highlightbackground=Theme.BORDER,
                      highlightthickness=1)
        sw.pack()
        tk.Label(sw, text="🔍", bg=Theme.BG,
                 fg=Theme.TEXT_LIGHT,
                 font=(Theme.FONT, 11)).pack(side="left", padx=(8, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        se = tk.Entry(sw, textvariable=self.search_var,
                      font=(Theme.FONT, 10),
                      relief="flat", bd=0,
                      bg=Theme.BG, fg=Theme.TEXT_DARK,
                      insertbackground=Theme.PRIMARY, width=22)
        se.pack(side="left", padx=8, ipady=6)
        se.bind("<FocusIn>",
                lambda e: sw.configure(highlightbackground=Theme.PRIMARY,
                                       highlightthickness=2))
        se.bind("<FocusOut>",
                lambda e: sw.configure(highlightbackground=Theme.BORDER,
                                       highlightthickness=1))

    def _build_table(self):
        outer = tk.Frame(self.master, bg=Theme.BG)
        outer.pack(expand=True, fill="both", padx=18, pady=(10, 0))

        sn = Theme.apply_treeview_style("SV.Treeview")
        cols = ("STT","hoten","sdt","diachi","lop","tuoi","Sửa","Xóa")
        self.tree = ttk.Treeview(outer, columns=cols,
                                 show="headings", height=15,
                                 style=sn, selectmode="browse")

        specs = [
            ("STT",   "STT",          55,  "center"),
            ("hoten", "Họ và tên",   210,  "w"),
            ("sdt",   "Số ĐT",       130,  "center"),
            ("diachi","Địa chỉ",     200,  "w"),
            ("lop",   "Lớp",         100,  "center"),
            ("tuoi",  "Tuổi",         70,  "center"),
            ("Sửa",   "",             72,  "center"),
            ("Xóa",   "",             72,  "center"),
        ]
        for col, label, width, anchor in specs:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)

        self.tree.tag_configure("even", background=Theme.WHITE,
                                foreground=Theme.TEXT_DARK)
        self.tree.tag_configure("odd",  background=Theme.ROW_ALT,
                                foreground=Theme.TEXT_DARK)
        self.tree.tag_configure("hover",background=Theme.ROW_HOVER,
                                foreground=Theme.TEXT_DARK)

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<Motion>",          self._on_hover)
        self.tree.bind("<Leave>",           self._on_leave)

        vsb = ttk.Scrollbar(outer, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Sẵn sàng")
        Theme.build_statusbar(self.master, self.status_var)

    # ── Dữ liệu ────────────────────────────────────────────────────
    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        data = self.sv.list(1, 10000)
        self._all_data = data["data"]
        self._render(self._all_data)

    def _render(self, rows):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for i, item in enumerate(rows, start=1):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end",
                             values=(item["id"],
                                     item["hoten"], item["sdt"],
                                     item["diachi"], item["lop"],
                                     item["tuoi"],
                                     "✏️  Sửa", "🗑️  Xóa"),
                             tags=(tag,))
        self.count_var.set(f"{len(rows)} sinh viên")
        self.status_var.set(f"Hiển thị {len(rows)} sinh viên")

    # ── Sự kiện ────────────────────────────────────────────────────
    def _on_search(self, *_):
        kw = self.search_var.get().lower().strip()
        filtered = self._all_data if not kw else [
            r for r in self._all_data
            if any(kw in str(v).lower() for v in r.values())
        ]
        self._render(filtered)

    def _on_tree_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        col_idx = int(self.tree.identify_column(event.x).replace("#","")) - 1
        row_id  = self.tree.identify_row(event.y)
        if not row_id:
            return
        col_name = ("STT","hoten","sdt","diachi","lop","tuoi","Sửa","Xóa")[col_idx]
        vals = self.tree.item(row_id)["values"]
        sv_id = str(vals[0])

        if col_name == "Sửa":
            self.app_manager.show_sua_sinhvien_page(sv_id)
        elif col_name == "Xóa":
            if messagebox.askyesno("Xác nhận xóa",
                                   f"Xóa sinh viên «{vals[1]}»?",
                                   icon="warning"):
                self.sv.delete("id", sv_id)
                self.tree.delete(row_id)
                self._all_data = [r for r in self._all_data
                                  if str(r["id"]) != sv_id]
                self.count_var.set(
                    f"{len(self.tree.get_children())} sinh viên")
                self.status_var.set(f"Đã xóa: {vals[1]}")

    def _on_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id != self._hovered:
            if self._hovered:
                tags = tuple(t for t in
                             self.tree.item(self._hovered,"tags")
                             if t != "hover")
                self.tree.item(self._hovered, tags=tags)
            if row_id:
                self.tree.item(row_id,
                               tags=self.tree.item(row_id,"tags")+("hover",))
            self._hovered = row_id

    def _on_leave(self, _):
        if self._hovered:
            tags = tuple(t for t in
                         self.tree.item(self._hovered,"tags")
                         if t != "hover")
            self.tree.item(self._hovered, tags=tags)
            self._hovered = None

    def create_sv(self):
        self.app_manager.show_them_sinhvien_page()