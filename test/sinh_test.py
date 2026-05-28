import random
import pandas as pd

# ================= NGÀNH =================
nganh_list = [
    ("CNTT", "Công nghệ thông tin"),
    ("QTKD", "Quản trị kinh doanh"),
    ("KT", "Kế toán"),
    ("DL", "Du lịch"),
    ("NN", "Ngôn ngữ Anh"),
]

nganh_df = pd.DataFrame([
    {"id": i + 1, "ma_nganh": ma, "ten_nganh": ten, "mo_ta": ""}
    for i, (ma, ten) in enumerate(nganh_list)
])
nganh_df.to_csv("data/nganh.csv", index=False)

# ================= SINH VIÊN =================
sv_rows = []

for i in range(1, 5001):
    ma_nganh, _ = random.choice(nganh_list)
    
    # Sinh lớp ngẫu nhiên đi kèm theo đúng mã ngành (Ví dụ: CNTT3, QTKD1)
    ten_lop = f"{ma_nganh}{random.randint(1, 5)}"

    sv_rows.append({
        "id": i,
        "masv": f"SV{i:05}",
        "hoten": f"Sinh viên {i}",
        "sdt": f"09{random.randint(10000000, 99999999)}",
        "diachi": f"Hạ Long {i}",
        "lop": ten_lop,
        "ma_nganh": ma_nganh,
        "ngay_sinh": f"{random.randint(1, 28):02}/{random.randint(1, 12):02}/{random.randint(2000, 2005)}",
        "gioi_tinh": random.choice(["Nam", "Nữ"]),
        "ghi_chu": ""
    })

sv_df = pd.DataFrame(sv_rows)
sv_df.to_csv("data/sinhvien.csv", index=False)

# ================= ĐIỂM =================
diem_rows = []

for i in range(1, 5001):
    cc = round(random.uniform(5, 10), 1)
    dk1 = round(random.uniform(3, 10), 1)
    dk2 = round(random.uniform(3, 10), 1)
    dt = round(random.uniform(2, 10), 1)

    # Tính ĐTB theo hệ số chuẩn
    dtb = round(cc * 0.1 + (dk1 + dk2) * 0.15 + dt * 0.6, 2)

    # Đồng bộ xếp loại khớp 100% với giao diện thống kê học lực
    if dtb >= 8.0:
        xl = "Giỏi"
    elif dtb >= 6.5:
        xl = "Khá"
    elif dtb >= 5.0:
        xl = "Trung bình"
    else:
        xl = "Yếu"

    diem_rows.append({
        "id": i,
        "masv": f"SV{i:05}",
        "hoten": f"Sinh viên {i}",
        "cc": cc,
        "dk1": dk1,
        "dk2": dk2,
        "dt": dt,
        "diem_trung_binh": dtb,
        "ghi_chu": xl
    })

diem_df = pd.DataFrame(diem_rows)
diem_df.to_csv("data/diem.csv", index=False)

print("Đã tạo dữ liệu test lớn thành công và đồng bộ hệ thống!")