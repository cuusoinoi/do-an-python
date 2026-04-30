from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import Jinja2Templates
from datetime import datetime

from app.db import execute, fetch_one
from app.security import md5_hash
from app.session import pop_flash, set_flash

router = APIRouter(prefix="/customer", tags=["customer-auth"])
templates = Jinja2Templates(directory="templates")
DEFAULT_OTP = "123456"


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "customer/auth/login.html",
        {"request": request, "title": "Dang nhap - UIT Petcare", "flash": pop_flash(request)},
    )


@router.post("/login")
def login(request: Request, phone: str = Form(""), otp: str = Form("")):
    if not phone:
        set_flash(request, error="Vui long nhap so dien thoai")
        return RedirectResponse(url="/customer/login", status_code=302)
    if otp != DEFAULT_OTP:
        set_flash(request, error="Ma OTP khong dung. Ma mac dinh: 123456")
        return RedirectResponse(url="/customer/login", status_code=302)

    customer = fetch_one(
        "SELECT * FROM customers WHERE customer_phone_number = :phone LIMIT 1", {"phone": phone}
    )
    if not customer:
        set_flash(request, error="So dien thoai chua duoc dang ky")
        return RedirectResponse(url="/customer/login", status_code=302)

    user = fetch_one("SELECT * FROM users WHERE username = :username LIMIT 1", {"username": phone})
    if not user:
        now = datetime.now()
        try:
            execute(
                """
                INSERT INTO users (username, password, fullname, role, created_at)
                VALUES (:username, :password, :fullname, 'customer', :created_at)
                """,
                {"username": phone, "password": md5_hash(DEFAULT_OTP), "fullname": customer["customer_name"], "created_at": now},
            )
        except Exception:
            execute(
                """
                INSERT INTO users (username, password, fullname, role, create_at)
                VALUES (:username, :password, :fullname, 'customer', :create_at)
                """,
                {"username": phone, "password": md5_hash(DEFAULT_OTP), "fullname": customer["customer_name"], "create_at": now},
            )
        user = fetch_one("SELECT * FROM users WHERE username = :username LIMIT 1", {"username": phone})
    elif user["role"] != "customer":
        execute("UPDATE users SET role='customer' WHERE id=:id", {"id": user["id"]})
        user = fetch_one("SELECT * FROM users WHERE id=:id", {"id": user["id"]})

    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["fullname"] = user["fullname"]
    request.session["role"] = "customer"
    request.session["customer_id"] = customer["customer_id"]
    set_flash(request, success="Dang nhap thanh cong")
    return RedirectResponse(url="/customer/dashboard", status_code=302)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "customer/auth/register.html",
        {"request": request, "title": "Dang ky - UIT Petcare", "flash": pop_flash(request)},
    )


@router.post("/register")
def register(
    request: Request,
    name: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    otp: str = Form(""),
):
    if not name or not phone:
        set_flash(request, error="Vui long dien day du thong tin bat buoc")
        return RedirectResponse(url="/customer/register", status_code=302)
    if otp != DEFAULT_OTP:
        set_flash(request, error="Ma OTP khong dung. Ma mac dinh: 123456")
        return RedirectResponse(url="/customer/register", status_code=302)
    existing_customer = fetch_one(
        "SELECT customer_id FROM customers WHERE customer_phone_number = :phone LIMIT 1", {"phone": phone}
    )
    if existing_customer:
        set_flash(request, error="So dien thoai da duoc dang ky")
        return RedirectResponse(url="/customer/register", status_code=302)
    existing_user = fetch_one("SELECT id FROM users WHERE username=:username LIMIT 1", {"username": phone})
    if existing_user:
        set_flash(request, error="So dien thoai da duoc su dung")
        return RedirectResponse(url="/customer/register", status_code=302)

    execute(
        """
        INSERT INTO customers (customer_name, customer_phone_number, customer_email, customer_address)
        VALUES (:name, :phone, :email, :address)
        """,
        {"name": name, "phone": phone, "email": email or None, "address": address or None},
    )
    customer = fetch_one(
        "SELECT * FROM customers WHERE customer_phone_number=:phone ORDER BY customer_id DESC LIMIT 1",
        {"phone": phone},
    )
    now = datetime.now()
    try:
        execute(
            """
            INSERT INTO users (username, password, fullname, role, created_at)
            VALUES (:username, :password, :fullname, 'customer', :created_at)
            """,
            {"username": phone, "password": md5_hash(DEFAULT_OTP), "fullname": name, "created_at": now},
        )
    except Exception:
        execute(
            """
            INSERT INTO users (username, password, fullname, role, create_at)
            VALUES (:username, :password, :fullname, 'customer', :create_at)
            """,
            {"username": phone, "password": md5_hash(DEFAULT_OTP), "fullname": name, "create_at": now},
        )
    user = fetch_one("SELECT * FROM users WHERE username = :username LIMIT 1", {"username": phone})

    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["fullname"] = user["fullname"]
    request.session["role"] = "customer"
    request.session["customer_id"] = customer["customer_id"]
    set_flash(request, success="Dang ky thanh cong")
    return RedirectResponse(url="/customer/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    set_flash(request, success="Dang xuat thanh cong")
    return RedirectResponse(url="/customer/login", status_code=302)
