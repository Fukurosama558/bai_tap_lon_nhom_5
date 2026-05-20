import tkinter as tk
from tkinter import messagebox
from model.sinhvien import SinhvienModel
from theme import Theme

_E_BG = "#ffffff"


class ThemSinhVienPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.sv = SinhvienModel("data/sinhvien.csv",
                                ['id','hoten','sdt','diachi','lop','tuoi'])
        self.config()
        self.view()

    def config(self):
        self.master.title("Thêm Sinh viên – Trường Đại học Hạ Long")
        self.master.geometry("700x420")
        self.master.minsize(600, 380)
        self.master.resizable(True, True)
        self.master.configure(bg=Theme.BG)

    def view(self):
        Theme.build_header(self.master, "Thêm Sinh viên",
                           back_cmd=self.back)
        self._build_form()
        self._build_statusbar()

    def _build_form(self):
        # Card chứa form
        card = tk.Frame(self.master, bg=Theme.WHITE,
                        highlightbackground=Theme.BORDER,
                        highlightthickness=1)
        card.pack(fill="both", expand=True, padx=24, pady=18)

        # Tiêu đề form
        tk.Label(card, text="Thông tin sinh viên",
                 font=(Theme.FONT, 12, "bold"),
                 bg=Theme.WHITE, fg=Theme.TEXT_DARK
                 ).grid(row=0, column=0, columnspan=4,
                        sticky="w", padx=16, pady=(16, 12))

        # Divider
        tk.Frame(card, bg=Theme.BORDER, height=1
                 ).grid(row=1, column=0, columnspan=4,
                        sticky="ew", padx=16, pady=(0, 14))

        fields = [
            ("Họ và tên *", "hoten"),
            ("Số điện thoại *", "sdt"),
            ("Địa chỉ", "diachi"),
            ("Lớp *", "lop"),
            ("Tuổi *", "tuoi"),
        ]
        self._entries = {}
        positions = [(2,0),(2,2),(3,0),(3,2),(4,0)]

        for (label, key), (row, col) in zip(fields, positions):
            tk.Label(card, text=label,
                     font=(Theme.FONT, 9, "bold"),
                     bg=Theme.WHITE, fg=Theme.TEXT_DARK
                     ).grid(row=row, column=col, sticky="w",
                            padx=(16 if col==0 else 8, 4), pady=(0,4))
            wrap, entry = Theme.make_entry(card, _E_BG)
            wrap.grid(row=row+1 if False else row,
                      column=col+1, sticky="ew",
                      padx=(0, 16 if col==2 else 8), pady=(0,10))
            # Thực ra dùng row riêng cho entry
            self._entries[key] = (wrap, entry)

        # Xếp lại đúng row cho label và entry
        for widget in card.grid_slaves():
            widget.grid_forget()

        # Label + Entry xếp đúng vị trí
        layout = [
            # (label_text, key, label_row, label_col, entry_col)
            ("Họ và tên *",       "hoten",  2, 0, 1),
            ("Số điện thoại *",   "sdt",    2, 2, 3),
            ("Địa chỉ",           "diachi", 4, 0, 1),
            ("Lớp *",             "lop",    4, 2, 3),
            ("Tuổi *",            "tuoi",   6, 0, 1),
        ]

        tk.Label(card, text="Thông tin sinh viên",
                 font=(Theme.FONT, 12, "bold"),
                 bg=Theme.WHITE, fg=Theme.TEXT_DARK
                 ).grid(row=0, column=0, columnspan=4,
                        sticky="w", padx=16, pady=(16,8))
        tk.Frame(card, bg=Theme.BORDER, height=1
                 ).grid(row=1, column=0, columnspan=4,
                        sticky="ew", padx=16, pady=(0,12))

        self._entries = {}
        for lbl_text, key, lrow, lcol, ecol in layout:
            tk.Label(card, text=lbl_text,
                     font=(Theme.FONT, 9, "bold"),
                     bg=Theme.WHITE, fg=Theme.TEXT_DARK
                     ).grid(row=lrow, column=lcol, sticky="w",
                            padx=(16 if lcol==0 else 8, 4),
                            pady=(0, 2))
            wrap, entry = Theme.make_entry(card, _E_BG)
            wrap.grid(row=lrow+1, column=ecol, sticky="ew",
                      padx=(0, 16 if ecol==3 else 8),
                      pady=(0, 10))
            card.columnconfigure(ecol, weight=1)
            self._entries[key] = entry

        # Ghi chú bắt buộc
        tk.Label(card, text="* Bắt buộc nhập",
                 font=(Theme.FONT, 8),
                 bg=Theme.WHITE, fg=Theme.TEXT_MUTED
                 ).grid(row=8, column=0, columnspan=4,
                        sticky="w", padx=16, pady=(0, 8))

        # Nút
        btn_frame = tk.Frame(card, bg=Theme.WHITE)
        btn_frame.grid(row=9, column=0, columnspan=4,
                       sticky="ew", padx=16, pady=(4, 16))

        Theme.make_btn(btn_frame, "💾  Lưu sinh viên",
                       self.create_sv, "primary",
                       padx=16, pady=8).pack(side="left", padx=(0,8))
        Theme.make_btn(btn_frame, "✖  Hủy",
                       self.back, "outline",
                       padx=16, pady=8).pack(side="left")

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Nhập thông tin sinh viên mới")
        Theme.build_statusbar(self.master, self.status_var)

    # ── Logic ──────────────────────────────────────────────────────
    def create_sv(self):
        hoten  = self._entries["hoten"].get().strip()
        sdt    = self._entries["sdt"].get().strip()
        diachi = self._entries["diachi"].get().strip()
        lop    = self._entries["lop"].get().strip()
        tuoi   = self._entries["tuoi"].get().strip()

        # Validation
        errors = []
        if not hoten:
            errors.append("Họ và tên không được để trống")
        if not sdt:
            errors.append("Số điện thoại không được để trống")
        elif not sdt.isdigit() or len(sdt) != 10:
            errors.append("Số điện thoại phải gồm đúng 10 chữ số")
        if not lop:
            errors.append("Lớp không được để trống")
        if not tuoi:
            errors.append("Tuổi không được để trống")
        elif not tuoi.isdigit() or not (16 <= int(tuoi) <= 40):
            errors.append("Tuổi phải là số từ 16 đến 40")

        if errors:
            messagebox.showwarning("Thông tin chưa hợp lệ",
                                   "\n".join(f"• {e}" for e in errors))
            return

        sv_id = self.sv.get_next_id()
        self.sv.create([sv_id, hoten, sdt, diachi, lop, tuoi])
        messagebox.showinfo("Thành công",
                            f"Đã thêm sinh viên «{hoten}» thành công!")
        self.app_manager.show_sinhvien_page()

    def back(self):
        self.app_manager.show_sinhvien_page()