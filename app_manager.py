import tkinter as tk
from page.sinhvien_page import SinhvienPage
from page.themsinhvien_page import ThemSinhVienPage
from page.suasinhvien_page import SuaSinhVienPage


class AppManager:
    def __init__(self):
        self.root = tk.Tk()
        self.current_page = None
        self.show_sinhvien_page()

    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_page = None

    def show_sinhvien_page(self):
        self._clear()
        self.current_page = SinhvienPage(self.root, self)

    def show_them_sinhvien_page(self):
        self._clear()
        self.current_page = ThemSinhVienPage(self.root, self)

    def show_sua_sinhvien_page(self, id):
        self._clear()
        self.current_page = SuaSinhVienPage(self.root, self, id)

    def run(self):
        self.root.mainloop()