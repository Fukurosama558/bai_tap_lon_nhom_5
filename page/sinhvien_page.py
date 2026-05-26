import tkinter as tk
from tkinter import ttk, messagebox
from model.sinhvien_model import SinhvienModel

# Tất cả cột trong CSV (id dùng nội bộ, không hiển thị)
SV_COLS = ['id', 'masv', 'hoten', 'sdt', 'diachi', 'lop', 'tuoi', 'gioi_tinh', 'ghi_chu']

# Cột hiển thị (bỏ 'id')
DISPLAY_COLS = ['masv', 'hoten', 'sdt', 'diachi', 'lop', 'tuoi', 'gioi_tinh', 'ghi_chu']
DISPLAY_HEADS = {
    'masv': 'Mã SV', 'hoten': 'Họ tên', 'sdt': 'SĐT',
    'diachi': 'Địa chỉ', 'lop': 'Lớp', 'tuoi': 'Tuổi', 'gioi_tinh': 'Giới tính', 'ghi_chu': 'Ghi chú'
}
COL_W = {
    'masv': 90, 'hoten': 180, 'sdt': 120,
    'diachi': 180, 'lop': 90, 'tuoi': 65, 'gioi_tinh': 80, 'ghi_chu': 120
}

FORM_FIELDS = [
    ("Mã sinh viên *", "masv"),
    ("Họ tên *",       "hoten"),
    ("Số điện thoại",  "sdt"),
    ("Địa chỉ",        "diachi"),
    ("Lớp *",          "lop"),
    ("Tuổi",           "tuoi"),
    ("Giới tính",      "gioi_tinh"),
    ("Ghi chú",        "ghi_chu"),
]


class SinhvienPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.sv = SinhvienModel("data/sinhvien.csv", SV_COLS)
        self._build()
        self.load_data()
        self.pack(fill="both", expand=True)

    # ── Giao diện chính ───────────────────────────────────────────────────────

    def _build(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Thông tin Sinh viên",
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm", lambda: self._open_form()),
                         ("🔄 Làm mới", self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        # Tìm kiếm
        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_field = ttk.Combobox(
            toolbar, values=list(DISPLAY_HEADS.values()), width=10, state="readonly")
        self.search_field.current(1)   # mặc định: Họ tên
        self.search_field.pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=18).pack(side="left", padx=4)
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left")

        tk.Button(toolbar, text="📥 Import CSV", command=self._import_csv).pack(side="right", padx=4)
        tk.Button(toolbar, text="📤 Export CSV", command=self._export_csv).pack(side="right", padx=4)
        tk.Button(toolbar, text="ℹ️ About",       command=self._about).pack(side="right", padx=4)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        tree_cols = DISPLAY_COLS + ["sua", "xoa"]
        self.tree = ttk.Treeview(tree_frame, columns=tree_cols, show="headings", height=15)

        for c in DISPLAY_COLS:
            self.tree.heading(c, text=DISPLAY_HEADS[c])
            self.tree.column(c, width=COL_W[c], anchor="center")
        self.tree.heading("sua", text="Sửa")
        self.tree.column("sua", width=60, anchor="center")
        self.tree.heading("xoa", text="Xóa")
        self.tree.column("xoa", width=60, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self._on_click)

        self.status = tk.Label(self, text="", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

    # ── Dữ liệu ──────────────────────────────────────────────────────────────

    def load_data(self, records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = records if records is not None else self.sv.list_all()
        for r in data:
            # Lưu id vào iid của treeview để dùng nội bộ, không hiển thị
            self.tree.insert("", "end", iid=str(r.get("id", "")), values=(
                r.get("masv", ""), r.get("hoten", ""), r.get("sdt", ""),
                r.get("diachi", ""), r.get("lop", ""), r.get("tuoi", ""),
                r.get("gioi_tinh", ""), r.get("ghi_chu", ""),
                "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} sinh viên")

    def _on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return
        col_idx = int(col.replace("#", "")) - 1
        all_cols = DISPLAY_COLS + ["sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""

        # row chính là id (vì dùng iid=id khi insert)
        id_val = row

        if col_name == "sua":
            rec = self.sv.get_by_id(id_val)
            if rec:
                self._open_form(rec)
        elif col_name == "xoa":
            if messagebox.askyesno("Xác nhận", "Xóa sinh viên này?"):
                self.sv.delete(id_val)
                self.tree.delete(row)
                self.status.config(text="Đã xóa sinh viên.")

    # ── Form Thêm / Sửa (popup giống trang điểm) ─────────────────────────────

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa thông tin sinh viên" if is_edit else "Thêm sinh viên mới")
        win.geometry("420x310")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Sửa thông tin sinh viên" if is_edit else "Thêm sinh viên mới",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        entries = {}
        for i, (label, key) in enumerate(FORM_FIELDS):
            tk.Label(win, text=label, anchor="w").grid(
                row=i + 1, column=0, sticky="w", padx=14, pady=3)
            e = tk.Entry(win, width=28)
            e.grid(row=i + 1, column=1, padx=10, pady=3, sticky="w")
            if data:
                e.insert(0, data.get(key, ""))
            entries[key] = e

        def _luu():
            masv  = entries["masv"].get().strip()
            hoten = entries["hoten"].get().strip()
            lop   = entries["lop"].get().strip()
            tuoi  = entries["tuoi"].get().strip()

            if not masv:
                messagebox.showwarning("Lỗi", "Vui lòng nhập Mã sinh viên!", parent=win)
                return
            if not hoten:
                messagebox.showwarning("Lỗi", "Vui lòng nhập Họ tên!", parent=win)
                return
            if not lop:
                messagebox.showwarning("Lỗi", "Vui lòng nhập Lớp!", parent=win)
                return
            if tuoi and not tuoi.isdigit():
                messagebox.showwarning("Lỗi", "Tuổi phải là số nguyên!", parent=win)
                return

            record = {k: entries[k].get().strip() for _, k in FORM_FIELDS}

            if is_edit:
                self.sv.update(data["id"], record)
            else:
                record["id"] = self.sv.get_next_id()
                self.sv.create(record)

            win.destroy()
            self.load_data()

        btn_row = len(FORM_FIELDS) + 1
        btn_frame = tk.Frame(win)
        btn_frame.grid(row=btn_row, column=0, columnspan=2, pady=12)
        tk.Button(btn_frame, text="💾 Lưu",  command=_luu,        width=12).pack(side="left", padx=6)
        tk.Button(btn_frame, text="❌ Hủy",  command=win.destroy, width=12).pack(side="left", padx=6)

    # ── Tiện ích ──────────────────────────────────────────────────────────────

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data()
            return
        field_map = {v: k for k, v in DISPLAY_HEADS.items()}
        col = field_map.get(self.search_field.get(), "hoten")
        result = self.sv.search(col, kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả cho '{kw}'")

    def _import_csv(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            shutil.copy(path, "data/sinhvien.csv")
            self.load_data()
            messagebox.showinfo("Import", "Import CSV thành công!")

    def _export_csv(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")])
        if path:
            shutil.copy("data/sinhvien.csv", path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")

    def _about(self):
        messagebox.showinfo("About",
            "Phần mềm Quản lý Sinh viên ĐHHL\n"
            "Phiên bản: 1.0\n"
            "Nhóm: ...\n"
            "Ngày phát hành: 2025")
