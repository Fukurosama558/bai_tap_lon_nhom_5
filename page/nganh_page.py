import os
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from controller.nganh_controller import NganhController
from model.sinhvien_model import SinhvienModel

# ── Cấu hình hệ thống ─────────────────────────────────────────────────────────
NGANH_COLS = ["id", "ma_nganh", "ten_nganh", "mo_ta"]
DISPLAY_COLS = ["STT", "ma_nganh", "ten_nganh", "mo_ta"]
NGANH_HEADS = {"STT": "STT", "ma_nganh": "Mã ngành", "ten_nganh": "Tên ngành", "mo_ta": "Mô tả"}
COL_W = {"STT": 50, "ma_nganh": 110, "ten_nganh": 260, "mo_ta": 320}
NGANH_FILE = "data/nganh.csv"

class NganhPage(tk.Frame):

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.nm = SinhvienModel(NGANH_FILE, NGANH_COLS)
        self.controller = NganhController(self.nm)
        
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    # ── Giao diện ────────────────────────────────────────────────────────────

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Quản lý Ngành học", font=("Arial", 14, "bold")).pack(side="left", padx=10)

        for txt, cmd in [("➕ Thêm ngành", lambda: self._open_form()), ("🔄 Làm mới", self.load_data)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side="left", padx=4)

        # Tìm kiếm
        tk.Label(toolbar, text="Tìm:").pack(side="left", padx=(20, 2))
        self.search_field = ttk.Combobox(toolbar, values=["Mã ngành", "Tên ngành", "Mô tả"], state="readonly", width=10)
        self.search_field.current(1)
        self.search_field.pack(side="left")
        
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, width=18).pack(side="left", padx=4)
        tk.Button(toolbar, text="🔍", command=self._search).pack(side="left")

        tk.Button(toolbar, text="📤 Export", command=self._export).pack(side="right", padx=4)
        tk.Button(toolbar, text="📥 Import", command=self._import).pack(side="right", padx=4)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=6)

        self.tree = ttk.Treeview(tree_frame, columns=DISPLAY_COLS + ["sv_count", "sua", "xoa"], show="headings", height=18)
        for c in DISPLAY_COLS:
            self.tree.heading(c, text=NGANH_HEADS[c])
            self.tree.column(c, width=COL_W[c], anchor="center")
            
        self.tree.heading("sv_count", text="Số SV"); self.tree.column("sv_count", width=70, anchor="center")
        self.tree.heading("sua", text="Sửa"); self.tree.column("sua", width=60, anchor="center")
        self.tree.heading("xoa", text="Xóa"); self.tree.column("xoa", width=60, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<ButtonRelease-1>", self._on_click)
        self.status = tk.Label(self, text="", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

    # ── Đếm SV theo ngành ────────────────────────────────────────────────────

    def _count_sv_by_nganh(self):
        try:
            return pd.read_csv("data/sinhvien.csv", dtype=str)["ma_nganh"].value_counts().to_dict()
        except Exception:
            return {}

    # ── Dữ liệu ──────────────────────────────────────────────────────────────

    def load_data(self, records=None):
        for row in self.tree.get_children():    
            self.tree.delete(row)
            
        data = records if records is not None else self.nm.list_all()
        sv_cnt = self._count_sv_by_nganh()
        for i, r in enumerate(data, start=1):
            ma = str(r.get("ma_nganh", ""))
            self.tree.insert("", "end", iid=str(r.get("id", "")), values=(
                i, ma, r.get("ten_nganh", ""), r.get("mo_ta", ""),
                sv_cnt.get(ma, 0), "✏️ Sửa", "🗑️ Xóa"
            ))
        self.status.config(text=f"Tổng: {len(data)} ngành học")

    def _on_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row: return

        col_idx = int(col.replace("#", "")) - 1
        all_cols = NGANH_COLS + ["sv_count", "sua", "xoa"]
        col_name = all_cols[col_idx] if col_idx < len(all_cols) else ""
        
        if col_name == "sua":
            rec = self.nm.get_by_id(row)
            if rec: self._open_form(rec)
        elif col_name == "xoa":
            cnt = self._count_sv_by_nganh()
            vals = self.tree.item(row)["values"]
            ma = str(vals[1]) if len(vals) > 1 else ""
            if cnt.get(ma, 0) > 0:
                messagebox.showwarning("Không thể xóa", f"Ngành '{ma}' còn {cnt[ma]} sinh viên.\nVui lòng chuyển hoặc xóa sinh viên trước!"); return
            if messagebox.askyesno("Xác nhận", "Xóa ngành học này?"):
                self.controller.delete_nganh(row)
                self.tree.delete(row)

    # ── Tìm kiếm ─────────────────────────────────────────────────────────────

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.load_data(); return
            
        col_map = {"Mã ngành": "ma_nganh", "Tên ngành": "ten_nganh", "Mô tả": "mo_ta"}
        col = col_map.get(self.search_field.get(), "ten_nganh")
        
        result = self.controller.search_nganh(col, kw)
        self.load_data(result)
        self.status.config(text=f"Tìm thấy {len(result)} kết quả cho '{kw}'")

    # ── Form Thêm / Sửa ───────────────────────────────────────────────────────

    def _open_form(self, data=None):
        is_edit = data is not None
        win = tk.Toplevel(self)
        win.title("Sửa ngành học" if is_edit else "Thêm ngành học")
        win.geometry("420x240")
        win.resizable(False, False)
        win.grab_set()

        title_txt = "Sửa ngành học" if is_edit else "Thêm ngành học mới"
        tk.Label(win, text=title_txt, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [("Mã ngành *", "ma_nganh"), ("Tên ngành *", "ten_nganh"), ("Mô tả", "mo_ta")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(win, text=label, anchor="w").grid(row=i+1, column=0, sticky="w", padx=14, pady=5)
            e = tk.Entry(win, width=30)
            e.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
            if data: e.insert(0, data.get(key, ""))
            entries[key] = e

        if is_edit:
            entries["ma_nganh"].config(state="readonly")

        def _luu():
            record = {
                "ma_nganh": entries["ma_nganh"].get().strip().upper(),
                "ten_nganh": entries["ten_nganh"].get().strip(),
                "mo_ta": entries["mo_ta"].get().strip()
            }
            ok, msg = self.controller.save_nganh(record, is_edit, data["id"] if is_edit else None)
            if not ok:
                messagebox.showwarning("Lỗi", msg, parent=win)
                return
            win.destroy()
            self.load_data()
            messagebox.showinfo("Thành công", msg)

        btn = tk.Frame(win)
        btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=12)
        tk.Button(btn, text="💾 Lưu", command=_luu, width=12).pack(side="left", padx=6)
        tk.Button(btn, text="❌ Hủy", command=win.destroy, width=12).pack(side="left", padx=6)

    # ── Import / Export ───────────────────────────────────────────────────────

    def _import(self):
        from tkinter import filedialog
        import shutil

        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return

        def task():
            try:
                # Đọc kiểm tra dữ liệu
                df = pd.read_csv(path, dtype=str)
                required = {"ma_nganh", "ten_nganh"}

                if not required.issubset(set(df.columns)):
                    missing = required - set(df.columns)
                    self.after(0, lambda: messagebox.showerror("Lỗi Import", f"File thiếu cột bắt buộc: {missing}"))
                    return

                # Copy ghi đè vào file dữ liệu ngành
                shutil.copy(path, NGANH_FILE)

                # Cập nhật lại giao diện và thông báo
                self.after(0, self.load_data)
                self.after(0, lambda: messagebox.showinfo("Import", f"Import thành công {len(df)} ngành!"))

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Lỗi", str(e)))

        self.app.run_async(task, "Đang import dữ liệu ngành...")
        
    def _export(self):
        from tkinter import filedialog
        import shutil
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            shutil.copy(NGANH_FILE, path)
            messagebox.showinfo("Export", f"Đã xuất ra:\n{path}")