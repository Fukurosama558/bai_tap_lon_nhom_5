import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
from datetime import datetime


class ThongKePage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Thống kê - Báo cáo",
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)
        tk.Button(toolbar, text="🔄 Cập nhật", command=self.load_data).pack(side="left", padx=4)

        # Nội dung chính chia 2 cột
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=8)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # ── Khung 1: Thống kê sinh viên ──────────────────────────────────────
        sv_frame = tk.LabelFrame(main, text="Sinh viên", padx=10, pady=8)
        sv_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.sv_labels = {}
        sv_items = [
            ("tong_sv",   "Tổng số sinh viên:"),
            ("tuoi_tb",   "Tuổi trung bình:"),
            ("tuoi_min",  "Tuổi nhỏ nhất:"),
            ("tuoi_max",  "Tuổi lớn nhất:"),
        ]
        for i, (key, text) in enumerate(sv_items):
            tk.Label(sv_frame, text=text, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(sv_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=10, pady=3)
            self.sv_labels[key] = lbl

        # Thống kê theo lớp
        tk.Label(sv_frame, text="Sĩ số theo lớp:", anchor="w").grid(
            row=len(sv_items), column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.lop_tree = ttk.Treeview(sv_frame, columns=("lop", "so_luong"),
                                     show="headings", height=5)
        self.lop_tree.heading("lop", text="Lớp")
        self.lop_tree.heading("so_luong", text="Số lượng")
        self.lop_tree.column("lop", width=100, anchor="center")
        self.lop_tree.column("so_luong", width=80, anchor="center")
        self.lop_tree.grid(row=len(sv_items)+1, column=0, columnspan=2, sticky="ew", pady=4)

        # ── Khung 2: Thống kê điểm ───────────────────────────────────────────
        diem_frame = tk.LabelFrame(main, text="Điểm số", padx=10, pady=8)
        diem_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        self.diem_labels = {}
        diem_items = [
            ("tong_bd",    "Tổng bản ghi điểm:"),
            ("diem_tb",    "ĐTB toàn khóa:"),
            ("diem_max",   "Điểm cao nhất:"),
            ("diem_min",   "Điểm thấp nhất:"),
        ]
        for i, (key, text) in enumerate(diem_items):
            tk.Label(diem_frame, text=text, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(diem_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=10, pady=3)
            self.diem_labels[key] = lbl

        # Phân loại
        tk.Label(diem_frame, text="Phân loại học lực:", anchor="w").grid(
            row=len(diem_items), column=0, columnspan=2, sticky="w", pady=(10, 2))

        phan_loai_items = [
            ("xuat_sac",   "Xuất sắc (≥9.0):"),
            ("gioi",       "Giỏi (7.0-8.9):"),
            ("kha",        "Khá (5.5-6.9):"),
            ("trung_binh", "Trung bình (4.0-5.4):"),
            ("yeu",        "Yếu (<4.0):"),
        ]
        self.pl_labels = {}
        for i, (key, text) in enumerate(phan_loai_items):
            tk.Label(diem_frame, text=text, anchor="w").grid(
                row=len(diem_items)+1+i, column=0, sticky="w", pady=2)
            lbl = tk.Label(diem_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=len(diem_items)+1+i, column=1, sticky="w", padx=10, pady=2)
            self.pl_labels[key] = lbl

        # ── Ghi chú ───────────────────────────────────────────────────────────
        note_frame = tk.LabelFrame(main, text="Ghi chú", padx=10, pady=6)
        note_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        self.note_text = tk.Text(note_frame, height=4, state="disabled",
                                 font=("Arial", 10), wrap="word")
        self.note_text.pack(fill="x")

    def load_data(self):
        # ── Sinh viên ──────────────────────────────────────────────────────────
        try:
            df_sv = pd.read_csv("data/sinhvien.csv", dtype=str)
            total_sv = len(df_sv)
            self.sv_labels["tong_sv"].config(text=str(total_sv))

            if "ngay_sinh" in df_sv.columns:
                today = datetime.today()

                def _tinh_tuoi(ns):
                    try:
                        bd = datetime.strptime(str(ns).strip(), "%d/%m/%Y")
                        age = today.year - bd.year - (
                            (today.month, today.day) < (bd.month, bd.day)
                        )
                        return age if 1 <= age <= 120 else np.nan
                    except Exception:
                        return np.nan

                tuoi = pd.to_numeric(
                    df_sv["ngay_sinh"].map(_tinh_tuoi), errors="coerce"
                ).dropna()

                if not tuoi.empty:
                    self.sv_labels["tuoi_tb"].config(text=f"{np.mean(tuoi):.1f}")
                    self.sv_labels["tuoi_min"].config(text=str(int(np.min(tuoi))))
                    self.sv_labels["tuoi_max"].config(text=str(int(np.max(tuoi))))
                else:
                    for k in ("tuoi_tb", "tuoi_min", "tuoi_max"):
                        self.sv_labels[k].config(text="Không có dữ liệu")

            # Theo lớp
            for row in self.lop_tree.get_children():
                self.lop_tree.delete(row)
            if "lop" in df_sv.columns:
                for lop, count in df_sv["lop"].value_counts().items():
                    self.lop_tree.insert("", "end", values=(lop, count))
        except Exception as e:
            self.sv_labels["tong_sv"].config(text=f"Lỗi: {e}")

        # ── Điểm ─────────────────────────────────────────────────────────────
        try:
            df_d = pd.read_csv("data/diem.csv", dtype=str)
            total_d = len(df_d)
            self.diem_labels["tong_bd"].config(text=str(total_d))

            if "diem_trung_binh" in df_d.columns:
                dtb = pd.to_numeric(df_d["diem_trung_binh"], errors="coerce").dropna()
                if not dtb.empty:
                    self.diem_labels["diem_tb"].config(text=f"{np.mean(dtb):.2f}")
                    self.diem_labels["diem_max"].config(text=f"{np.max(dtb):.1f}")
                    self.diem_labels["diem_min"].config(text=f"{np.min(dtb):.1f}")
                    self.pl_labels["xuat_sac"].config(text=str(int((dtb >= 9.0).sum())))
                    self.pl_labels["gioi"].config(text=str(int(((dtb >= 7.0) & (dtb < 9.0)).sum())))
                    self.pl_labels["kha"].config(text=str(int(((dtb >= 5.5) & (dtb < 7.0)).sum())))
                    self.pl_labels["trung_binh"].config(text=str(int(((dtb >= 4.0) & (dtb < 5.5)).sum())))
                    self.pl_labels["yeu"].config(text=str(int((dtb < 4.0).sum())))

                    # Ghi chú tự động
                    note = (f"Tổng {total_d} sinh viên có điểm. "
                            f"ĐTB toàn khóa: {np.mean(dtb):.2f}. "
                            f"Sinh viên đạt (≥4.0): {int((dtb >= 4.0).sum())}, "
                            f"Không đạt: {int((dtb < 4.0).sum())}.")
                    self.note_text.config(state="normal")
                    self.note_text.delete("1.0", "end")
                    self.note_text.insert("end", note)
                    self.note_text.config(state="disabled")
        except Exception as e:
            self.diem_labels["tong_bd"].config(text=f"Lỗi: {e}")