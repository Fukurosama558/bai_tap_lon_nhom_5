import tkinter as tk
from tkinter import ttk, messagebox
from model.sinhvien_model import SinhvienModel
import os, pandas as pd

NGANH_COLS  = ['id', 'ma_nganh', 'ten_nganh', 'mo_ta']
NGANH_HEADS = {'id': 'STT', 'ma_nganh': 'Mã ngành', 'ten_nganh': 'Tên ngành', 'mo_ta': 'Mô tả'}
COL_W       = {'id': 50, 'ma_nganh': 120, 'ten_nganh': 250, 'mo_ta': 300}

NGANH_FILE  = "data/nganh.csv"

def _ensure_nganh_file():
    """Tạo file nganh.csv mặc định nếu chưa tồn tại."""
    if not os.path.exists(NGANH_FILE):
        df = pd.DataFrame([
            {"id": 1, "ma_nganh": "CNTT", "ten_nganh": "Công nghệ Thông tin", "mo_ta": "Ngành CNTT"},
            {"id": 2, "ma_nganh": "QTKD", "ten_nganh": "Quản trị Kinh doanh", "mo_ta": "Ngành QTKD"},
            {"id": 3, "ma_nganh": "KT",   "ten_nganh": "Kế toán",              "mo_ta": "Ngành Kế toán"},
        ])
        df.to_csv(NGANH_FILE, index=False)


class NganhPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        _ensure_nganh_file()
        self.nm = SinhvienModel(NGANH_FILE, NGANH_COLS)
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Quản lý Ngành học",
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm ngành", lambda: self._open_form()),
                         ("🔄 Làm mới",   self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=18).pack(side="left")
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left", padx=4)

        tk.Button(toolbar, text="📤 Export", command=self._export).pack(side="right", padx=4)
        tk.Button(toolbar, text="ℹ️ About",  command=self._about).pack(side="right", padx=4)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        cols = NGANH_COLS + ["sua", "xoa"]
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        for c in NGANH_COLS:
            self.tree.heading(c, text=NGANH_HEADS[c])
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

    def load_data(self, records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = records if records is not None else self.nm.list_all()
        for r in data:
            self.tree.insert("", "end", iid=str(r.get("id", "")), values=(
                r.get("id",""), r.get("ma_nganh",""), r.get("ten_nganh",""),
                r.get("mo_ta",""), "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} ngành học")

    def _on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row: return
        col_idx = int(col.replace("#", "")) - 1
        all_cols = NGANH_COLS + ["sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""
        id_val = row
        if col_name == "sua":
            rec = self.nm.get_by_id(id_val)
            if rec: self._open_form(rec)
        elif col_name == "xoa":
            if messagebox.askyesno("Xác nhận", "Xóa ngành học này?"):
                self.nm.delete(id_val)
                self.tree.delete(row)

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data(); return
        result = self.nm.search("ten_nganh", kw)
        if not result:
            result = self.nm.search("ma_nganh", kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả")

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa ngành học" if is_edit else "Thêm ngành học")
        win.geometry("420x240")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Sửa ngành học" if is_edit else "Thêm ngành học mới",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [("Mã ngành *",  "ma_nganh"),
                  ("Tên ngành *", "ten_nganh"),
                  ("Mô tả",       "mo_ta")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(win, text=label, anchor="w").grid(
                row=i+1, column=0, sticky="w", padx=14, pady=5)
            e = tk.Entry(win, width=30)
            e.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
            if data:
                e.insert(0, data.get(key, ""))
            entries[key] = e

        def _luu():
            ma    = entries["ma_nganh"].get().strip()
            ten   = entries["ten_nganh"].get().strip()
            mo_ta = entries["mo_ta"].get().strip()
            if not ma:
                messagebox.showwarning("Lỗi", "Vui lòng nhập Mã ngành!", parent=win); return
            if not ten:
                messagebox.showwarning("Lỗi", "Vui lòng nhập Tên ngành!", parent=win); return

            # Kiểm tra trùng mã ngành khi thêm mới
            if not is_edit:
                existing = self.nm.search("ma_nganh", ma)
                exact = [r for r in existing if str(r.get("ma_nganh","")).strip().upper() == ma.upper()]
                if exact:
                    messagebox.showwarning("Lỗi", f"Mã ngành '{ma}' đã tồn tại!", parent=win); return

            record = {"ma_nganh": ma.upper(), "ten_nganh": ten, "mo_ta": mo_ta}
            if is_edit:
                self.nm.update(data["id"], record)
            else:
                record["id"] = self.nm.get_next_id()
                self.nm.create(record)
            win.destroy()
            self.load_data()

        btn_frame = tk.Frame(win)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=12)
        tk.Button(btn_frame, text="💾 Lưu", command=_luu,        width=12).pack(side="left", padx=6)
        tk.Button(btn_frame, text="❌ Hủy", command=win.destroy, width=12).pack(side="left", padx=6)

    def _export(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if path:
            shutil.copy(NGANH_FILE, path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")

    def _about(self):
        messagebox.showinfo("About – Ngành học",
            "Module: Quản lý Ngành học\n"
            "Phiên bản: 1.0\n"
            "─────────────────────────\n"
            "Phần mềm Quản lý Sinh viên ĐHHL\n"
            "Nhóm: ...  |  Năm: 2025")
