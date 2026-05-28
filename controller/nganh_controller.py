class NganhController:

    def __init__(self, nganh_model):
        self.nm = nganh_model

    # ================= VALIDATE =================

    def validate(self, data, is_edit=False):
        ma = data["ma_nganh"].strip().upper()
        ten = data["ten_nganh"].strip()

        if not ma: return False, "Vui lòng nhập Mã ngành!"
        if not ten: return False, "Vui lòng nhập Tên ngành!"

        # kiểm tra trùng mã ngành
        if not is_edit:
            existing = [r for r in self.nm.search("ma_nganh", ma) if str(r.get("ma_nganh", "")).strip().upper() == ma]
            if existing:
                return False, f"Mã ngành '{ma}' đã tồn tại!"

        return True, "OK"

    # ================= SAVE =================

    def save_nganh(self, data, is_edit=False, edit_id=None):
        ok, msg = self.validate(data, is_edit)
        if not ok:
            return False, msg

        # sửa hoặc thêm mới
        if is_edit:
            self.nm.update(edit_id, data)
        else:
            data["id"] = self.nm.get_next_id()
            self.nm.create(data)

        return True, "Lưu thành công!"

    # ================= DELETE =================

    def delete_nganh(self, id_val):
        self.nm.delete(id_val)

    # ================= SEARCH =================

    def search_nganh(self, col, keyword):
        return self.nm.search(col, keyword)