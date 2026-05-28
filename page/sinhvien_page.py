import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from controller.sinhvien_controller import SinhvienController
from model.sinhvien_model import SinhvienModel

# ── Cấu hình hệ thống ─────────────────────────────────────────────────────────
SV_COLS = ["id", "masv", "hoten", "sdt", "diachi", "lop", "ma_nganh", "ngay_sinh", "gioi_tinh", "ghi_chu"]
DISPLAY_COLS = ["STT", "masv", "hoten", "sdt", "diachi", "lop", "ma_nganh", "ngay_sinh", "gioi_tinh", "ghi_chu"]

DISPLAY_HEADS = {
    "STT": "STT", "masv": "Mã SV", "hoten": "Họ tên", "sdt": "SĐT", "diachi": "Địa chỉ",
    "lop": "Lớp", "ma_nganh": "Mã ngành", "ngay_sinh": "Ngày sinh", "gioi_tinh": "Giới tính", "ghi_chu": "Ghi chú"
}
COL_W = {
    "STT": 45, "masv": 85, "hoten": 160, "sdt": 110, "diachi": 160,
    "lop": 80, "ma_nganh": 90, "ngay_sinh": 95, "gioi_tinh": 75, "ghi_chu": 110
}
FORM_FIELDS = [
    ("Mã sinh viên *", "masv"), ("Họ tên *", "hoten"), ("Số điện thoại", "sdt"),
    ("Địa chỉ", "diachi"), ("Lớp *", "lop"), ("Mã ngành *", "ma_nganh"),
    ("Ngày sinh *", "ngay_sinh"), ("Giới tính *", "gioi_tinh"), ("Ghi chú", "ghi_chu")
]

NGANH_FILE = "data/nganh.csv"


def _load_nganh_options():
    """Trả về list mã ngành từ file nganh.csv."""
    try:
        return pd.read_csv(NGANH_FILE, dtype=str)["ma_nganh"].dropna().tolist()
    except Exception:
        return []


