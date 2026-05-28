import os
import numpy as np
import pandas as pd


class SinhvienModel:

    def __init__(self, file_path, columns=None):
        self.file_path = file_path
        self.columns = columns or []

    # ================= LOAD / SAVE =================

    def _load(self):
        # tạo file nếu chưa có
        if not os.path.exists(self.file_path):
            pd.DataFrame(columns=self.columns).to_csv(self.file_path, index=False)

        df = pd.read_csv(self.file_path, dtype=str).fillna("")
        
        # lọc cột
        if self.columns:
            df = df[[c for c in self.columns if c in df.columns]]
        return df

    def _save(self, df):
        df.to_csv(self.file_path, index=False)

    # ================= CRUD =================

    def list_all(self):
        return self._load().to_dict(orient="records")

    def get_by_id(self, id_val):
        df = self._load()
        rows = df[df["id"].astype(str) == str(id_val)]
        return rows.iloc[0].to_dict() if not rows.empty else None

    def create(self, record):
        df = self._load()
        new_row = pd.DataFrame([record])
        df = pd.concat([df, new_row], ignore_index=True)
        self._save(df)

    def update(self, id_val, record):
        df = self._load()
        mask = df["id"].astype(str) == str(id_val)
        for col, val in record.items():
            if col in df.columns:
                df.loc[mask, col] = val
        self._save(df)

    def delete(self, id_val):
        df = self._load()
        df = df[df["id"].astype(str) != str(id_val)]
        self._save(df)

    # ================= SEARCH =================

    def search(self, col, keyword):
        df = self._load()
        if col not in df.columns:
            return []
        
        mask = df[col].astype(str).str.contains(keyword, case=False, na=False)
        return df[mask].to_dict(orient="records")

    # ================= PAGINATION =================

    def list_page(self, page=1, page_size=100):
        df = self._load()
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
            "data": df.iloc[start:end].to_dict(orient="records")
        }

    # ================= AUTO ID =================

    def get_next_id(self):
        df = self._load()
        if df.empty:
            return 1
        
        ids = pd.to_numeric(df["id"], errors="coerce").dropna()
        return int(ids.max()) + 1 if not ids.empty else 1

    # ================= THỐNG KÊ =================

    def thong_ke(self):
        df = self._load()
        result = {"tong_so": len(df)}

        # điểm trung bình
        if "diem_trung_binh" in df.columns:
            dtb = pd.to_numeric(df["diem_trung_binh"], errors="coerce").dropna()
            if not dtb.empty:
                result["diem_tb"] = round(float(np.mean(dtb)), 2)
                result["diem_max"] = float(np.max(dtb))
                result["diem_min"] = float(np.min(dtb))

        # thống kê lớp
        if "lop" in df.columns:
            result["theo_lop"] = df["lop"].value_counts().to_dict()

        return result