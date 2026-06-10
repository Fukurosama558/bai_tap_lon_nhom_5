import threading
import tkinter as tk
from tkinter import messagebox, ttk
import os
import webbrowser

class AppManager:

    def __init__(self):
        self.root = tk.Tk()

        # ================= WINDOW =================
        self.root.title("🎓 Hệ thống Quản lý Sinh viên - Đại học Hạ Long")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#ecf0f1")

        self._current_frame = None
        self._setup_style()
        self._build_nav()
        self._build_footer()
        self.show_sinhvien_page()

    # ================= STYLE =================
    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview", rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # ================= NAVIGATION =================
    def _build_nav(self):
        nav = tk.Frame(self.root, bg="#2c3e50", height=55)
        nav.pack(fill="x")

        # Logo
        tk.Label(nav, text="🎓 ĐHHL", bg="#2c3e50", fg="white", font=("Arial", 15, "bold")).pack(side="left", padx=16)

        # Tabs
        self._nav_btns = {}
        tabs = [
            ("👤 Sinh viên", self.show_sinhvien_page),
            ("📊 Bảng điểm", self.show_diem_page),
            ("🏫 Ngành học", self.show_nganh_page),
            ("📈 Thống kê", self.show_thong_ke_page),
        ]

        for label, cmd in tabs:
            btn = tk.Button(
                nav,
                text=label,
                command=cmd,
                bg="#2c3e50",
                fg="white",
                relief="flat",
                activebackground="#34495e",
                activeforeground="white",
                font=("Arial", 10, "bold"),
                padx=14,
                pady=6,
                cursor="hand2",
            )
            btn.pack(side="left", padx=4, pady=6)
            self._nav_btns[label] = btn

        # Right buttons
        tk.Button(
            nav, text="ℹ️ About", bg="#16a085", fg="white", relief="flat", font=("Arial", 9, "bold"), cursor="hand2", command=self._about
        ).pack(side="right", padx=10)
        tk.Button(
            nav, text="📖 Hướng dẫn", bg="#2980b9", fg="white", relief="flat", font=("Arial", 9, "bold"), cursor="hand2", command=self._open_guide).pack(side="right", padx=5)
    # ================= FOOTER =================
    def _build_footer(self):
        footer = tk.Label(
            self.root,
            text="© 2026 - Hệ thống Quản lý Sinh viên | Bài tập lớn Nhóm 5 - Đại học Hạ Long",
            bg="#dfe6e9",
            fg="#2d3436",
            anchor="w",
            padx=10,
        )
        footer.pack(fill="x", side="bottom")

    # ================= ACTIVE TAB =================
    def _set_active_tab(self, label):
        for lbl, btn in self._nav_btns.items():
            if lbl == label:
                btn.config(bg="#1abc9c", relief="sunken")
            else:
                btn.config(bg="#2c3e50", relief="flat")

    # ================= CLEAR PAGE =================
    def _clear(self):
        if self._current_frame:
            self._current_frame.destroy()
            self._current_frame = None

    # ================= PAGES =================
    def show_sinhvien_page(self):
        from page.sinhvien_page import SinhvienPage

        self._clear()
        self._set_active_tab("👤 Sinh viên")
        self._current_frame = SinhvienPage(self.root, self)

    def show_diem_page(self):
        from page.diem_page import DiemPage

        self._clear()
        self._set_active_tab("📊 Bảng điểm")
        self._current_frame = DiemPage(self.root, self)

    def show_nganh_page(self):
        from page.nganh_page import NganhPage

        self._clear()
        self._set_active_tab("🏫 Ngành học")
        self._current_frame = NganhPage(self.root, self)

    def show_thong_ke_page(self):
        from page.thong_ke_page import ThongKePage

        self._clear()
        self._set_active_tab("📈 Thống kê")
        self._current_frame = ThongKePage(self.root, self)

    # ================= ABOUT =================
    def _about(self):
        messagebox.showinfo(
            "About",
            "Hệ thống Quản lý Sinh viên\n"
            "Phiên bản: 1.0\n"
            "-----------------------------------------\n"
            "Phát triển bởi: Nhóm 5\n"
            "• Phạm Đoàn Trí Đức (Leader)\n"
            "• Phạm Thị Mỹ Duyên\n"
            "• Đinh Thị Mỹ Dung\n"
            "• Hoàng Thanh Thúy\n"
            "-----------------------------------------\n"
            "Đơn vị: Trường Đại học Hạ Long"
        )

    # ================= HƯỚNG DẪN =================
    def _open_guide(self):
        import os
        import webbrowser

        path = os.path.abspath("assets/HDSD.pdf")

        if os.path.exists(path):
            webbrowser.open(path)
        else:
            messagebox.showwarning("Thông báo", "Không tìm thấy file hướng dẫn!\nVui lòng kiểm tra thư mục assets/huong_dan_su_dung.pdf")

    # ================= LOADING =================
    def show_loading(self, text="Đang xử lý..."):
        self.loading = tk.Toplevel(self.root)
        self.loading.title("Vui lòng chờ")
        self.loading.geometry("260x90")
        self.loading.resizable(False, False)

        # Căn cửa sổ loading ra chính giữa màn hình chính
        self.loading.transient(self.root)
        
        tk.Label(self.loading, text=text, font=("Arial", 11)).pack(expand=True, pady=20)
        self.loading.grab_set()

    def hide_loading(self):
        if hasattr(self, "loading"):
            self.loading.destroy()

    def run_async(self, task, text="Đang xử lý..."):
        self.show_loading(text)

        def wrapper():
            try:
                task()
            finally:
                self.root.after(0, self.hide_loading)

        threading.Thread(target=wrapper, daemon=True).start()

    # ================= RUN =================
    def run(self):
        self.root.mainloop()