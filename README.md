# UIT Petcare - FastAPI Web Application

Hệ thống chăm sóc thú cưng toàn diện được xây dựng bằng **FastAPI + Jinja2 + MySQL** với giao diện web cho **Admin/Staff** và **Customer**.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt và chạy](#-cài-đặt-và-chạy)
- [Tính năng chính](#-tính-năng-chính)
- [Hướng dẫn sử dụng nhanh](#-hướng-dẫn-sử-dụng-nhanh)
- [Thông tin đăng nhập](#-thông-tin-đăng-nhập)

---

## 🎯 Tổng quan

**UIT Petcare Python** là hệ thống quản lý phòng khám thú cưng chạy trên web:

- Quản lý khách hàng, thú cưng, bác sĩ, lịch hẹn, khám bệnh, tiêm chủng, liệu trình.
- Quản lý lưu chuồng, checkout và tạo hóa đơn.
- Hỗ trợ in mẫu lưu chuồng (giấy cam kết + hóa đơn).
- Phân quyền theo vai trò `admin`, `staff`, `customer`.
- Đồng bộ dữ liệu mẫu và luồng nghiệp vụ từ database chuẩn của đề tài.

---

## 💻 Công nghệ sử dụng

### Backend

- **Python 3.11+**
- **FastAPI** (routing + web framework)
- **SQLAlchemy Core + PyMySQL** (truy cập MySQL)
- **Jinja2** (server-side rendering)
- **bcrypt** (băm mật khẩu)

### Frontend

- **HTML5, CSS3, JavaScript**
- **Font Awesome 6.x**
- **Chart.js** (dashboard)
- **Responsive layout** (sidebar, bảng dữ liệu, form)

### Database

- **MySQL 8.0+** (khuyến nghị)
- File schema/data chính: `petcare_mysql_database.sql`

---

## 📁 Cấu trúc dự án

```text
do_an_python/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Settings/.env
│   ├── db.py                      # DB engine + query helpers
│   ├── routers/
│   │   ├── admin_auth.py          # Đăng nhập/đăng xuất admin
│   │   ├── admin_core.py          # Module quản trị chính
│   │   ├── customer_auth.py       # Auth customer
│   │   ├── customer_pages.py      # Trang public customer
│   │   └── customer_dashboard.py  # Dashboard customer
│   ├── security.py                # Hash/verify password (bcrypt)
│   ├── templating.py              # Jinja2 compatibility helpers
│   └── session.py                 # Flash/session utilities
├── templates/                     # Giao diện Jinja2 (admin/customer/layouts)
├── static/
│   ├── assets/                    # CSS/JS chính
│   └── admin_assets/              # Ảnh/logo admin
├── scripts/
│   ├── init_db.py                 # Khởi tạo dữ liệu DB
│   ├── smoke_check.py             # Kiểm tra DB/query cơ bản
│   └── route_smoke.py             # Kiểm tra route quan trọng
├── requirements.txt
├── run_dev.py                     # Chạy init_db + uvicorn
└── README.md
```

---

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống

- Python `3.11+`
- MySQL chạy tại `localhost:3306`
- Tài khoản MySQL:
  - User: `mysql`
  - Password: `123456`

### Bước 1: Tạo môi trường và cài package

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Bước 2: Cấu hình biến môi trường

- Copy `.env.example` thành `.env` (nếu cần).
- Kiểm tra các biến DB khớp máy local.

### Bước 3: Khởi tạo dữ liệu từ `petcare_mysql_database.sql`

#### Cách 1: MySQL CLI

```bash
mysql -u mysql -p123456 -e "CREATE DATABASE IF NOT EXISTS petcare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u mysql -p123456 petcare < "petcare_mysql_database.sql"
```

#### Cách 2: phpMyAdmin

1. Mở `http://localhost/phpmyadmin`
2. Tạo database `petcare` (utf8mb4_unicode_ci)
3. Chọn tab **Import**
4. Chọn file `petcare_mysql_database.sql`
5. Bấm **Go**

#### Kiểm tra nhanh sau import

```bash
mysql -u mysql -p123456 -D petcare -e "SHOW TABLES;"
mysql -u mysql -p123456 -D petcare -e "SELECT COUNT(*) AS users FROM users;"
```

### Bước 4: Chạy ứng dụng

```bash
python run_dev.py
```

`run_dev.py` sẽ chạy khởi tạo dữ liệu và start server dev.

### URL chính

- Customer home: `http://127.0.0.1:8000/customer`
- Customer login: `http://127.0.0.1:8000/customer/login`
- Admin login: `http://127.0.0.1:8000/admin`
- Admin dashboard: `http://127.0.0.1:8000/admin/dashboard`

---

## ✨ Tính năng chính

### Admin/Staff

- Dashboard thống kê khách hàng, thú cưng, lượt khám, lưu chuồng, doanh thu.
- CRUD: khách hàng, thú cưng, bác sĩ, lịch hẹn.
- Khám bệnh có chi tiết dịch vụ/thuốc.
- Tiêm chủng, liệu trình điều trị và buổi điều trị.
- Lưu chuồng: check-in/check-out, tính tiền, tạo hóa đơn.
- Hóa đơn: tạo thủ công, tạo từ lượt khám, chi tiết nhiều nhóm dịch vụ.
- Danh mục: dịch vụ, thuốc, vaccine (có đơn giá).
- In ấn: mẫu in lưu chuồng (giấy cam kết + hóa đơn).
- Quản lý user và settings (theo phân quyền).

### Customer

- Đăng ký/đăng nhập.
- Quản lý hồ sơ thú cưng.
- Đặt lịch khám.
- Xem lịch sử khám, toa thuốc, tiêm chủng.
- Xem hóa đơn và chi tiết.

### Bảo mật và phân quyền

- Mật khẩu dùng **bcrypt**.
- Phân quyền theo vai trò (`admin`/`staff`/`customer`).
- Route guard ở backend + ẩn menu theo quyền ở frontend.

---

## 📖 Hướng dẫn sử dụng nhanh

### Luồng Admin cơ bản

1. Đăng nhập admin.
2. Tạo hoặc chọn khách hàng/thú cưng.
3. Tạo lịch hẹn hoặc phiếu khám.
4. Thực hiện lưu chuồng (nếu có), checkout để tạo hóa đơn.
5. Vào mục in lưu chuồng để xem/in giấy cam kết và hóa đơn.

### Luồng Customer cơ bản

1. Đăng ký hoặc đăng nhập bằng số điện thoại.
2. Thêm thú cưng.
3. Đặt lịch.
4. Theo dõi lịch sử khám và hóa đơn trong dashboard.

---

## 🔑 Thông tin đăng nhập

### Admin mặc định

- Username: `admin`
- Password: `123456`

### Customer mẫu

- Phone: `0901234567`
- OTP/Password: `123456`

---

**UIT Petcare Python** là hệ thống quản lý vận hành phòng khám thú cưng trên nền web.
