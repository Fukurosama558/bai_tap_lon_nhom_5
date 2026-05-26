import tkinter as tk
from tkinter import ttk


class AppManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quản lý Sinh viên - Đại học Hạ Long")
        self.root.geometry("1050x580")
        self.root.resizable(True, True)

        self._current_frame = None
        self._build_nav()
        self.show_sinhvien_page()

    # ── Thanh điều hướng (tab) ────────────────────────────────────────────────

    def _build_nav(self):
        nav = tk.Frame(self.root, bg="#2c3e50", pady=4)
        nav.pack(fill="x")

        tk.Label(nav, text="🎓 ĐHHL", bg="#2c3e50", fg="white",
                 font=("Arial", 13, "bold")).pack(side="left", padx=14)

        self._nav_btns = {}
        tabs = [
            ("👤 Thông tin SV", self.show_sinhvien_page),
            ("📊 Bảng điểm",   self.show_diem_page),
            ("📈 Thống kê",    self.show_thong_ke_page),
        ]
        for label, cmd in tabs:
            b = tk.Button(nav, text=label, bg="#2c3e50", fg="white",
                          relief="flat", font=("Arial", 10),
                          activebackground="#3d5166", activeforeground="white",
                          command=cmd, padx=12, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)
            self._nav_btns[label] = b

    def _set_active_tab(self, label):
        for lbl, btn in self._nav_btns.items():
            if lbl == label:
                btn.config(bg="#1a252f", relief="sunken")
            else:
                btn.config(bg="#2c3e50", relief="flat")

    # ── Điều hướng ────────────────────────────────────────────────────────────

    def _clear(self):
        if self._current_frame:
            self._current_frame.destroy()
            self._current_frame = None

    def show_sinhvien_page(self):
        from page.sinhvien_page import SinhvienPage
        self._clear()
        self._set_active_tab("👤 Thông tin SV")
        self._current_frame = SinhvienPage(self.root, self)

    def show_diem_page(self):
        from page.diem_page import DiemPage
        self._clear()
        self._set_active_tab("📊 Bảng điểm")
        self._current_frame = DiemPage(self.root, self)

    def show_thong_ke_page(self):
        from page.thong_ke_page import ThongKePage
        self._clear()
        self._set_active_tab("📈 Thống kê")
        self._current_frame = ThongKePage(self.root, self)

    # ── Chạy ─────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
