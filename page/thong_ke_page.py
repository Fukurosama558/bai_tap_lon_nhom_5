import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


class ThongKePage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        self.pack(fill="both", expand=True)
        
        self._load_data()
        self._build_ui()
        self._draw_chart()

    # ================= LOAD DATA =================

    def _load_data(self):
        try:
            diem_df = pd.read_csv("data/diem.csv")
            sv_df = pd.read_csv("data/sinhvien.csv")
            
            diem_df["diem_trung_binh"] = pd.to_numeric(diem_df["diem_trung_binh"], errors="coerce")
            self.df = pd.merge(diem_df, sv_df[["masv", "lop"]], on="masv", how="left")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được dữ liệu\n{e}")
            self.df = pd.DataFrame()

    # ================= UI =================

    def _build_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=15, pady=10)
        tk.Label(header, text="📈 Thống kê dữ liệu sinh viên", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(side="left")

        # ===== CONTROL =====
        ctrl = tk.Frame(self, bg="white")
        ctrl.pack(fill="x", padx=15)
        
        tk.Label(ctrl, text="Chọn biểu đồ:", bg="white", font=("Arial", 11)).pack(side="left")
        self.chart_type = ttk.Combobox(ctrl, values=["Phân loại học lực", "ĐTB theo lớp", "Phân bố điểm"], state="readonly", width=25)
        self.chart_type.current(0)
        self.chart_type.pack(side="left", padx=10)
        ttk.Button(ctrl, text="Vẽ biểu đồ", command=self._draw_chart).pack(side="left")

        # ===== MAIN LAYOUT =====
        main = tk.Frame(self, bg="white")
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # LEFT PANEL : Thống kê số liệu
        left = tk.Frame(main, bg="#f7f9fb", width=260, bd=1, relief="solid")
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left, text="📋 Thống kê", font=("Arial", 13, "bold"), bg="#f7f9fb").pack(pady=10)

        total = len(self.df)
        avg = round(self.df["diem_trung_binh"].mean(), 2) if total > 0 else 0
        max_score = round(self.df["diem_trung_binh"].max(), 2) if total > 0 else 0
        min_score = round(self.df["diem_trung_binh"].min(), 2) if total > 0 else 0

        stats = [f"Tổng sinh viên: {total}", f"ĐTB toàn trường: {avg}", f"Điểm cao nhất: {max_score}", f"Điểm thấp nhất: {min_score}"]
        for s in stats:
            tk.Label(left, text=s, bg="#f7f9fb", anchor="w", font=("Arial", 11)).pack(fill="x", padx=15, pady=5)

        # Chú thích học lực
        tk.Label(left, text="📌 Chú thích", bg="#f7f9fb", font=("Arial", 11, "bold")).pack(anchor="w", padx=15, pady=(20, 5))
        notes = ["Giỏi: >= 8.0", "Khá: 6.5 → < 8.0", "Trung bình: 5.0 → < 6.5", "Yếu: < 5.0"]
        for n in notes:
            tk.Label(left, text=f"• {n}", bg="#f7f9fb", anchor="w").pack(fill="x", padx=20, pady=2)

        # RIGHT PANEL : Đồ thị Matplotlib
        right = tk.Frame(main, bg="white")
        right.pack(side="left", fill="both", expand=True)

        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= DRAW CHART =================

    def _draw_chart(self):
        if self.df.empty: return
        self.ax.clear()
        choice = self.chart_type.get()

        # 1. PHÂN LOẠI HỌC LỰC (Pie Chart)
        if choice == "Phân loại học lực":
            dtb = self.df["diem_trung_binh"]
            gioi = len(self.df[dtb >= 8])
            kha = len(self.df[(dtb >= 6.5) & (dtb < 8)])
            tb = len(self.df[(dtb >= 5) & (dtb < 6.5)])
            yeu = len(self.df[dtb < 5])

            self.ax.pie([gioi, kha, tb, yeu], labels=["Giỏi", "Khá", "TB", "Yếu"], autopct="%1.1f%%")
            self.ax.set_title("Phân loại học lực")

        # 2. ĐTB THEO LỚP (Bar Chart)
        elif choice == "ĐTB theo lớp":
            data = self.df.groupby("lop")["diem_trung_binh"].mean().sort_values(ascending=False)
            self.ax.bar(data.index, data.values)
            self.ax.set_title("Điểm trung bình theo lớp")
            self.ax.set_ylabel("ĐTB")
            self.ax.tick_params(axis="x", rotation=15)

        # 3. PHÂN BỐ ĐIỂM (Histogram)
        elif choice == "Phân bố điểm":
            self.ax.hist(self.df["diem_trung_binh"].dropna(), bins=10)
            self.ax.set_title("Phân bố điểm")
            self.ax.set_xlabel("Điểm")
            self.ax.set_ylabel("Số lượng")

        # Cập nhật render
        self.fig.tight_layout()
        self.canvas.draw_idle()