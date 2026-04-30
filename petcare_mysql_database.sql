-- =====================================================
-- UIT PETCARE - MySQL Database
-- =====================================================

-- Tạo database (nếu chưa có)
CREATE DATABASE IF NOT EXISTS petcare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE petcare;

-- =====================================================
-- PHẦN 1: TẠO CẤU TRÚC BẢNG
-- =====================================================

DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS invoice_vaccination_details;
DROP TABLE IF EXISTS invoice_medicine_details;
DROP TABLE IF EXISTS medical_record_services;
DROP TABLE IF EXISTS medical_record_medicines;
DROP TABLE IF EXISTS diagnoses;
DROP TABLE IF EXISTS treatment_sessions;
DROP TABLE IF EXISTS treatment_courses;
DROP TABLE IF EXISTS pet_vaccinations;
DROP TABLE IF EXISTS invoice_details;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS pet_enclosures;
DROP TABLE IF EXISTS vaccination_records;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS otp_codes;
DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS general_settings;
DROP TABLE IF EXISTS vaccines;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS service_types;
DROP TABLE IF EXISTS users;

-- Bảng người dùng
CREATE TABLE users (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    password VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    fullname VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    avatar VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    role ENUM('admin', 'staff', 'customer') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL DEFAULT 'staff',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng loại dịch vụ
CREATE TABLE service_types (
    service_type_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    description TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    price DECIMAL(10,2) DEFAULT 0
);

-- Bảng thuốc
CREATE TABLE medicines (
    medicine_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    medicine_route ENUM('PO', 'IM', 'IV', 'SC') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    unit_price INT(11) NOT NULL DEFAULT 0
);

-- Bảng vaccine
CREATE TABLE vaccines (
    vaccine_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    vaccine_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    description TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    unit_price INT(11) NOT NULL DEFAULT 0
);

-- Bảng cài đặt chung
CREATE TABLE general_settings (
    setting_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    clinic_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    clinic_address_1 VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    clinic_address_2 VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    phone_number_1 VARCHAR(11) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    phone_number_2 VARCHAR(11) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    representative_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    checkout_hour TIME DEFAULT '18:00:00',
    overtime_fee_per_hour INT(11) DEFAULT 0,
    default_daily_rate INT(11) DEFAULT 0,
    signing_place VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL
);

-- Bảng khách hàng
CREATE TABLE customers (
    customer_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    customer_phone_number VARCHAR(11) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    customer_email VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    customer_identity_card VARCHAR(12) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    customer_address VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    customer_note TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL
);

-- Bảng bác sĩ
CREATE TABLE doctors (
    doctor_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    doctor_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    doctor_phone_number VARCHAR(11) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    doctor_identity_card VARCHAR(12) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    doctor_address VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    doctor_note TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL
);

-- Bảng thú cưng
CREATE TABLE pets (
    pet_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_id INT(11) NOT NULL,
    pet_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    pet_species VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    pet_gender ENUM('0', '1') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL COMMENT '0: đực, 1: cái',
    pet_dob DATE DEFAULT NULL,
    pet_weight DECIMAL(10,2) DEFAULT NULL,
    pet_sterilization ENUM('0', '1') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL COMMENT '0: chưa triệt sản, 1: đã triệt sản',
    pet_characteristic TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    pet_drug_allergy TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng hồ sơ y tế
CREATE TABLE medical_records (
    medical_record_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    doctor_id INT(11) NOT NULL,
    medical_record_type ENUM('Khám', 'Điều trị', 'Vaccine') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    medical_record_visit_date DATE NOT NULL,
    medical_record_summary TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    medical_record_details TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng hồ sơ tiêm chủng
CREATE TABLE vaccination_records (
    medical_record_id INT(11) NOT NULL,
    vaccine_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    batch_number VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    next_injection_date DATE DEFAULT NULL,
    PRIMARY KEY (medical_record_id, vaccine_name),
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng lưu chuồng
CREATE TABLE pet_enclosures (
    pet_enclosure_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    pet_enclosure_number INT(11) NOT NULL,
    check_in_date DATETIME NOT NULL,
    check_out_date DATETIME,
    daily_rate INT(11) NOT NULL,
    deposit INT(11) DEFAULT 0,
    emergency_limit INT(11) DEFAULT 0,
    pet_enclosure_note TEXT,
    pet_enclosure_status ENUM('Check In', 'Check Out') NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng hóa đơn
CREATE TABLE invoices (
    invoice_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    pet_enclosure_id INT(11) DEFAULT NULL,
    medical_record_id INT(11) DEFAULT NULL,
    invoice_date DATETIME NOT NULL,
    discount INT(11) DEFAULT 0,
    subtotal INT(11) NOT NULL,
    deposit INT(11) DEFAULT 0,
    total_amount INT(11) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_enclosure_id) REFERENCES pet_enclosures(pet_enclosure_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Bảng chi tiết hóa đơn
CREATE TABLE invoice_details (
    detail_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT(11) NOT NULL,
    service_type_id INT(11) NOT NULL,
    quantity INT(11) NOT NULL,
    unit_price INT(11) NOT NULL,
    total_price INT(11) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng tiêm chủng thú cưng (gắn với lượt khám)
CREATE TABLE pet_vaccinations (
    pet_vaccination_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    vaccine_id INT(11) NOT NULL,
    medical_record_id INT(11) DEFAULT NULL,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    doctor_id INT(11) NOT NULL,
    vaccination_date DATE NOT NULL,
    next_vaccination_date DATE DEFAULT NULL,
    notes TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    FOREIGN KEY (vaccine_id) REFERENCES vaccines(vaccine_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng liệu trình điều trị (gắn với lượt khám)
CREATE TABLE treatment_courses (
    treatment_course_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    medical_record_id INT(11) DEFAULT NULL,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('0', '1') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL COMMENT '1 = Đang điều trị, 0 = Kết thúc',
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng buổi điều trị
CREATE TABLE treatment_sessions (
    treatment_session_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    treatment_course_id INT(11) NOT NULL,
    doctor_id INT(11) NOT NULL,
    treatment_session_datetime DATETIME NOT NULL,
    temperature DECIMAL(10,2) NOT NULL,
    weight DECIMAL(10,2) NOT NULL,
    pulse_rate INT(11),
    respiratory_rate INT(11),
    overall_notes TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci,
    FOREIGN KEY (treatment_course_id) REFERENCES treatment_courses(treatment_course_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng chẩn đoán
CREATE TABLE diagnoses (
    diagnosis_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    treatment_session_id INT(11) NOT NULL,
    diagnosis_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    diagnosis_type ENUM('0', '1') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL COMMENT '0 = Phụ, 1 = Chính',
    clinical_tests TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci,
    notes TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci,
    FOREIGN KEY (treatment_session_id) REFERENCES treatment_sessions(treatment_session_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng đơn thuốc
CREATE TABLE prescriptions (
    prescription_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    treatment_session_id INT(11) NOT NULL,
    medicine_id INT(11) NOT NULL,
    treatment_type ENUM('tiêm', 'uống', 'truyền') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    dosage DECIMAL(10,2) NOT NULL,
    unit ENUM('ml', 'mg', 'mg/kg', 'g', 'viên', 'giọt', '%') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    frequency VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci,
    status ENUM('0', '1') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL COMMENT '1 = Đang thực hiện, 0 = Đã làm',
    notes TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci,
    FOREIGN KEY (treatment_session_id) REFERENCES treatment_sessions(treatment_session_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Thuốc kê trong lượt khám
CREATE TABLE medical_record_medicines (
    record_medicine_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    medical_record_id INT(11) NOT NULL,
    medicine_id INT(11) NOT NULL,
    quantity INT(11) NOT NULL,
    unit_price INT(11) NOT NULL,
    total_price INT(11) NOT NULL,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Dịch vụ đã thêm trong lượt khám
CREATE TABLE medical_record_services (
    record_service_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    medical_record_id INT(11) NOT NULL,
    service_type_id INT(11) NOT NULL,
    quantity INT(11) NOT NULL,
    unit_price INT(11) NOT NULL,
    total_price INT(11) NOT NULL,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(medical_record_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Chi tiết thuốc trên hóa đơn (xuất hóa đơn từ lượt khám)
CREATE TABLE invoice_medicine_details (
    detail_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT(11) NOT NULL,
    medicine_id INT(11) NOT NULL,
    quantity INT(11) NOT NULL,
    unit_price INT(11) NOT NULL,
    total_price INT(11) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Chi tiết tiêm chủng trên hóa đơn (từ lượt khám)
CREATE TABLE invoice_vaccination_details (
    detail_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT(11) NOT NULL,
    vaccine_id INT(11) NOT NULL,
    quantity INT(11) NOT NULL,
    unit_price INT(11) NOT NULL,
    total_price INT(11) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES vaccines(vaccine_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Bảng đặt lịch hẹn (Appointments)
CREATE TABLE appointments (
    appointment_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    customer_id INT(11) NOT NULL,
    pet_id INT(11) NOT NULL,
    doctor_id INT(11) DEFAULT NULL,
    service_type_id INT(11) DEFAULT NULL,
    appointment_date DATETIME NOT NULL,
    appointment_type ENUM('Khám', 'Spa', 'Tiêm chủng') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL DEFAULT 'pending',
    notes TEXT CHARACTER SET utf8 COLLATE utf8_vietnamese_ci DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Bảng mã OTP (OTP Codes)
CREATE TABLE otp_codes (
    otp_id INT(11) AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    otp_code VARCHAR(6) CHARACTER SET utf8 COLLATE utf8_vietnamese_ci NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used TINYINT(1) DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone_number),
    INDEX idx_expires (expires_at)
);

-- =====================================================
-- PHẦN 2: DỮ LIỆU MẪU
-- =====================================================

-- === USERS ===
INSERT INTO users (username, password, fullname, avatar, role, created_at) VALUES
('admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeapvT9gqHHhU1pKuMj2cpskE48fM3Kwy', 'Quản trị viên', NULL, 'admin', NOW()),
('staff', '$2a$10$EixZaYVK1fsbw1ZfbX3OXeabk2r5C7ovVRf5NIaezHaxeq67HvBQS', 'Nhân viên', NULL, 'staff', NOW()),
('lethimai', '$2a$10$EixZaYVK1fsbw1ZfbX3OXeabk2r5C7ovVRf5NIaezHaxeq67HvBQS', 'Lê Thị Mai', NULL, 'staff', NOW()),
('tranhung', '$2a$10$EixZaYVK1fsbw1ZfbX3OXeabk2r5C7ovVRf5NIaezHaxeq67HvBQS', 'Trần Văn Hùng', NULL, 'staff', NOW()),
('nguyenlan', '$2a$10$EixZaYVK1fsbw1ZfbX3OXeabk2r5C7ovVRf5NIaezHaxeq67HvBQS', 'Nguyễn Thị Lan', NULL, 'staff', NOW()),
('phamquang', '$2a$10$EixZaYVK1fsbw1ZfbX3OXeabk2r5C7ovVRf5NIaezHaxeq67HvBQS', 'Phạm Quang Minh', NULL, 'staff', NOW());

-- === SERVICE TYPES ===
INSERT INTO service_types (service_name, description, price) VALUES
('Lưu chuồng theo ngày', 'Dịch vụ lưu trú cho thú cưng theo ngày, có camera giám sát 24/7.', 150000),
('Phụ thu trễ giờ', 'Phí phụ thu cho khách đến đón muộn sau 18h.', 50000),
('Đồ gửi kèm', 'Nhận giữ đồ dùng cá nhân của thú cưng như gối, chăn, đồ chơi.', 30000),
('Tắm thú cưng', 'Tắm rửa, sấy khô, chăm sóc lông da chuyên nghiệp.', 200000),
('Cắt tỉa lông', 'Cắt tỉa lông tạo kiểu theo yêu cầu của chủ nuôi.', 180000),
('Khám sức khỏe định kỳ', 'Khám tổng quát định kỳ, kiểm tra sức khỏe toàn diện.', 150000),
('Tiêm phòng vắc xin', 'Phòng ngừa các bệnh truyền nhiễm nguy hiểm.', 250000),
('Vệ sinh tai', 'Làm sạch tai, ngừa viêm nhiễm.', 80000),
('Vệ sinh răng miệng', 'Làm sạch răng, khử mùi hôi miệng.', 120000),
('Massage thư giãn', 'Massage thư giãn giúp thú cưng giảm stress.', 150000),
('Huấn luyện cơ bản', 'Dạy các lệnh cơ bản: ngồi, nằm, bắt tay, đi theo.', 400000),
('Thức ăn theo ngày', 'Cung cấp thức ăn chất lượng phù hợp với từng loài.', 60000),
('Cắt móng', 'Cắt móng chân an toàn, không gây đau.', 60000),
('Tắm dưỡng lông', 'Dưỡng lông mềm mượt, suôn mượt.', 250000),
('Tẩy giun định kỳ', 'Tẩy giun định kỳ theo lịch.', 120000),
('Phẫu thuật nhỏ', 'Tiểu phẫu, triệt sản.', 800000),
('Chụp X-quang', 'Kiểm tra xương khớp, phát hiện bất thường.', 250000),
('Siêu âm', 'Kiểm tra các cơ quan nội tạng.', 350000),
('Tư vấn dinh dưỡng', 'Tư vấn chế độ ăn uống phù hợp với thể trạng.', 100000);

-- === GENERAL SETTINGS ===
INSERT INTO general_settings (
    clinic_name, clinic_address_1, clinic_address_2,
    phone_number_1, phone_number_2,
    representative_name, checkout_hour,
    overtime_fee_per_hour, default_daily_rate, signing_place
) VALUES (
    'UIT Petcare',
    'Hàn Thuyên, Khu phố 6 P, Thủ Đức, TP. Hồ Chí Minh',
    '',
    '0283725002',
    '',
    '',
    '18:00:00',
    25000,
    80000,
    'TP. Hồ Chí Minh'
);

-- === MEDICINES ===
INSERT INTO medicines (medicine_name, medicine_route, unit_price) VALUES
('Amoxicillin 250mg', 'PO', 15000),
('Cefotaxime 1g', 'IM', 45000),
('Vitamin C 500mg', 'IV', 25000),
('Ivermectin 1%', 'SC', 35000),
('Metronidazole 250mg', 'PO', 12000),
('Dexamethasone 4mg', 'IM', 18000),
('Prednisolone 5mg', 'PO', 8000),
('Enrofloxacin 50mg', 'PO', 22000);

-- === VACCINES ===
INSERT INTO vaccines (vaccine_name, description, unit_price) VALUES
('Vacxin Dại Rabisin', 'Phòng chống bệnh dại cho chó mèo, tiêm định kỳ 12 tháng/lần.', 150000),
('Vacxin 7 bệnh DHPPiL', 'Phòng 7 bệnh phổ biến cho chó: Carré, Parvo, Viêm gan...', 200000),
('Vacxin Care', 'Phòng bệnh Care (sài sốt) ở chó, nguy hiểm và dễ lây lan.', 180000),
('Vacxin Parvo', 'Phòng bệnh Parvo gây tiêu chảy, nôn mửa nghiêm trọng ở chó.', 120000),
('Vacxin 4 bệnh mèo FVRCP', 'Phòng 4 bệnh cho mèo: viêm mũi, calici, chlamydia, panleukopenia.', 220000);

-- === CUSTOMERS ===
INSERT INTO customers (customer_name, customer_phone_number, customer_identity_card, customer_address, customer_note) VALUES
('Trần Minh Tuấn', '0912345678', '079123456789', '125 Lê Văn Việt, Q9, TP.HCM', 'Khách hàng VIP, thường gửi dài hạn.'),
('Nguyễn Thị Hương', '0987654321', '079987654321', '88 Nguyễn Thị Minh Khai, Q1, TP.HCM', 'Mèo bị dị ứng một số loại thuốc.'),
('Lê Hoàng Nam', '0909123456', '079111222333', '45 Trần Hưng Đạo, Q5, TP.HCM', 'Hay đi công tác, gửi thường xuyên.'),
('Phạm Thu Trang', '0918765432', '079444555666', '200 Điện Biên Phủ, Q3, TP.HCM', 'Yêu cầu gọi trước khi đón.'),
('Võ Minh Khoa', '0933221100', '079777888999', '78 Võ Văn Tần, Q3, TP.HCM', 'Có 2 chó, thích phòng rộng.'),
('Đặng Thị Lan', '0944556677', '079000111222', '156 Nguyễn Huệ, Q1, TP.HCM', 'Thường gửi cuối tuần.'),
('Huỳnh Văn Đức', '0955667788', '079333444555', '34 Lý Tự Trọng, Q1, TP.HCM', NULL),
('Lý Thị Hồng', '0966778899', '079666777888', '90 Hai Bà Trưng, Q1, TP.HCM', 'Khách quen từ năm 2023.'),
('Bùi Quốc Cường', '0977889900', '079999000111', '67 Pasteur, Q1, TP.HCM', NULL),
('Cao Thị Yến', '0988990011', '079222333444', '123 Nam Kỳ Khởi Nghĩa, Q3, TP.HCM', 'Mèo lông dài, cần chải lông kỹ.'),
('Đinh Văn Phú', '0999001122', '079555666777', '45 Cách Mạng Tháng 8, Q10, TP.HCM', NULL),
('Hồ Thị Ngọc', '0900112233', '079888999000', '78 Nguyễn Văn Trỗi, Phú Nhuận', 'Chó rất nhát, cần nhẹ nhàng.'),
('Lâm Minh Quân', '0911223344', '079012345678', '234 Trường Chinh, Tân Bình', NULL),
('Mai Thị Diễm', '0922334455', '079345678901', '56 Lê Quang Định, Bình Thạnh', 'VIP'),
('Ngô Văn Thành', '0933445566', '079678901234', '89 Huỳnh Tấn Phát, Q7', NULL),
('Phan Thị Kim', '0944556688', '079901234567', '12 Nguyễn Thông, Q3', 'Thích phòng có điều hòa.'),
('Quách Văn Hải', '0955667799', '079234567890', '145 Phan Đăng Lưu, Phú Nhuận', NULL),
('Sơn Thị Linh', '0966778800', '079567890123', '67 Nguyễn Kiệm, Gò Vấp', NULL),
('Tạ Minh Đức', '0977889911', '079890123456', '234 Lê Văn Sỹ, Q3', 'Có chó giống lớn.'),
('Ung Thị Hà', '0988990022', '079123098765', '98 Võ Văn Kiệt, Q6', NULL),
('Khách hàng', '0901234567', NULL, NULL, NULL);

-- === DOCTORS ===
INSERT INTO doctors (doctor_name, doctor_phone_number, doctor_identity_card, doctor_address, doctor_note) VALUES
('BS. Trần Thanh Phong', '0909111222', '079111111111', '125 Nguyễn Đình Chiểu, Q3', 'Chuyên khoa nội, 10 năm kinh nghiệm.'),
('BS. Lê Thị Thanh Mai', '0918222333', '079222222222', '78 Võ Thị Sáu, Q3', 'Chuyên tiêm phòng và da liễu.'),
('BS. Nguyễn Hoàng Sơn', '0927333444', '079333333333', '200 Cống Quỳnh, Q1', 'Chuyên phẫu thuật.'),
('BS. Phạm Minh Châu', '0936444555', '079444444444', '34 Nguyễn Kiệm, Gò Vấp', 'Chuyên dinh dưỡng và theo dõi sau điều trị.'),
('BS. Võ Đức Anh', '0945555666', '079555555555', '56 Trần Não, Q2', 'Chuyên chẩn đoán hình ảnh.'),
('BS. Hoàng Thị Hạnh', '0954666777', '079666666666', '89 Phạm Văn Đồng, Thủ Đức', 'Khám tổng quát.'),
('BS. Đỗ Quang Vinh', '0963777888', '079777777777', '123 Điện Biên Phủ, Q3', 'Chuyên bệnh truyền nhiễm.'),
('BS. Lý Minh Tuấn', '0972888999', '079888888888', '67 Nguyễn Văn Cừ, Q5', 'Bác sĩ trực đêm.');

-- === PETS ===
INSERT INTO pets (customer_id, pet_name, pet_species, pet_gender, pet_dob, pet_weight, pet_sterilization, pet_characteristic, pet_drug_allergy) VALUES
(1, 'Mochi', 'Chó Poodle', '1', '2022-03-15', 5.8, '1', 'Hiếu động, thích chơi bóng.', NULL),
(1, 'Pudding', 'Chó Poodle', '0', '2023-06-20', 4.5, '0', 'Rất thân thiện với người lạ.', NULL),
(2, 'Mimi', 'Mèo Anh lông ngắn', '1', '2021-08-10', 4.2, '1', 'Lười vận động, thích nằm.', 'Penicillin'),
(3, 'Max', 'Chó Corgi', '0', '2023-02-01', 9.5, '0', 'Năng động, hay sủa.', NULL),
(4, 'Luna', 'Chó Shiba Inu', '1', '2022-11-11', 8.8, '1', 'Trung thành, kén ăn.', NULL),
(5, 'Kitty', 'Mèo Ba Tư', '1', '2023-09-09', 3.5, '0', 'Dễ chăm sóc, ăn uống tốt.', NULL),
(5, 'Muffin', 'Chó Pug', '0', '2021-05-12', 7.8, '1', 'Thích ăn, hơi béo.', NULL),
(6, 'Snowball', 'Mèo Ragdoll', '1', '2022-07-30', 5.2, '1', 'Hiền lành, dễ bế.', NULL),
(7, 'Rocky', 'Chó Husky', '0', '2020-12-22', 22.5, '1', 'Sôi nổi, hay tru.', NULL),
(8, 'Chloe', 'Mèo Xiêm', '1', '2024-04-10', 3.0, '0', 'Thích leo trèo, tò mò.', NULL),
(9, 'Cooper', 'Chó Golden Retriever', '0', '2023-02-02', 28.0, '0', 'Rất thân thiện với trẻ em.', NULL),
(10, 'Bella', 'Mèo Ba Tư', '1', '2023-06-09', 4.0, '0', 'Thích tắm, lông dày.', NULL),
(11, 'Charlie', 'Chó Cocker Spaniel', '0', '2021-07-17', 12.5, '1', 'Ngoan, biết nhiều trò.', NULL),
(12, 'Tom', 'Mèo Munchkin', '0', '2022-01-01', 3.8, '0', 'Chân ngắn, dễ thương.', NULL),
(13, 'Nala', 'Mèo Scottish Fold', '1', '2024-03-12', 3.2, '0', 'Tai cụp, rất cute.', NULL),
(14, 'Duke', 'Chó Becgie', '0', '2021-09-09', 25.0, '1', 'Canh gác tốt, trung thành.', NULL),
(15, 'Buddy', 'Chó Samoyed', '0', '2022-10-10', 24.0, '1', 'Lông trắng, rất thân thiện.', NULL),
(16, 'Sophie', 'Mèo Sphynx', '1', '2023-08-01', 3.2, '0', 'Không có lông, cần giữ ấm.', NULL),
(17, 'Teddy', 'Chó Pomeranian', '0', '2024-01-05', 2.5, '0', 'Nhỏ, nhanh nhẹn, hay sủa.', NULL),
(18, 'Daisy', 'Chó Chihuahua', '1', '2024-12-25', 2.2, '0', 'Hơi sợ người lạ.', NULL);

-- === MEDICAL RECORDS ===
INSERT INTO medical_records (customer_id, pet_id, doctor_id, medical_record_type, medical_record_visit_date, medical_record_summary, medical_record_details) VALUES
(1, 1, 1, 'Khám', '2026-01-20', 'Khám tổng quát định kỳ cho Mochi.', 'Sức khỏe ổn định, cân nặng đạt chuẩn, không có dấu hiệu bất thường.'),
(1, 2, 2, 'Vaccine', '2026-01-22', 'Tiêm phòng dại cho Pudding.', 'Đã tiêm 1 mũi Rabisin, theo dõi 30 phút sau tiêm, phản ứng tốt.'),
(2, 3, 3, 'Điều trị', '2026-01-18', 'Điều trị viêm da dị ứng cho Mimi.', 'Bôi thuốc kháng viêm trong 7 ngày, tránh thức ăn có hải sản.'),
(3, 4, 4, 'Khám', '2026-01-25', 'Khám lần đầu cho Max.', 'Cún khỏe mạnh, đề nghị tiêm phòng vaccine 7 bệnh.'),
(4, 5, 5, 'Điều trị', '2026-01-16', 'Điều trị viêm tai cho Luna.', 'Làm sạch tai, kê thuốc nhỏ tai và kháng sinh uống 5 ngày.'),
(5, 6, 2, 'Vaccine', '2026-01-15', 'Tiêm phòng 4 bệnh cho Kitty.', 'Đã tiêm FVRCP, không có phản ứng phụ.'),
(6, 8, 1, 'Khám', '2026-01-16', 'Khám sức khỏe cho Snowball.', 'Ổn định, cân nặng 5.2kg, mắt trong.'),
(7, 9, 2, 'Vaccine', '2026-01-17', 'Tiêm phòng 7 bệnh cho Rocky.', 'Tiêm DHPPiL, theo dõi tốt.'),
(8, 10, 5, 'Điều trị', '2026-01-17', 'Điều trị rối loạn tiêu hóa cho Chloe.', 'Kê thuốc men tiêu hóa 5 ngày, ăn cháo loãng.'),
(9, 11, 4, 'Khám', '2026-01-19', 'Khám tổng quát cho Cooper.', 'Sức khỏe tốt, đề xuất tẩy giun định kỳ.'),
(10, 12, 3, 'Điều trị', '2026-01-16', 'Viêm da nhẹ ở tai phải Bella.', 'Bôi thuốc hằng ngày, kiểm tra lại sau 1 tuần.'),
(11, 13, 1, 'Khám', '2026-01-21', 'Khám định kỳ cho Charlie.', 'Đề xuất tiêm phòng dại.'),
(12, 14, 4, 'Vaccine', '2026-01-22', 'Tiêm phòng dại cho Tom.', 'Tiêm Rabisin, theo dõi tốt.'),
(13, 15, 5, 'Điều trị', '2026-01-24', 'Điều trị nấm ngoài da cho Nala.', 'Tắm bằng dung dịch đặc trị, 3 lần/tuần.'),
(14, 16, 6, 'Khám', '2026-01-26', 'Khám kiểm tra sau điều trị Duke.', 'Tình trạng da đã cải thiện 95%.'),
(15, 17, 7, 'Vaccine', '2026-01-27', 'Tiêm phòng 7 bệnh cho Buddy.', 'Không phản ứng phụ, sức khỏe tốt.'),
(16, 18, 1, 'Điều trị', '2026-01-17', 'Điều trị cảm lạnh cho Sophie.', 'Giữ ấm, vitamin C và kháng sinh 3 ngày.'),
(17, 19, 8, 'Khám', '2026-01-19', 'Khám sức khỏe tổng quát Teddy.', 'Ổn định, cân nặng đạt chuẩn giống Pomeranian.'),
(18, 20, 2, 'Điều trị', '2026-01-21', 'Điều trị stress do xa chủ cho Daisy.', 'Bổ sung vitamin, tạo môi trường thoải mái.'),
(19, 3, 3, 'Vaccine', '2026-01-25', 'Tiêm vaccine 4 bệnh mèo cho Mimi.', 'Hoàn tất FVRCP, theo dõi tốt.'),
(1, 1, 1, 'Khám', '2026-01-30', 'Khám định kỳ tháng 1 cho Mochi.', 'Sức khỏe tốt, cân nặng ổn định.'),
(2, 3, 2, 'Vaccine', '2026-01-30', 'Tiêm nhắc vaccine dại cho Mimi.', 'Đã tiêm Rabisin, phản ứng tốt.'),
(3, 4, 4, 'Khám', '2026-01-31', 'Khám kiểm tra sức khỏe Max.', 'Cún khỏe, đề xuất tẩy giun.'),
(4, 5, 5, 'Điều trị', '2026-01-31', 'Kiểm tra tai Luna sau điều trị.', 'Tai đã lành, ngừng thuốc.');

-- === VACCINATION RECORDS ===
INSERT INTO vaccination_records (medical_record_id, vaccine_name, batch_number, next_injection_date) VALUES
(2, 'Rabisin (Phòng dại)', 'RBS-2026-01', '2027-01-22'),
(6, 'FVRCP (Phòng 4 bệnh mèo)', 'FVR-2026-01', '2027-01-15'),
(8, 'DHPPiL (Phòng 7 bệnh)', 'DHP-2026-01', '2027-01-17'),
(13, 'Rabisin (Phòng dại)', 'RBS-2026-01B', '2027-01-22'),
(16, 'DHPPiL (Phòng 7 bệnh)', 'DHP-2026-01', '2027-01-27'),
(20, 'FVRCP (Phòng 4 bệnh mèo)', 'FVR-2026-01B', '2027-01-25'),
(22, 'Rabisin (Phòng dại)', 'RBS-2026-01C', '2027-01-30');

-- === MEDICAL RECORD MEDICINES ===
INSERT INTO medical_record_medicines (medical_record_id, medicine_id, quantity, unit_price, total_price) VALUES
(3, 7, 14, 8000, 112000),
(3, 1, 14, 15000, 210000),
(4, 8, 10, 22000, 220000),
(4, 6, 2, 18000, 36000),
(10, 7, 7, 8000, 56000),
(13, 4, 3, 35000, 105000),
(16, 3, 5, 25000, 125000);

-- === MEDICAL RECORD SERVICES ===
INSERT INTO medical_record_services (medical_record_id, service_type_id, quantity, unit_price, total_price) VALUES
(1, 6, 1, 150000, 150000),
(2, 7, 1, 250000, 250000),
(3, 8, 1, 80000, 80000),
(5, 6, 1, 150000, 150000),
(5, 8, 1, 80000, 80000),
(9, 6, 1, 150000, 150000),
(11, 6, 1, 150000, 150000),
(12, 7, 1, 250000, 250000),
(21, 6, 1, 150000, 150000),
(22, 7, 1, 250000, 250000),
(23, 6, 1, 150000, 150000),
(24, 8, 1, 80000, 80000);

-- === PET ENCLOSURES ===
INSERT INTO pet_enclosures (customer_id, pet_id, pet_enclosure_number, check_in_date, check_out_date, daily_rate, deposit, emergency_limit, pet_enclosure_note, pet_enclosure_status) VALUES
(1, 1, 101, '2026-01-18 09:00:00', '2026-01-21 10:00:00', 80000, 100000, 500000, 'Gửi 3 ngày, thú cưng ngoan, ăn uống tốt.', 'Check Out'),
(2, 3, 102, '2026-01-20 08:30:00', '2026-01-25 09:00:00', 100000, 150000, 1000000, 'Mèo VIP, chuồng có điều hòa, camera.', 'Check Out'),
(3, 4, 103, '2026-01-26 10:00:00', NULL, 85000, 120000, 800000, 'Cún lần đầu gửi, cần quan sát kỹ.', 'Check In'),
(4, 5, 104, '2026-01-22 14:00:00', '2026-01-26 09:00:00', 90000, 100000, 600000, 'Thú cưng sợ tiếng ồn, đặt phòng yên tĩnh.', 'Check Out'),
(5, 6, 105, '2026-01-28 09:00:00', NULL, 95000, 130000, 700000, 'Mèo đang theo dõi sức khỏe.', 'Check In'),
(6, 8, 106, '2026-01-15 08:00:00', '2026-01-18 10:00:00', 80000, 100000, 500000, 'Gửi 3 ngày.', 'Check Out'),
(7, 9, 107, '2026-01-16 09:00:00', '2026-01-20 11:00:00', 120000, 200000, 1000000, 'Chó lớn, cần phòng rộng.', 'Check Out'),
(8, 10, 108, '2026-01-17 08:30:00', '2026-01-20 09:00:00', 85000, 100000, 600000, 'Có camera theo dõi 24/7.', 'Check Out'),
(9, 11, 109, '2026-01-19 09:00:00', '2026-01-22 09:00:00', 110000, 150000, 800000, 'Chó Golden, cần nhiều không gian.', 'Check Out'),
(10, 12, 110, '2026-01-20 10:00:00', '2026-01-23 10:00:00', 90000, 120000, 600000, 'Mèo lông dài, chải lông mỗi ngày.', 'Check Out'),
(11, 13, 111, '2026-01-22 09:00:00', NULL, 85000, 100000, 500000, 'Đang điều trị ve, cần theo dõi.', 'Check In'),
(12, 14, 112, '2026-01-22 08:00:00', '2026-01-25 09:00:00', 80000, 100000, 400000, 'Mèo nhỏ, rất ngoan.', 'Check Out'),
(13, 15, 113, '2026-01-24 10:00:00', '2026-01-28 09:00:00', 85000, 110000, 500000, 'Mèo mới, cần quan sát.', 'Check Out'),
(14, 16, 114, '2026-01-26 09:00:00', '2026-01-29 09:00:00', 115000, 180000, 900000, 'Chó Becgie, cần phòng riêng.', 'Check Out'),
(15, 17, 115, '2026-01-27 09:30:00', NULL, 110000, 160000, 800000, 'Đang gửi dài hạn.', 'Check In'),
(16, 18, 116, '2026-01-17 08:00:00', '2026-01-20 09:00:00', 100000, 120000, 600000, 'Mèo không lông, cần giữ ấm.', 'Check Out'),
(17, 19, 117, '2026-01-19 08:30:00', '2026-01-22 09:00:00', 75000, 80000, 400000, 'Chó nhỏ, hay sủa ban đêm.', 'Check Out'),
(18, 20, 118, '2026-01-21 08:00:00', '2026-01-24 09:00:00', 75000, 80000, 400000, 'Chó nhút nhát, cần nhẹ nhàng.', 'Check Out'),
(19, 4, 119, '2026-01-28 10:00:00', NULL, 85000, 120000, 700000, 'Gửi trong khi chủ đi du lịch.', 'Check In'),
(20, 6, 120, '2026-01-27 09:00:00', NULL, 95000, 130000, 700000, 'Mèo VIP, có yêu cầu đặc biệt.', 'Check In'),
(1, 2, 121, '2026-01-30 08:00:00', '2026-01-31 10:00:00', 80000, 100000, 500000, 'Gửi 1 đêm, Pudding khám vaccine.', 'Check Out'),
(2, 3, 122, '2026-01-31 09:00:00', NULL, 100000, 150000, 800000, 'Mimi gửi từ 31/1, đang Check In.', 'Check In');

-- === INVOICES ===
INSERT INTO invoices (customer_id, pet_id, pet_enclosure_id, medical_record_id, invoice_date, discount, subtotal, deposit, total_amount) VALUES
(1, 1, 1, NULL, '2026-01-21 11:00:00', 0, 340000, 100000, 240000),
(2, 3, 2, NULL, '2026-01-25 10:30:00', 50000, 650000, 150000, 450000),
(4, 5, 4, NULL, '2026-01-26 09:30:00', 0, 460000, 100000, 360000),
(6, 8, 6, NULL, '2026-01-18 11:00:00', 0, 340000, 100000, 240000),
(7, 9, 7, NULL, '2026-01-20 11:30:00', 100000, 680000, 200000, 380000),
(8, 10, 8, NULL, '2026-01-20 10:00:00', 0, 355000, 100000, 255000),
(9, 11, 9, NULL, '2026-01-22 09:30:00', 0, 530000, 150000, 380000),
(10, 12, 10, NULL, '2026-01-23 09:45:00', 0, 370000, 120000, 250000),
(12, 14, 12, NULL, '2026-01-25 09:15:00', 0, 340000, 100000, 240000),
(13, 15, 13, NULL, '2026-01-28 10:30:00', 30000, 440000, 110000, 300000),
(14, 16, 14, NULL, '2026-01-29 09:40:00', 0, 545000, 180000, 365000),
(16, 18, 16, NULL, '2026-01-20 09:00:00', 0, 400000, 120000, 280000),
(17, 19, 17, NULL, '2026-01-22 09:00:00', 0, 325000, 80000, 245000),
(18, 20, 18, NULL, '2026-01-24 09:00:00', 0, 325000, 80000, 245000),
(1, 2, 21, NULL, '2026-01-31 10:30:00', 0, 330000, 100000, 230000);

-- === INVOICE DETAILS ===
INSERT INTO invoice_details (invoice_id, service_type_id, quantity, unit_price, total_price) VALUES
(1, 1, 3, 80000, 240000),
(1, 4, 1, 100000, 100000),
(2, 1, 5, 100000, 500000),
(2, 4, 1, 150000, 150000),
(3, 1, 4, 90000, 360000),
(3, 8, 1, 100000, 100000),
(4, 1, 3, 80000, 240000),
(4, 12, 1, 100000, 100000),
(5, 1, 4, 120000, 480000),
(5, 4, 1, 200000, 200000),
(6, 1, 3, 85000, 255000),
(6, 8, 1, 100000, 100000),
(7, 1, 3, 110000, 330000),
(7, 4, 1, 200000, 200000),
(8, 1, 3, 90000, 270000),
(8, 14, 1, 100000, 100000),
(9, 1, 3, 80000, 240000),
(9, 13, 1, 100000, 100000),
(10, 1, 4, 85000, 340000),
(10, 8, 1, 100000, 100000),
(11, 1, 3, 115000, 345000),
(11, 4, 1, 200000, 200000),
(12, 1, 3, 100000, 300000),
(12, 3, 1, 100000, 100000),
(13, 1, 3, 75000, 225000),
(13, 13, 1, 100000, 100000),
(14, 1, 3, 75000, 225000),
(14, 8, 1, 100000, 100000),
(15, 1, 2, 85000, 170000),
(15, 4, 1, 160000, 160000);

-- === PET VACCINATIONS ===
INSERT INTO pet_vaccinations (vaccine_id, medical_record_id, customer_id, pet_id, doctor_id, vaccination_date, next_vaccination_date, notes) VALUES
(1, 1, 1, 1, 1, '2026-01-20', '2027-01-20', 'Tiêm phòng dại định kỳ hàng năm.'),
(2, 2, 1, 2, 2, '2026-01-22', '2027-01-22', 'Tiêm 7 bệnh lần đầu.'),
(5, 6, 2, 3, 1, '2026-01-15', NULL, 'Tiêm FVRCP cho mèo, theo dõi phản ứng.'),
(4, 4, 3, 4, 3, '2026-01-25', '2026-02-25', 'Tiêm Parvo mũi tăng cường.');

-- === TREATMENT COURSES ===
INSERT INTO treatment_courses (medical_record_id, customer_id, pet_id, start_date, end_date, status) VALUES
(3, 2, 3, '2026-01-18', NULL, '1'),
(4, 4, 5, '2026-01-16', '2026-01-23', '0'),
(NULL, 5, 7, '2026-01-25', NULL, '1');

-- === TREATMENT SESSIONS ===
INSERT INTO treatment_sessions (treatment_course_id, doctor_id, treatment_session_datetime, temperature, weight, pulse_rate, respiratory_rate, overall_notes) VALUES
(1, 3, '2026-01-19 09:00:00', 38.8, 4.2, 95, 28, 'Mèo sốt nhẹ do viêm da, bắt đầu điều trị.'),
(1, 3, '2026-01-22 09:30:00', 38.2, 4.3, 88, 24, 'Đã giảm sốt, da đang lành.'),
(2, 5, '2026-01-17 10:00:00', 39.2, 8.8, 100, 32, 'Viêm tai nặng, cần điều trị tích cực.'),
(2, 5, '2026-01-21 10:00:00', 38.5, 8.9, 92, 26, 'Cải thiện rõ rệt, tiếp tục thuốc.'),
(3, 4, '2026-01-26 08:45:00', 37.5, 7.8, 85, 22, 'Khám định kỳ, béo phì nhẹ.');

-- === DIAGNOSES ===
INSERT INTO diagnoses (treatment_session_id, diagnosis_name, diagnosis_type, clinical_tests, notes) VALUES
(1, 'Viêm da dị ứng', '1', 'Xét nghiệm da, kiểm tra dị ứng', 'Điều trị bằng thuốc kháng viêm.'),
(1, 'Sốt nhẹ do nhiễm khuẩn thứ phát', '0', 'Xét nghiệm máu: tăng bạch cầu', 'Kết hợp kháng sinh.'),
(2, 'Phục hồi sau viêm da', '1', NULL, 'Tiếp tục theo dõi 1 tuần.'),
(3, 'Viêm tai giữa', '1', 'Soi tai, xét nghiệm dịch tai', 'Điều trị kháng sinh + thuốc nhỏ tai.'),
(4, 'Viêm tai đang hồi phục', '1', NULL, 'Tiếp tục thuốc 3 ngày nữa.'),
(5, 'Béo phì nhẹ', '1', 'Đo cân nặng, kiểm tra dinh dưỡng', 'Điều chỉnh chế độ ăn, tăng vận động.');

-- === PRESCRIPTIONS ===
INSERT INTO prescriptions (treatment_session_id, medicine_id, treatment_type, dosage, unit, frequency, status, notes) VALUES
(1, 7, 'uống', 5.00, 'mg', '2 lần/ngày', '1', 'Prednisolone chống viêm'),
(1, 1, 'uống', 125.00, 'mg', '2 lần/ngày', '1', 'Amoxicillin kháng sinh'),
(2, 7, 'uống', 2.50, 'mg', '1 lần/ngày', '0', 'Giảm liều Prednisolone'),
(3, 8, 'uống', 50.00, 'mg', '2 lần/ngày', '1', 'Enrofloxacin cho tai'),
(3, 6, 'tiêm', 4.00, 'mg', '1 lần', '0', 'Dexamethasone giảm viêm'),
(4, 8, 'uống', 50.00, 'mg', '1 lần/ngày', '0', 'Tiếp tục kháng sinh'),
(5, 3, 'uống', 500.00, 'mg', '1 lần/ngày', '1', 'Vitamin C tăng đề kháng');

-- =====================================================
-- HOÀN TẤT
-- =====================================================
