import pandas as pd
import numpy as np
import os


class SinhvienModel:
    def __init__(self, file_path, columns=None):
        self.file_path = file_path
        self.columns = columns  # danh sách cột cần dùng

    def _load(self):
        df = pd.read_csv(self.file_path, dtype=str)
        if self.columns:
            df = df[[c for c in self.columns if c in df.columns]]
        return df

    def _save(self, df):
        df.to_csv(self.file_path, index=False)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def list_all(self):
        return self._load().to_dict(orient="records")

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
            "data": df.iloc[start:end].to_dict(orient="records"),
        }

    def search(self, col, keyword):
        df = self._load()
        mask = df[col].astype(str).str.contains(keyword, case=False, na=False)
        return df[mask].to_dict(orient="records")

    def get_by_id(self, id_val):
        rows = self.search("id", str(id_val))
        return rows[0] if rows else None

    def create(self, record: dict):
        df = self._load()
        new_row = pd.DataFrame([record])
        df = pd.concat([df, new_row], ignore_index=True)
        self._save(df)

    def update(self, id_val, record: dict):
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

    def get_next_id(self):
        df = self._load()
        if df.empty or "id" not in df.columns:
            return 1
        ids = pd.to_numeric(df["id"], errors="coerce").dropna()
        return int(ids.max()) + 1 if not ids.empty else 1

    # ── Thống kê (dùng numpy / pandas) ───────────────────────────────────────

    def thong_ke(self):
        df = pd.read_csv(self.file_path, dtype=str)
        total = len(df)
        result = {"tong_so": total}

        # Tuổi (nếu có)
        if "tuoi" in df.columns:
            tuoi = pd.to_numeric(df["tuoi"], errors="coerce").dropna()
            if not tuoi.empty:
                result["tuoi_tb"] = round(float(np.mean(tuoi)), 2)
                result["tuoi_min"] = int(np.min(tuoi))
                result["tuoi_max"] = int(np.max(tuoi))

        # Lớp (nếu có)
        if "lop" in df.columns:
            result["theo_lop"] = df["lop"].value_counts().to_dict()

        # Điểm TB (nếu có)
        if "diem_trung_binh" in df.columns:
            dtb = pd.to_numeric(df["diem_trung_binh"], errors="coerce").dropna()
            if not dtb.empty:
                result["diem_tb"] = round(float(np.mean(dtb)), 2)
                result["diem_max"] = float(np.max(dtb))
                result["diem_min"] = float(np.min(dtb))
                # Phân loại
                result["xuat_sac"] = int((dtb >= 9.0).sum())
                result["gioi"]     = int(((dtb >= 7.0) & (dtb < 9.0)).sum())
                result["kha"]      = int(((dtb >= 5.5) & (dtb < 7.0)).sum())
                result["trung_binh"] = int(((dtb >= 4.0) & (dtb < 5.5)).sum())
                result["yeu"]      = int((dtb < 4.0).sum())

        return result
