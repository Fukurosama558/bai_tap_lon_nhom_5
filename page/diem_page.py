import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from controller.diem_controller import DiemController
from model.sinhvien_model import SinhvienModel

# ── Cấu hình hệ thống ─────────────────────────────────────────────────────────
DIEM_COLS = ["id", "masv", "hoten", "cc", "dk1", "dk2", "dt", "diem_trung_binh", "ghi_chu"]
DISPLAY_COLS = ["STT", "masv", "hoten", "cc", "dk1", "dk2", "dt", "diem_trung_binh", "ghi_chu"]
DIEM_HEADS = {
    "STT": "STT", "masv": "Mã SV", "hoten": "Họ tên", "cc": "CC", "dk1": "ĐK1", 
    "dk2": "ĐK2", "dt": "ĐT", "diem_trung_binh": "ĐTB", "ghi_chu": "Xếp loại"
}
COL_W = {"STT": 45, "masv": 90, "hoten": 170, "cc": 55, "dk1": 65, "dk2": 65, "dt": 65, "diem_trung_binh": 70, "ghi_chu": 105}
PASS_MARK = 5.0
SV_FILE = "data/sinhvien.csv"


class DiemPage(tk.Frame):

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.dm = SinhvienModel("data/diem.csv", DIEM_COLS)
        self.controller = DiemController(self.dm)
        
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    # ── Giao diện ────────────────────────────────────────────────────────────

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Bảng điểm sinh viên", font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm điểm", self._them), ("🔄 Làm mới", self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        # Tìm kiếm
        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_field = ttk.Combobox(toolbar, values=["Mã SV", "Họ tên", "Xếp loại"], state="readonly", width=10)
        self.search_field.current(1)
        self.search_field.pack(side="left")
        
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=15).pack(side="left", padx=4)
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left")

        tk.Button(toolbar, text="📤 Export", command=self._export).pack(side="right", padx=4)
        tk.Button(toolbar, text="📥 Import", command=self._import).pack(side="right", padx=4)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        self.tree = ttk.Treeview(tree_frame, columns=DISPLAY_COLS + ["sua", "xoa"], show="headings", height=15)
        self.tree.tag_configure("fail", background="#ffe0e0")
        self.tree.tag_configure("pass", background="#e0ffe0")
        self.tree.tag_configure("no_score", background="#f5f5f5")

        for c in DISPLAY_COLS:
            self.tree.heading(c, text=DIEM_HEADS[c])
            self.tree.column(c, width=COL_W[c], anchor="center")
            
        self.tree.heading("sua", text="Sửa"); self.tree.column("sua", width=60, anchor="center")
        self.tree.heading("xoa", text="Xóa"); self.tree.column("xoa", width=60, anchor="center")

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
            
        data = records if records is not None else self.dm.list_all()
        for i, r in enumerate(data, start=1):
            dtb = r.get("diem_trung_binh", "")
            try:
                tag = "fail" if float(dtb) < PASS_MARK else "pass"
            except (ValueError, TypeError):
                tag = "no_score"
                
            self.tree.insert("", "end", iid=str(r.get("id", "")), tags=(tag,), values=(
                i, r.get("masv", ""), r.get("hoten", ""), r.get("cc", ""), 
                r.get("dk1", ""), r.get("dk2", ""), r.get("dt", ""), dtb, r.get("ghi_chu", ""), 
                "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} bản ghi  |  🟢 Đạt  🔴 Không đạt  ⬜ Chưa có điểm")

    def _on_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row: return

        col_idx = int(col.replace("#", "")) - 1
        all_cols = DIEM_COLS + ["sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""
        
        if col_name == "sua":
            self._sua_diem(row)
        elif col_name == "xoa" and messagebox.askyesno("Xác nhận", f"Xóa bản ghi ID {row}?"):
            self.controller.delete_diem(row)
            self.tree.delete(row)

    # ── Tìm kiếm ─────────────────────────────────────────────────────────────

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data(); return
            
        col_map = {"Mã SV": "masv", "Họ tên": "hoten", "Xếp loại": "ghi_chu"}
        col = col_map.get(self.search_field.get(), "hoten")
        
        result = self.controller.search_diem(col, kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả cho '{kw}'")

    # ── Form thêm / sửa ───────────────────────────────────────────────────────

    def _them(self): self._open_form()
    
    def _sua_diem(self, id_val):
        rec = self.dm.get_by_id(id_val)
        if rec: self._open_form(rec)

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa điểm" if is_edit else "Thêm điểm")
        win.geometry("440x340")
        win.resizable(False, False)
        win.grab_set()

        title_txt = "Sửa điểm sinh viên" if is_edit else "Thêm điểm sinh viên"
        tk.Label(win, text=title_txt, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        sv_list = self._get_sv_list()
        masv_list = [f"{s['masv']} – {s['hoten']}" for s in sv_list]

        tk.Label(win, text="Sinh viên *", anchor="w").grid(row=1, column=0, sticky="w", padx=14, pady=4)
        sv_combo = ttk.Combobox(win, values=masv_list, width=30, state="readonly")
        sv_combo.grid(row=1, column=1, padx=10, pady=4, sticky="w")

        if is_edit:
            label_str = f"{data.get('masv', '')} – {data.get('hoten', '')}"
            sv_combo.set(label_str if label_str in masv_list else data.get("masv", ""))
            sv_combo.config(state="disabled")

        score_fields = [("CC (0–10) *", "cc"), ("ĐK1 (0–10) *", "dk1"), ("ĐK2 (0–10) *", "dk2"), ("ĐT – Điểm thi (0–10) *", "dt")]
        entries = {}
        for i, (label, key) in enumerate(score_fields):
            tk.Label(win, text=label, anchor="w").grid(row=i+2, column=0, sticky="w", padx=14, pady=4)
            e = tk.Entry(win, width=12)
            e.grid(row=i+2, column=1, padx=10, pady=4, sticky="w")
            if is_edit: e.insert(0, data.get(key, ""))
            entries[key] = e

        dtb_var = tk.StringVar(value="—")
        tk.Label(win, text="ĐTB:", anchor="w").grid(row=6, column=0, sticky="w", padx=14, pady=4)
        tk.Label(win, textvariable=dtb_var, font=("Arial", 10, "bold"), fg="#2980b9").grid(row=6, column=1, sticky="w", padx=10)

        def _preview(*_):
            try:
                dtb = self.controller.calc_dtb(float(entries["cc"].get()), float(entries["dk1"].get()), float(entries["dk2"].get()), float(entries["dt"].get()))
                dtb_var.set(f"{dtb} ({self.controller.xep_loai(dtb)})")
            except Exception:
                dtb_var.set("—")

        # Ràng buộc sự kiện thay đổi text để tự động cập nhật ĐTB Preview
        for e in entries.values():
            e.bind("<KeyRelease>", _preview)
        if is_edit: _preview()

        def _luu():
            sel = sv_combo.get().strip()
            if not sel:
                messagebox.showwarning("Lỗi", "Vui lòng chọn sinh viên!", parent=win); return

            masv, hoten = sel.split(" – ", 1) if " – " in sel else (sel, sel)
            record = {
                "masv": masv.strip(), "hoten": hoten.strip(),
                "cc": entries["cc"].get().strip(), "dk1": entries["dk1"].get().strip(),
                "dk2": entries["dk2"].get().strip(), "dt": entries["dt"].get().strip()
            }

            ok, msg = self.controller.save_diem(record, is_edit, data["id"] if is_edit else None)
            if not ok:
                messagebox.showwarning("Lỗi", msg, parent=win); return

            win.destroy()
            self.load_data()
            messagebox.showinfo("Thành công", msg)

        btn = tk.Frame(win)
        btn.grid(row=8, column=0, columnspan=2, pady=8)
        tk.Button(btn, text="💾 Lưu", command=_luu, width=10).pack(side="left", padx=6)
        tk.Button(btn, text="❌ Hủy", command=win.destroy, width=10).pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_sv_list(self):
        """Lấy danh sách {masv, hoten} từ sinhvien.csv."""
        try:
            return pd.read_csv(SV_FILE, dtype=str)[["masv", "hoten"]].dropna(subset=["masv"]).to_dict(orient="records")
        except Exception:
            return []

    # ── Import / Export ───────────────────────────────────────────────────────

    def _import(self):
        from tkinter import filedialog
        import shutil

        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return

        def task():
            try:
                # Đọc và kiểm tra cấu trúc dữ liệu file điểm
                df = pd.read_csv(path, dtype=str)
                required = {"masv", "hoten"}

                if not required.issubset(set(df.columns)):
                    missing = required - set(df.columns)
                    self.after(0, lambda: messagebox.showerror("Lỗi Import", f"File thiếu cột bắt buộc: {missing}"))
                    return

                # Copy đè thẳng file vào bộ nhớ dữ liệu điểm
                shutil.copy(path, "data/diem.csv")

                # Cập nhật giao diện thông qua luồng chính
                self.after(0, self.load_data)
                self.after(0, lambda: messagebox.showinfo("Import", f"Import thành công {len(df)} bản ghi!"))

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Lỗi", str(e)))

        self.app.run_async(task, "Đang import dữ liệu điểm...")

    def _export(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            shutil.copy("data/diem.csv", path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")