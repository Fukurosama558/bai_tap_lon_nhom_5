from datetime import datetime


class SinhvienController:

    def __init__(self, sv_model, diem_model):
        self.sv = sv_model
        self.dm = diem_model

    # ================= VALIDATE =================

    def validate(self, data):
        if not data["masv"]: return False, "Vui lòng nhập Mã sinh viên!"
        if not data["hoten"]: return False, "Vui lòng nhập Họ tên!"
        if not data["lop"]: return False, "Vui lòng nhập Lớp!"
        if not data["ma_nganh"]: return False, "Vui lòng chọn Mã ngành!"
        if not data["gioi_tinh"]: return False, "Vui lòng chọn Giới tính!"

        # kiểm tra ngày sinh
        if data["ngay_sinh"]:
            try:
                datetime.strptime(data["ngay_sinh"], "%d/%m/%Y")
            except ValueError:
                return False, "Ngày sinh không hợp lệ! (dd/mm/yyyy)"

        return True, "OK"

    # ================= SAVE =================

    def save_student(self, data, is_edit=False, edit_id=None):
        ok, msg = self.validate(data)
        if not ok:
            return False, msg

        # sửa hoặc thêm mới
        if is_edit:
            self.sv.update(edit_id, data)
        else:
            data["id"] = self.sv.get_next_id()
            self.sv.create(data)
            self.create_empty_score(data["masv"], data["hoten"])

        return True, "Lưu thành công!"

    # ================= DELETE =================

    def delete_student(self, id_val):
        self.sv.delete(id_val)

    # ================= SEARCH =================

    def search_student(self, col, keyword):
        return self.sv.search(col, keyword)

    # ================= ĐIỂM TRỐNG =================

    def create_empty_score(self, masv, hoten):
        existing = [r for r in self.dm.search("masv", masv) if str(r.get("masv", "")).strip() == masv]
        if existing:
            return

        self.dm.create({
            "id": self.dm.get_next_id(), "masv": masv, "hoten": hoten,
            "cc": "", "dk1": "", "dk2": "", "dt": "", "diem_trung_binh": "",
            "ghi_chu": "Chưa có điểm"
        })