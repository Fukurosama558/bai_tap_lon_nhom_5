import tkinter as tk
from tkinter import ttk, messagebox
from model.sinhvien_model import SinhvienModel

DIEM_COLS  = ['id', 'masv', 'hoten', 'diem_giua_ky', 'diem_cuoi_ky', 'diem_trung_binh', 'ghi_chu']
DIEM_HEADS = {
    'id': 'STT', 'masv': 'Mã SV', 'hoten': 'Họ tên',
    'diem_giua_ky': 'ĐGK', 'diem_cuoi_ky': 'ĐCK',
    'diem_trung_binh': 'ĐTB', 'ghi_chu': 'Xếp loại'
}
COL_W = {'id': 50, 'masv': 90, 'hoten': 180,
          'diem_giua_ky': 80, 'diem_cuoi_ky': 80,
          'diem_trung_binh': 80, 'ghi_chu': 110}
PASS_MARK = 5.0


class DiemPage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.dm = SinhvienModel("data/diem.csv", DIEM_COLS)
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Bảng điểm sinh viên",
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm điểm", self._them),
                         ("🔄 Làm mới",   self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        # Tìm kiếm
        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=15).pack(side="left")
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left", padx=4)

        # Bên phải toolbar
        tk.Button(toolbar, text="ℹ️ About",   command=self._about).pack(side="right", padx=4)
        tk.Button(toolbar, text="📤 Export",  command=self._export).pack(side="right", padx=4)
        tk.Button(toolbar, text="📥 Import",  command=self._import).pack(side="right", padx=4)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        cols = DIEM_COLS + ["sua", "xoa"]
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        self.tree.tag_configure("fail", background="#ffe0e0")
        self.tree.tag_configure("pass", background="#e0ffe0")
        self.tree.tag_configure("no_score", background="#f5f5f5")

        for c in DIEM_COLS:
            self.tree.heading(c, text=DIEM_HEADS[c])
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
        data = records if records is not None else self.dm.list_all()
        for r in data:
            dtb = r.get("diem_trung_binh", "")
            try:
                val = float(dtb)
                tag = "fail" if val < PASS_MARK else "pass"
            except (ValueError, TypeError):
                tag = "no_score"  # Chưa có điểm
            # Dùng iid = id để tra cứu chính xác khi sửa/xóa
            self.tree.insert("", "end", iid=str(r.get("id", "")), tags=(tag,), values=(
                r.get("id",""), r.get("masv",""), r.get("hoten",""),
                r.get("diem_giua_ky",""), r.get("diem_cuoi_ky",""),
                r.get("diem_trung_binh",""), r.get("ghi_chu",""),
                "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} bản ghi | "
                                 "🟢 Xanh: đạt  🔴 Đỏ: không đạt  ⬜ Chưa có điểm")

    def _on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row: return
        col_idx = int(col.replace("#", "")) - 1
        all_cols = DIEM_COLS + ["sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""

        # row = iid = id thực của bản ghi (không phải STT hiển thị)
        id_val = row

        if col_name == "sua":
            self._sua_diem(id_val)
        elif col_name == "xoa":
            if messagebox.askyesno("Xác nhận", f"Xóa bản ghi ID {id_val}?"):
                self.dm.delete(id_val)
                self.tree.delete(row)

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data(); return
        result = self.dm.search("hoten", kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả")

    def _them(self):
        self._open_form()

    def _sua_diem(self, id_val):
        rec = self.dm.get_by_id(id_val)
        if rec:
            self._open_form(rec)

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa điểm" if is_edit else "Thêm điểm")
        win.geometry("420x300")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Sửa điểm sinh viên" if is_edit else "Thêm điểm sinh viên",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [("Mã SV *",       "masv"),
                  ("Họ tên *",      "hoten"),
                  ("Điểm giữa kỳ *","diem_giua_ky"),
                  ("Điểm cuối kỳ *","diem_cuoi_ky"),
                  ("Ghi chú",       "ghi_chu")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(win, text=label, anchor="w").grid(
                row=i+1, column=0, sticky="w", padx=14, pady=4)
            e = tk.Entry(win, width=26)
            e.grid(row=i+1, column=1, padx=10, pady=4, sticky="w")
            if data:
                e.insert(0, data.get(key, ""))
            entries[key] = e

        # Khi sửa: khoá Mã SV và Họ tên để tránh nhập sai
        if is_edit:
            entries["masv"].config(state="readonly")
            entries["hoten"].config(state="readonly")

        def _luu():
            masv  = entries["masv"].get().strip()
            hoten = entries["hoten"].get().strip()
            dgk_s = entries["diem_giua_ky"].get().strip()
            dck_s = entries["diem_cuoi_ky"].get().strip()

            if not masv or not hoten:
                messagebox.showwarning("Lỗi", "Mã SV và Họ tên không được để trống!", parent=win)
                return
            try:
                dgk = float(dgk_s)
                dck = float(dck_s)
                if not (0 <= dgk <= 10 and 0 <= dck <= 10):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Lỗi", "Điểm phải là số từ 0 đến 10!", parent=win)
                return

            dtb = round(dgk * 0.4 + dck * 0.6, 2)
            xep_loai = ("Xuất sắc" if dtb >= 9 else "Giỏi" if dtb >= 7
                        else "Khá" if dtb >= 5.5 else "Trung bình" if dtb >= 4 else "Yếu")
            ghi_chu = entries["ghi_chu"].get().strip() or xep_loai

            record = {"masv": masv, "hoten": hoten,
                      "diem_giua_ky": dgk, "diem_cuoi_ky": dck,
                      "diem_trung_binh": dtb, "ghi_chu": ghi_chu}

            if is_edit:
                self.dm.update(data["id"], record)
            else:
                record["id"] = self.dm.get_next_id()
                self.dm.create(record)

            win.destroy()
            self.load_data()

        note = tk.Label(win, text="ĐTB = ĐGK×40% + ĐCK×60%  |  * là trường bắt buộc",
                        fg="gray", font=("Arial", 9))
        note.grid(row=len(fields)+1, column=0, columnspan=2, pady=4)

        btn = tk.Frame(win)
        btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=8)
        tk.Button(btn, text="💾 Lưu", command=_luu,        width=10).pack(side="left", padx=6)
        tk.Button(btn, text="❌ Hủy", command=win.destroy, width=10).pack(side="left", padx=6)

    def _import(self):
        from tkinter import filedialog
        import shutil, pandas as pd
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            df = pd.read_csv(path, dtype=str)
            required = {"masv", "hoten", "diem_giua_ky", "diem_cuoi_ky"}
            if not required.issubset(set(df.columns)):
                messagebox.showerror("Lỗi Import",
                    f"File thiếu cột bắt buộc: {required - set(df.columns)}")
                return
            shutil.copy(path, "data/diem.csv")
            self.load_data()
            messagebox.showinfo("Import", f"Import thành công {len(df)} bản ghi!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if path:
            shutil.copy("data/diem.csv", path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")

    def _about(self):
        messagebox.showinfo("About – Bảng điểm",
            "Module: Quản lý Bảng điểm\n"
            "Phiên bản: 1.0\n"
            "Công thức: ĐTB = ĐGK×40% + ĐCK×60%\n"
            "Xếp loại: Xuất sắc ≥9 | Giỏi ≥7 | Khá ≥5.5 | TB ≥4 | Yếu <4\n"
            "─────────────────────────\n"
            "Phần mềm Quản lý Sinh viên ĐHHL\n"
            "Nhóm: ...  |  Năm: 2025")