class SinhvienPage(tk.Frame):

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.sv = SinhvienModel("data/sinhvien.csv", SV_COLS)
        self.dm = SinhvienModel("data/diem.csv", ["id", "masv", "hoten", "cc", "dk1", "dk2", "dt", "diem_trung_binh", "ghi_chu"])
        self.controller = SinhvienController(self.sv, self.dm)
        
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    # ── Giao diện ────────────────────────────────────────────────────────────

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Thông tin Sinh viên", font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm", lambda: self._open_form()), ("🔄 Làm mới", self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        # Tìm kiếm
        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_field = ttk.Combobox(toolbar, values=list(DISPLAY_HEADS.values()), width=10, state="readonly")
        self.search_field.current(2)  # mặc định: Họ tên
        self.search_field.pack(side="left")
        
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=18).pack(side="left", padx=4)
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left")

        tk.Button(toolbar, text="📤 Export CSV", command=self._export_csv).pack(side="right", padx=4)
        tk.Button(toolbar, text="📥 Import CSV", command=self._import_csv).pack(side="right", padx=4)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        self.tree = ttk.Treeview(tree_frame, columns=DISPLAY_COLS + ["sua", "xoa"], show="headings", height=15)
        for c in DISPLAY_COLS:
            self.tree.heading(c, text=DISPLAY_HEADS[c])
            self.tree.column(c, width=COL_W[c], anchor="center")
            
        self.tree.heading("sua", text="Sửa"); self.tree.column("sua", width=55, anchor="center")
        self.tree.heading("xoa", text="Xóa"); self.tree.column("xoa", width=55, anchor="center")

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
        for i, r in enumerate(data, 1):
            self.tree.insert("", "end", iid=str(r.get("id", "")), values=(
                i, r.get("masv", ""), r.get("hoten", ""), r.get("sdt", ""), r.get("diachi", ""), 
                r.get("lop", ""), r.get("ma_nganh", ""), r.get("ngay_sinh", ""), r.get("gioi_tinh", ""), 
                r.get("ghi_chu", ""), "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} sinh viên")

    def _on_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row: return

        col_idx = int(col.replace("#", "")) - 1
        all_cols = DISPLAY_COLS + ["sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""
        
        if col_name == "sua":
            rec = self.sv.get_by_id(row)
            if rec: self._open_form(rec)
        elif col_name == "xoa" and messagebox.askyesno("Xác nhận", "Xóa sinh viên này?"):
            self.controller.delete_student(row)
            self.tree.delete(row)
            self.status.config(text="Đã xóa sinh viên.")

    # ── Form Thêm / Sửa ───────────────────────────────────────────────────────

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa thông tin sinh viên" if is_edit else "Thêm sinh viên mới")
        win.geometry("440x500")
        win.resizable(False, False)
        win.grab_set()

        title_txt = "Sửa thông tin sinh viên" if is_edit else "Thêm sinh viên mới"
        tk.Label(win, text=title_txt, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        entries = {}
        nganh_options = _load_nganh_options()

        for i, (label, key) in enumerate(FORM_FIELDS):
            tk.Label(win, text=label, anchor="w").grid(row=i+1, column=0, sticky="w", padx=14, pady=3)
            
            if key in ["gioi_tinh", "ma_nganh"]:
                vals = ["Nam", "Nữ", "Khác"] if key == "gioi_tinh" else nganh_options
                e = ttk.Combobox(win, values=vals, width=26, state="readonly")
                e.grid(row=i+1, column=1, padx=10, pady=3, sticky="w")
                if data: e.set(data.get(key, ""))
                elif key == "ma_nganh" and nganh_options: e.current(0)
            else:
                e = tk.Entry(win, width=28)
                e.grid(row=i+1, column=1, padx=10, pady=3, sticky="w")
                if data: e.insert(0, data.get(key, ""))
                
            entries[key] = e

        def _luu():
            record = {k: entries[k].get().strip() for _, k in FORM_FIELDS}
            ok, msg = self.controller.save_student(record, is_edit, data["id"] if is_edit else None)
            if not ok:
                messagebox.showwarning("Lỗi", msg, parent=win)
                return
            win.destroy()
            self.load_data()
            messagebox.showinfo("Thành công", msg)

        ttk.Button(win, text="Lưu dữ liệu", command=_luu).grid(row=len(FORM_FIELDS)+1, column=0, columnspan=2, pady=15)

    def _tao_diem_trong(self, masv, hoten):
        existing = [r for r in self.dm.search("masv", masv) if str(r.get("masv", "")).strip() == masv]
        if existing: return
        
        self.dm.create({
            "id": self.dm.get_next_id(), "masv": masv, "hoten": hoten,
            "cc": "", "dk1": "", "dk2": "", "dt": "", "diem_trung_binh": "", "ghi_chu": "Chưa có điểm",
        })

    # ── Tiện ích ──────────────────────────────────────────────────────────────

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data(); return
            
        field_map = {v: k for k, v in DISPLAY_HEADS.items()}
        col = field_map.get(self.search_field.get(), "hoten")
        if col == "STT": col = "masv"
        
        result = self.controller.search_student(col, kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả cho '{kw}'")

    def _import_csv(self):
        from tkinter import filedialog
        import shutil

        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return

        def task():
            try:
                # Đọc kiểm tra dữ liệu
                df = pd.read_csv(path, dtype=str)
                required = {"masv", "hoten"}

                if not required.issubset(set(df.columns)):
                    missing = required - set(df.columns)
                    self.after(0, lambda: messagebox.showerror("Lỗi", f"File thiếu cột: {missing}"))
                    return

                # Copy file thô đè thẳng vào data
                shutil.copy(path, "data/sinhvien.csv")

                # Cập nhật giao diện và thông báo
                self.after(0, self.load_data)
                self.after(0, lambda: messagebox.showinfo("Import", f"Import thành công {len(df)} sinh viên!"))

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Lỗi", str(e)))

        self.app.run_async(task, "Đang import dữ liệu...")

    def _export_csv(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            shutil.copy("data/sinhvien.csv", path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")