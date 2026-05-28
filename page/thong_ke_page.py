import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
from datetime import datetime

# matplotlib nhúng vào Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Cố định font hỗ trợ tiếng Việt (fallback an toàn)
plt.rcParams["font.family"] = "DejaVu Sans"


class ThongKePage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._view()
        self.load_data()
        self.pack(fill="both", expand=True)

    # ─────────────────────────────────────────────────────────────────────────
    def _view(self):
        toolbar = tk.Frame(self, bd=1, relief="raised", pady=4)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Thống kê - Báo cáo",
                 font=("Arial", 14, "bold")).pack(side="left", padx=10)
        tk.Button(toolbar, text="🔄 Cập nhật", command=self.load_data).pack(side="left", padx=4)

        # Notebook: 3 tab
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        self._tab_tong_quan(nb)
        self._tab_bieu_do(nb)
        self._tab_bxh(nb)

    # ── Tab 1: Tổng quan ─────────────────────────────────────────────────────
    def _tab_tong_quan(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="📋 Tổng quan")

        main = tk.Frame(frame)
        main.pack(fill="both", expand=True, padx=10, pady=8)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Khung sinh viên
        sv_frame = tk.LabelFrame(main, text="Sinh viên", padx=10, pady=8)
        sv_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.sv_labels = {}
        sv_items = [
            ("tong_sv",  "Tổng số sinh viên:"),
            ("tuoi_tb",  "Tuổi trung bình:"),
            ("tuoi_min", "Tuổi nhỏ nhất:"),
            ("tuoi_max", "Tuổi lớn nhất:"),
        ]
        for i, (key, text) in enumerate(sv_items):
            tk.Label(sv_frame, text=text, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(sv_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=10, pady=3)
            self.sv_labels[key] = lbl

        tk.Label(sv_frame, text="Sĩ số theo lớp:", anchor="w").grid(
            row=len(sv_items), column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.lop_tree = ttk.Treeview(sv_frame, columns=("lop", "so_luong"),
                                     show="headings", height=5)
        self.lop_tree.heading("lop", text="Lớp")
        self.lop_tree.heading("so_luong", text="Số lượng")
        self.lop_tree.column("lop", width=100, anchor="center")
        self.lop_tree.column("so_luong", width=80, anchor="center")
        self.lop_tree.grid(row=len(sv_items)+1, column=0, columnspan=2, sticky="ew", pady=4)

        # Khung điểm
        diem_frame = tk.LabelFrame(main, text="Điểm số", padx=10, pady=8)
        diem_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.diem_labels = {}
        diem_items = [
            ("tong_bd",  "Tổng bản ghi điểm:"),
            ("diem_tb",  "ĐTB toàn khóa:"),
            ("diem_max", "Điểm cao nhất:"),
            ("diem_min", "Điểm thấp nhất:"),
        ]
        for i, (key, text) in enumerate(diem_items):
            tk.Label(diem_frame, text=text, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(diem_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="w", padx=10, pady=3)
            self.diem_labels[key] = lbl

        tk.Label(diem_frame, text="Phân loại học lực:", anchor="w").grid(
            row=len(diem_items), column=0, columnspan=2, sticky="w", pady=(10, 2))
        phan_loai_items = [
            ("xuat_sac",   "Xuất sắc (≥9.0):"),
            ("gioi",       "Giỏi (7.0–8.9):"),
            ("kha",        "Khá (5.5–6.9):"),
            ("trung_binh", "Trung bình (4.0–5.4):"),
            ("yeu",        "Yếu (<4.0):"),
        ]
        self.pl_labels = {}
        for i, (key, text) in enumerate(phan_loai_items):
            tk.Label(diem_frame, text=text, anchor="w").grid(
                row=len(diem_items)+1+i, column=0, sticky="w", pady=2)
            lbl = tk.Label(diem_frame, text="—", anchor="w", font=("Arial", 10, "bold"))
            lbl.grid(row=len(diem_items)+1+i, column=1, sticky="w", padx=10, pady=2)
            self.pl_labels[key] = lbl

        # Ghi chú
        note_frame = tk.LabelFrame(main, text="Ghi chú", padx=10, pady=6)
        note_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        self.note_text = tk.Text(note_frame, height=3, state="disabled",
                                 font=("Arial", 10), wrap="word")
        self.note_text.pack(fill="x")

    # ── Tab 2: Biểu đồ ───────────────────────────────────────────────────────
    def _tab_bieu_do(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="📊 Biểu đồ")

        ctrl = tk.Frame(frame)
        ctrl.pack(fill="x", padx=10, pady=4)
        tk.Label(ctrl, text="Loại biểu đồ:").pack(side="left")
        self.chart_type = ttk.Combobox(ctrl, state="readonly", width=25, values=[
            "Phân loại học lực (Pie)",
            "Điểm TB theo lớp (Bar)",
            "Phân bố ĐTB (Histogram)",
        ])
        self.chart_type.current(0)
        self.chart_type.pack(side="left", padx=6)
        tk.Button(ctrl, text="📈 Vẽ", command=self._ve_bieu_do).pack(side="left", padx=4)

        self.fig = Figure(figsize=(7, 4), dpi=100)
        self.ax  = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=6)

    # ── Tab 3: BXH ───────────────────────────────────────────────────────────
    def _tab_bxh(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="🏆 Bảng xếp hạng")

        ctrl = tk.Frame(frame)
        ctrl.pack(fill="x", padx=10, pady=4)
        tk.Label(ctrl, text="Xếp theo:").pack(side="left")
        self.bxh_type = ttk.Combobox(ctrl, state="readonly", width=20, values=[
            "Toàn trường",
            "Theo lớp",
            "Theo ngành",
        ])
        self.bxh_type.current(0)
        self.bxh_type.pack(side="left", padx=6)

        tk.Label(ctrl, text="Top:").pack(side="left", padx=(10, 2))
        self.top_n = ttk.Combobox(ctrl, state="readonly", width=6,
                                  values=["5", "10", "20", "Tất cả"])
        self.top_n.current(1)
        self.top_n.pack(side="left")
        tk.Button(ctrl, text="🏅 Xếp hạng", command=self._ve_bxh).pack(side="left", padx=6)

        cols = ("hang", "masv", "hoten", "lop", "nganh", "dtb", "xep_loai")
        heads = {"hang": "Hạng", "masv": "Mã SV", "hoten": "Họ tên",
                 "lop": "Lớp", "nganh": "Ngành", "dtb": "ĐTB", "xep_loai": "Xếp loại"}
        widths = {"hang": 50, "masv": 90, "hoten": 180,
                  "lop": 80, "nganh": 120, "dtb": 70, "xep_loai": 100}

        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=4)
        self.bxh_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        self.bxh_tree.tag_configure("gold",   background="#fff3cd")
        self.bxh_tree.tag_configure("silver", background="#e9ecef")
        self.bxh_tree.tag_configure("bronze", background="#f8d7b0")
        for c in cols:
            self.bxh_tree.heading(c, text=heads[c])
            self.bxh_tree.column(c, width=widths[c], anchor="center")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.bxh_tree.yview)
        self.bxh_tree.configure(yscrollcommand=sb.set)
        self.bxh_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.bxh_status = tk.Label(frame, text="", relief="sunken", anchor="w")
        self.bxh_status.pack(fill="x", side="bottom")

    # ─────────────────────────────────────────────────────────────────────────
    def load_data(self):
        self._load_sv()
        self._load_diem()
        self._ve_bieu_do()
        self._ve_bxh()

    def _load_sv(self):
        try:
            df_sv = pd.read_csv("data/sinhvien.csv", dtype=str)
            self.sv_labels["tong_sv"].config(text=str(len(df_sv)))

            if "ngay_sinh" in df_sv.columns:
                today = datetime.today()
                def _tuoi(ns):
                    try:
                        bd = datetime.strptime(str(ns).strip(), "%d/%m/%Y")
                        age = today.year - bd.year - (
                            (today.month, today.day) < (bd.month, bd.day))
                        return age if 1 <= age <= 120 else np.nan
                    except Exception:
                        return np.nan
                tuoi = pd.to_numeric(df_sv["ngay_sinh"].map(_tuoi), errors="coerce").dropna()
                if not tuoi.empty:
                    self.sv_labels["tuoi_tb"].config(text=f"{np.mean(tuoi):.1f}")
                    self.sv_labels["tuoi_min"].config(text=str(int(np.min(tuoi))))
                    self.sv_labels["tuoi_max"].config(text=str(int(np.max(tuoi))))
                else:
                    for k in ("tuoi_tb","tuoi_min","tuoi_max"):
                        self.sv_labels[k].config(text="Không có dữ liệu")

            for row in self.lop_tree.get_children():
                self.lop_tree.delete(row)
            if "lop" in df_sv.columns:
                for lop, cnt in df_sv["lop"].value_counts().items():
                    self.lop_tree.insert("", "end", values=(lop, cnt))

            self._df_sv = df_sv  # lưu để dùng cho BXH
        except Exception as e:
            self.sv_labels["tong_sv"].config(text=f"Lỗi: {e}")
            self._df_sv = pd.DataFrame()

    def _load_diem(self):
        try:
            df_d = pd.read_csv("data/diem.csv", dtype=str)
            self.diem_labels["tong_bd"].config(text=str(len(df_d)))
            dtb_raw = pd.to_numeric(df_d.get("diem_trung_binh", pd.Series()), errors="coerce")
            dtb = dtb_raw[(dtb_raw >= 0) & (dtb_raw <= 10)].dropna()
            if not dtb.empty:
                self.diem_labels["diem_tb"].config(text=f"{np.mean(dtb):.2f}")
                self.diem_labels["diem_max"].config(text=f"{np.max(dtb):.1f}")
                self.diem_labels["diem_min"].config(text=f"{np.min(dtb):.1f}")
                self.pl_labels["xuat_sac"].config(  text=str(int((dtb >= 9.0).sum())))
                self.pl_labels["gioi"].config(       text=str(int(((dtb >= 7.0) & (dtb < 9.0)).sum())))
                self.pl_labels["kha"].config(        text=str(int(((dtb >= 5.5) & (dtb < 7.0)).sum())))
                self.pl_labels["trung_binh"].config( text=str(int(((dtb >= 4.0) & (dtb < 5.5)).sum())))
                self.pl_labels["yeu"].config(        text=str(int((dtb < 4.0).sum())))

                note = (f"Tổng {len(df_d)} bản ghi ({len(dtb)} có điểm hợp lệ). "
                        f"ĐTB: {np.mean(dtb):.2f}. "
                        f"Đạt (≥4.0): {int((dtb >= 4.0).sum())}  "
                        f"Không đạt: {int((dtb < 4.0).sum())}.")
                self.note_text.config(state="normal")
                self.note_text.delete("1.0", "end")
                self.note_text.insert("end", note)
                self.note_text.config(state="disabled")
            self._df_diem = df_d
            self._dtb_series = dtb
        except Exception as e:
            self.diem_labels["tong_bd"].config(text=f"Lỗi: {e}")
            self._df_diem = pd.DataFrame()
            self._dtb_series = pd.Series(dtype=float)

    # ── Vẽ biểu đồ ───────────────────────────────────────────────────────────
    def _ve_bieu_do(self):
        self.ax.clear()
        choice = self.chart_type.get() if hasattr(self, "chart_type") else ""
        dtb = getattr(self, "_dtb_series", pd.Series(dtype=float))
        df_d = getattr(self, "_df_diem", pd.DataFrame())
        df_sv = getattr(self, "_df_sv", pd.DataFrame())

        try:
            if "Pie" in choice or choice == "":
                # Pie – phân loại học lực
                cats = {
                    "Xuat sac": int((dtb >= 9.0).sum()),
                    "Gioi":     int(((dtb >= 7.0) & (dtb < 9.0)).sum()),
                    "Kha":      int(((dtb >= 5.5) & (dtb < 7.0)).sum()),
                    "Trung binh": int(((dtb >= 4.0) & (dtb < 5.5)).sum()),
                    "Yeu":      int((dtb < 4.0).sum()),
                }
                cats = {k: v for k, v in cats.items() if v > 0}
                if cats:
                    colors = ["#2ecc71","#3498db","#f1c40f","#e67e22","#e74c3c"]
                    self.ax.pie(list(cats.values()), labels=list(cats.keys()),
                                autopct="%1.1f%%", colors=colors[:len(cats)],
                                startangle=140)
                    self.ax.set_title("Phan loai hoc luc")
                else:
                    self.ax.text(0.5, 0.5, "Khong co du lieu diem",
                                 ha="center", va="center", transform=self.ax.transAxes)

            elif "Bar" in choice:
                # Bar – ĐTB theo lớp
                if not df_d.empty and not df_sv.empty and "lop" in df_sv.columns:
                    merged = df_d.merge(
                        df_sv[["masv","lop"]].drop_duplicates("masv"),
                        on="masv", how="left")
                    merged["dtb_num"] = pd.to_numeric(
                        merged["diem_trung_binh"], errors="coerce")
                    grp = merged.groupby("lop")["dtb_num"].mean().dropna().sort_values(ascending=False)
                    if not grp.empty:
                        bars = self.ax.bar(grp.index, grp.values,
                                           color="#3498db", edgecolor="white")
                        self.ax.bar_label(bars, fmt="%.2f", padding=3)
                        self.ax.set_title("DTB theo lop")
                        self.ax.set_xlabel("Lop")
                        self.ax.set_ylabel("DTB")
                        self.ax.set_ylim(0, 10.5)
                        self.fig.autofmt_xdate(rotation=30)
                    else:
                        self.ax.text(0.5, 0.5, "Khong du du lieu",
                                     ha="center", va="center", transform=self.ax.transAxes)
                else:
                    self.ax.text(0.5, 0.5, "Khong co du lieu",
                                 ha="center", va="center", transform=self.ax.transAxes)

            elif "Histogram" in choice:
                if not dtb.empty:
                    self.ax.hist(dtb, bins=10, range=(0, 10),
                                 color="#9b59b6", edgecolor="white")
                    self.ax.set_title("Phan bo DTB")
                    self.ax.set_xlabel("DTB")
                    self.ax.set_ylabel("So SV")
                    self.ax.axvline(dtb.mean(), color="red", linestyle="--",
                                    label=f"TB={dtb.mean():.2f}")
                    self.ax.legend()
                else:
                    self.ax.text(0.5, 0.5, "Khong co du lieu",
                                 ha="center", va="center", transform=self.ax.transAxes)

        except Exception as e:
            self.ax.text(0.5, 0.5, f"Loi: {e}", ha="center", va="center",
                         transform=self.ax.transAxes)

        self.fig.tight_layout()
        self.canvas.draw()

    # ── BXH ──────────────────────────────────────────────────────────────────
    def _ve_bxh(self):
        for row in self.bxh_tree.get_children():
            self.bxh_tree.delete(row)

        df_d  = getattr(self, "_df_diem", pd.DataFrame())
        df_sv = getattr(self, "_df_sv",   pd.DataFrame())
        if df_d.empty:
            self.bxh_status.config(text="Không có dữ liệu điểm")
            return

        try:
            # Tải ngành
            try:
                df_ng = pd.read_csv("data/nganh.csv", dtype=str)
            except Exception:
                df_ng = pd.DataFrame(columns=["ma_nganh","ten_nganh"])

            # Merge SV + điểm
            df_d2 = df_d.copy()
            df_d2["dtb_num"] = pd.to_numeric(df_d2.get("diem_trung_binh",""), errors="coerce")
            df_d2 = df_d2.dropna(subset=["dtb_num"])

            if not df_sv.empty and "masv" in df_sv.columns:
                sv_cols = ["masv","lop"] + (["nganh"] if "nganh" in df_sv.columns else [])
                merged = df_d2.merge(df_sv[sv_cols].drop_duplicates("masv"),
                                     on="masv", how="left")
            else:
                merged = df_d2.copy()
                merged["lop"] = ""

            if "lop" not in merged.columns:
                merged["lop"] = ""
            if "nganh" not in merged.columns:
                merged["nganh"] = ""

            bxh_mode = self.bxh_type.get() if hasattr(self, "bxh_type") else "Toàn trường"

            if bxh_mode == "Theo lớp":
                # Sắp xếp trong từng lớp, thêm cột nhóm
                merged = merged.sort_values(["lop","dtb_num"], ascending=[True, False])
                merged["hang"] = merged.groupby("lop").cumcount() + 1
            elif bxh_mode == "Theo ngành":
                merged = merged.sort_values(["nganh","dtb_num"], ascending=[True, False])
                merged["hang"] = merged.groupby("nganh").cumcount() + 1
            else:  # Toàn trường
                merged = merged.sort_values("dtb_num", ascending=False)
                merged["hang"] = range(1, len(merged) + 1)

            # Giới hạn top N
            top_val = self.top_n.get() if hasattr(self, "top_n") else "10"
            if top_val != "Tất cả":
                n = int(top_val)
                if bxh_mode in ("Theo lớp", "Theo ngành"):
                    merged = merged[merged["hang"] <= n]
                else:
                    merged = merged.head(n)

            def _xep_loai(d):
                if d >= 9:   return "Xuất sắc"
                if d >= 7:   return "Giỏi"
                if d >= 5.5: return "Khá"
                if d >= 4:   return "Trung bình"
                return "Yếu"

            for _, row in merged.iterrows():
                hang  = int(row["hang"])
                tag   = "gold" if hang == 1 else "silver" if hang == 2 else "bronze" if hang == 3 else ""
                dtb_v = row["dtb_num"]
                self.bxh_tree.insert("", "end", tags=(tag,), values=(
                    hang,
                    row.get("masv",""), row.get("hoten",""),
                    row.get("lop",""),  row.get("nganh",""),
                    f"{dtb_v:.2f}", _xep_loai(dtb_v)
                ))

            self.bxh_status.config(text=f"Hiển thị {len(merged)} sinh viên  |  Chế độ: {bxh_mode}")
        except Exception as e:
            self.bxh_status.config(text=f"Lỗi BXH: {e}")
