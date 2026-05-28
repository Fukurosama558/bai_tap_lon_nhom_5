PASS_MARK = 5.0


class DiemController:

    def __init__(self, diem_model):
        self.dm = diem_model

    # ================= TÍNH ĐTB =================

    def calc_dtb(self, cc, dk1, dk2, dt):
        return round(cc / 10 + (dk1 + dk2) * (3 / 20) + dt * 0.6, 2)

    # ================= XẾP LOẠI =================

    def xep_loai(self, dtb):
        if dtb >= 9: return "Xuất sắc"
        if dtb >= 7: return "Giỏi"
        if dtb >= 5.5: return "Khá"
        if dtb >= 4: return "Trung bình"
        return "Yếu"

    # ================= VALIDATE =================

    def validate(self, data):
        if not data["masv"]:
            return False, "Vui lòng chọn sinh viên!"

        try:
            cc = float(data["cc"])
            dk1 = float(data["dk1"])
            dk2 = float(data["dk2"])
            dt = float(data["dt"])
        except ValueError:
            return False, "Điểm phải là số!"

        # kiểm tra 0-10
        for name, val in [("CC", cc), ("ĐK1", dk1), ("ĐK2", dk2), ("ĐT", dt)]:
            if not (0 <= val <= 10):
                return False, f"{name} phải từ 0–10"

        return True, "OK"

    # ================= SAVE =================

    def save_diem(self, data, is_edit=False, edit_id=None):
        ok, msg = self.validate(data)
        if not ok:
            return False, msg

        cc, dk1, dk2, dt = float(data["cc"]), float(data["dk1"]), float(data["dk2"]), float(data["dt"])
        dtb = self.calc_dtb(cc, dk1, dk2, dt)

        record = {
            "masv": data["masv"], "hoten": data["hoten"],
            "cc": str(cc), "dk1": str(dk1), "dk2": str(dk2), "dt": str(dt),
            "diem_trung_binh": str(dtb), "ghi_chu": self.xep_loai(dtb)
        }

        # sửa hoặc thêm mới
        if is_edit:
            self.dm.update(edit_id, record)
        else:
            record["id"] = self.dm.get_next_id()
            self.dm.create(record)

        return True, "Lưu thành công!"

    # ================= DELETE =================

    def delete_diem(self, id_val):
        self.dm.delete(id_val)

    # ================= SEARCH =================

    def search_diem(self, col, keyword):
        return self.dm.search(col, keyword)