from fastapi import Request
from starlette.responses import RedirectResponse

CUSTOMER_HOME_PATH = "/customer/dashboard"


def redirect_if_customer_session(request: Request) -> RedirectResponse | None:
    """Khách đã đăng nhập khu vực customer — không cho vào /admin."""
    if request.session.get("role") == "customer":
        return RedirectResponse(url=CUSTOMER_HOME_PATH, status_code=302)
    return None


_FLASH_TEXT_MAP = {
    "Dang nhap thanh cong": "Đăng nhập thành công",
    "Dang xuat thanh cong": "Đăng xuất thành công",
    "Dang ky thanh cong": "Đăng ký thành công",
    "Sai ten dang nhap hoac mat khau": "Sai tên đăng nhập hoặc mật khẩu",
    "Vui long dang nhap": "Vui lòng đăng nhập",
    "Vui long dang nhap de dat lich": "Vui lòng đăng nhập để đặt lịch",
    "Vui long nhap day du thong tin": "Vui lòng nhập đầy đủ thông tin",
    "Vui long nhap day du thong tin bat buoc": "Vui lòng nhập đầy đủ thông tin bắt buộc",
    "Vui long nhap so dien thoai": "Vui lòng nhập số điện thoại",
    "Ma OTP khong dung. Ma mac dinh: 123456": "Mã OTP không đúng. Mã mặc định: 123456",
    "So dien thoai chua duoc dang ky": "Số điện thoại chưa được đăng ký",
    "So dien thoai da duoc dang ky": "Số điện thoại đã được đăng ký",
    "So dien thoai da duoc su dung": "Số điện thoại đã được sử dụng",
    "Cap nhat thong tin thanh cong": "Cập nhật thông tin thành công",
    "Cap nhat trang thai thanh cong": "Cập nhật trạng thái thành công",
    "Cap nhat lich hen thanh cong": "Cập nhật lịch hẹn thành công",
    "Cap nhat cai dat thanh cong": "Cập nhật cài đặt thành công",
    "Doi mat khau thanh cong": "Đổi mật khẩu thành công",
    "Mat khau cu khong dung": "Mật khẩu cũ không đúng",
    "Mat khau moi va xac nhan khong khop": "Mật khẩu mới và xác nhận không khớp",
    "Ban khong the xoa chinh minh": "Bạn không thể xóa chính mình",
    "Khong tim thay khach hang": "Không tìm thấy khách hàng",
    "Khong tim thay hoa don hoac ban khong co quyen xem": "Không tìm thấy hóa đơn hoặc bạn không có quyền xem",
    "Khong tim thay phieu kham": "Không tìm thấy phiếu khám",
    "Khong tim thay du lieu dieu tri": "Không tìm thấy dữ liệu điều trị",
    "Khong tim thay luu chuong": "Không tìm thấy lưu chuồng",
    "Ten thu cung la bat buoc": "Tên thú cưng là bắt buộc",
    "Them thu cung thanh cong": "Thêm thú cưng thành công",
    "Vui long dien day du thong tin bat buoc": "Vui lòng điền đầy đủ thông tin bắt buộc",
    "Them khach hang thanh cong": "Thêm khách hàng thành công",
    "Cap nhat khach hang thanh cong": "Cập nhật khách hàng thành công",
    "Xoa khach hang thanh cong": "Xóa khách hàng thành công",
    "Them bac si thanh cong": "Thêm bác sĩ thành công",
    "Cap nhat bac si thanh cong": "Cập nhật bác sĩ thành công",
    "Xoa bac si thanh cong": "Xóa bác sĩ thành công",
    "Them dich vu thanh cong": "Thêm dịch vụ thành công",
    "Cap nhat dich vu thanh cong": "Cập nhật dịch vụ thành công",
    "Xoa dich vu thanh cong": "Xóa dịch vụ thành công",
    "Cap nhat thu cung thanh cong": "Cập nhật thú cưng thành công",
    "Xoa thu cung thanh cong": "Xóa thú cưng thành công",
    "Xoa lich hen thanh cong": "Xóa lịch hẹn thành công",
    "Them thuoc thanh cong": "Thêm thuốc thành công",
    "Cap nhat thuoc thanh cong": "Cập nhật thuốc thành công",
    "Xoa thuoc thanh cong": "Xóa thuốc thành công",
    "Them vaccine thanh cong": "Thêm vaccine thành công",
    "Cap nhat vaccine thanh cong": "Cập nhật vaccine thành công",
    "Xoa vaccine thanh cong": "Xóa vaccine thành công",
    "Them nguoi dung thanh cong": "Thêm người dùng thành công",
    "Cap nhat nguoi dung thanh cong": "Cập nhật người dùng thành công",
    "Xoa nguoi dung thanh cong": "Xóa người dùng thành công",
    "Them phieu kham thanh cong": "Thêm phiếu khám thành công",
    "Cap nhat phieu kham thanh cong": "Cập nhật phiếu khám thành công",
    "Xoa phieu kham thanh cong": "Xóa phiếu khám thành công",
    "Them hoa don thanh cong": "Thêm hóa đơn thành công",
    "Cap nhat hoa don thanh cong": "Cập nhật hóa đơn thành công",
    "Xoa hoa don thanh cong": "Xóa hóa đơn thành công",
    "Them luu chuong thanh cong": "Thêm lưu chuồng thành công",
    "Cap nhat luu chuong thanh cong": "Cập nhật lưu chuồng thành công",
    "Checkout thanh cong, da tao hoa don": "Checkout thành công, đã tạo hóa đơn",
    "Xoa luu chuong thanh cong": "Xóa lưu chuồng thành công",
    "Them tiem chung thanh cong": "Thêm tiêm chủng thành công",
    "Cap nhat tiem chung thanh cong": "Cập nhật tiêm chủng thành công",
    "Xoa tiem chung thanh cong": "Xóa tiêm chủng thành công",
    "Them lieu trinh thanh cong": "Thêm liệu trình thành công",
    "Cap nhat lieu trinh thanh cong": "Cập nhật liệu trình thành công",
    "Ket thuc lieu trinh thanh cong": "Kết thúc liệu trình thành công",
    "Xoa lieu trinh thanh cong": "Xóa liệu trình thành công",
    "Them buoi dieu tri thanh cong": "Thêm buổi điều trị thành công",
    "Cap nhat buoi dieu tri thanh cong": "Cập nhật buổi điều trị thành công",
    "Xoa buoi dieu tri thanh cong": "Xóa buổi điều trị thành công",
    "Luu chan doan thanh cong": "Lưu chẩn đoán thành công",
    "Them thuoc vao don thanh cong": "Thêm thuốc vào đơn thành công",
    "Xoa thuoc khoi don thanh cong": "Xóa thuốc khỏi đơn thành công",
    "Thu cung khong hop le": "Thú cưng không hợp lệ",
    "Dat lich thanh cong": "Đặt lịch thành công",
    "Tai khoan khach hang - chuyen den khu vuc khach": "Tài khoản khách hàng — đang chuyển đến khu vực khách hàng",
}


def _normalize_flash_text(text: str | None) -> str | None:
    if not text:
        return text
    return _FLASH_TEXT_MAP.get(text, text)


def pop_flash(request: Request) -> dict[str, str | None]:
    flash = request.session.pop("flash", None)
    if not flash:
        return {"success": None, "error": None}
    return {
        "success": flash.get("success"),
        "error": flash.get("error"),
    }


def set_flash(request: Request, success: str | None = None, error: str | None = None) -> None:
    request.session["flash"] = {
        "success": _normalize_flash_text(success),
        "error": _normalize_flash_text(error),
    }


def current_user(request: Request) -> dict[str, str | int] | None:
    if "username" not in request.session:
        return None
    return {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "fullname": request.session.get("fullname"),
        "role": request.session.get("role"),
        "customer_id": request.session.get("customer_id"),
    }
