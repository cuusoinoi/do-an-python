from math import ceil
from datetime import datetime, date

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import Jinja2Templates

from app.db import execute, fetch_all, fetch_one
from app.record_detail_queries import (
    load_invoice_medicines,
    load_invoice_vaccinations,
    load_record_medicines,
    load_record_services,
    save_record_medicines,
    save_record_services,
)
from app.security import hash_password, verify_password
from app.session import pop_flash, set_flash
from app.user_time_compat import insert_user_with_time_compat

router = APIRouter(prefix="/admin", tags=["admin-core"])
templates = Jinja2Templates(directory="templates")


def _guard_staff(request: Request):
    if request.session.get("role") not in {"admin", "staff"}:
        set_flash(request, error="Vui long dang nhap")
        return RedirectResponse(url="/admin", status_code=302)
    return None


def _guard_admin(request: Request):
    if request.session.get("role") != "admin":
        set_flash(request, error="Ban khong co quyen truy cap")
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return None


def _pager(total: int, page: int, limit: int):
    total_pages = max(1, ceil(total / limit)) if total else 1
    page = max(1, min(page, total_pages))
    return page, (page - 1) * limit, total_pages


def _normalize_medical_record_type(value: str) -> str:
    text = (value or "").strip()
    mapping = {
        "Khám bệnh": "Khám",
        "Tái khám": "Điều trị",
        "Khác": "Điều trị",
    }
    normalized = mapping.get(text, text)
    if normalized not in {"Khám", "Điều trị", "Vaccine"}:
        return "Khám"
    return normalized


@router.get("/customers", response_class=HTMLResponse)
def customers_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE customer_name LIKE :q OR customer_phone_number LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM customers {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    customers = fetch_all(
        f"""
        SELECT * FROM customers
        {where}
        ORDER BY customer_id DESC
        LIMIT :limit OFFSET :offset
        """,
        params,
    )
    return templates.TemplateResponse(
        "admin/customer/customers.html",
        {
            "request": request,
            "title": "Danh sach khach hang - UIT Petcare",
            "flash": pop_flash(request),
            "rows": customers,
            "page": page,
            "total_pages": total_pages,
            "q": q,
        },
    )


@router.get("/customers/add", response_class=HTMLResponse)
def customer_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse(
        "admin/customer/add_customer.html",
        {"request": request, "title": "Them khach hang", "flash": pop_flash(request), "row": None, "action": "add"},
    )


@router.post("/customers/store")
def customer_store(
    request: Request,
    fullname: str = Form(""),
    phone: str = Form(""),
    identity_card: str = Form(""),
    address: str = Form(""),
    note: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    if not fullname or not phone or not address:
        set_flash(request, error="Vui long dien day du thong tin bat buoc")
        return RedirectResponse(url="/admin/customers/add", status_code=302)
    execute(
        """
        INSERT INTO customers (customer_name, customer_phone_number, customer_identity_card, customer_address, customer_note)
        VALUES (:name, :phone, :card, :address, :note)
        """,
        {"name": fullname, "phone": phone, "card": identity_card or None, "address": address, "note": note or None},
    )
    set_flash(request, success="Them khach hang thanh cong")
    return RedirectResponse(url="/admin/customers", status_code=302)


@router.get("/customers/edit/{customer_id}", response_class=HTMLResponse)
def customer_edit_page(request: Request, customer_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": customer_id})
    if not row:
        set_flash(request, error="Khong tim thay khach hang")
        return RedirectResponse(url="/admin/customers", status_code=302)
    return templates.TemplateResponse(
        "admin/customer/edit_customer.html",
        {"request": request, "title": "Chinh sua khach hang", "flash": pop_flash(request), "row": row, "action": "edit"},
    )


@router.post("/customers/update/{customer_id}")
def customer_update(
    request: Request,
    customer_id: int,
    fullname: str = Form(""),
    phone: str = Form(""),
    identity_card: str = Form(""),
    address: str = Form(""),
    note: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE customers
        SET customer_name=:name, customer_phone_number=:phone, customer_identity_card=:card, customer_address=:address, customer_note=:note
        WHERE customer_id=:id
        """,
        {"name": fullname, "phone": phone, "card": identity_card or None, "address": address, "note": note or None, "id": customer_id},
    )
    set_flash(request, success="Cap nhat khach hang thanh cong")
    return RedirectResponse(url="/admin/customers", status_code=302)


@router.get("/customers/delete/{customer_id}")
def customer_delete(request: Request, customer_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM customers WHERE customer_id=:id", {"id": customer_id})
    set_flash(request, success="Xoa khach hang thanh cong")
    return RedirectResponse(url="/admin/customers", status_code=302)


@router.get("/doctors", response_class=HTMLResponse)
def doctors_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE doctor_name LIKE :q OR doctor_phone_number LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM doctors {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(f"SELECT * FROM doctors {where} ORDER BY doctor_id DESC LIMIT :limit OFFSET :offset", params)
    return templates.TemplateResponse(
        "admin/doctor/doctors.html",
        {"request": request, "title": "Danh sach bac si", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q},
    )


@router.get("/doctors/add", response_class=HTMLResponse)
def doctor_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/doctor/add_doctor.html", {"request": request, "title": "Them bac si", "flash": pop_flash(request), "row": None, "action": "add"})


@router.post("/doctors/store")
def doctor_store(request: Request, fullname: str = Form(""), phone: str = Form(""), identity_card: str = Form(""), address: str = Form(""), note: str = Form("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO doctors (doctor_name, doctor_phone_number, doctor_identity_card, doctor_address, doctor_note)
        VALUES (:name, :phone, :card, :address, :note)
        """,
        {"name": fullname, "phone": phone, "card": identity_card or None, "address": address, "note": note or None},
    )
    set_flash(request, success="Them bac si thanh cong")
    return RedirectResponse(url="/admin/doctors", status_code=302)


@router.get("/doctors/edit/{doctor_id}", response_class=HTMLResponse)
def doctor_edit_page(request: Request, doctor_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM doctors WHERE doctor_id=:id", {"id": doctor_id})
    return templates.TemplateResponse("admin/doctor/edit_doctor.html", {"request": request, "title": "Chinh sua bac si", "flash": pop_flash(request), "row": row, "action": "edit"})


@router.post("/doctors/update/{doctor_id}")
def doctor_update(request: Request, doctor_id: int, fullname: str = Form(""), phone: str = Form(""), identity_card: str = Form(""), address: str = Form(""), note: str = Form("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE doctors SET doctor_name=:name, doctor_phone_number=:phone, doctor_identity_card=:card, doctor_address=:address, doctor_note=:note
        WHERE doctor_id=:id
        """,
        {"name": fullname, "phone": phone, "card": identity_card or None, "address": address, "note": note or None, "id": doctor_id},
    )
    set_flash(request, success="Cap nhat bac si thanh cong")
    return RedirectResponse(url="/admin/doctors", status_code=302)


@router.get("/doctors/delete/{doctor_id}")
def doctor_delete(request: Request, doctor_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM doctors WHERE doctor_id=:id", {"id": doctor_id})
    set_flash(request, success="Xoa bac si thanh cong")
    return RedirectResponse(url="/admin/doctors", status_code=302)


@router.get("/service-types", response_class=HTMLResponse)
def service_types_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE service_name LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM service_types {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(f"SELECT * FROM service_types {where} ORDER BY service_type_id DESC LIMIT :limit OFFSET :offset", params)
    return templates.TemplateResponse(
        "admin/service_type/service_types.html",
        {"request": request, "title": "Danh sach dich vu", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q},
    )


@router.get("/service-types/add", response_class=HTMLResponse)
def service_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/service_type/add_service_type.html", {"request": request, "title": "Them dich vu", "flash": pop_flash(request), "row": None, "action": "add"})


@router.post("/service-types/store")
def service_store(request: Request, name: str = Form(""), description: str = Form(""), price: float = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("INSERT INTO service_types (service_name, description, price) VALUES (:name, :description, :price)", {"name": name, "description": description or None, "price": price or 0})
    set_flash(request, success="Them dich vu thanh cong")
    return RedirectResponse(url="/admin/service-types", status_code=302)


@router.get("/service-types/edit/{service_id}", response_class=HTMLResponse)
def service_edit_page(request: Request, service_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM service_types WHERE service_type_id=:id", {"id": service_id})
    return templates.TemplateResponse("admin/service_type/edit_service_type.html", {"request": request, "title": "Chinh sua dich vu", "flash": pop_flash(request), "row": row, "action": "edit"})


@router.post("/service-types/update/{service_id}")
def service_update(request: Request, service_id: int, name: str = Form(""), description: str = Form(""), price: float = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        "UPDATE service_types SET service_name=:name, description=:description, price=:price WHERE service_type_id=:id",
        {"name": name, "description": description or None, "price": price or 0, "id": service_id},
    )
    set_flash(request, success="Cap nhat dich vu thanh cong")
    return RedirectResponse(url="/admin/service-types", status_code=302)


@router.get("/service-types/delete/{service_id}")
def service_delete(request: Request, service_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM service_types WHERE service_type_id=:id", {"id": service_id})
    set_flash(request, success="Xoa dich vu thanh cong")
    return RedirectResponse(url="/admin/service-types", status_code=302)


@router.get("/pets", response_class=HTMLResponse)
def pets_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE p.pet_name LIKE :q OR c.customer_name LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM pets p LEFT JOIN customers c ON c.customer_id=p.customer_id {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(
        f"""
        SELECT p.*, c.customer_name
        FROM pets p
        LEFT JOIN customers c ON c.customer_id = p.customer_id
        {where}
        ORDER BY p.pet_id DESC
        LIMIT :limit OFFSET :offset
        """,
        params,
    )
    return templates.TemplateResponse("admin/pet/pets.html", {"request": request, "title": "Danh sach thu cung", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q})


@router.get("/pets/add", response_class=HTMLResponse)
def pet_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    customers = fetch_all("SELECT customer_id, customer_name FROM customers ORDER BY customer_name ASC")
    return templates.TemplateResponse("admin/pet/add_pet.html", {"request": request, "title": "Them thu cung", "flash": pop_flash(request), "row": None, "customers": customers, "action": "add"})


@router.post("/pets/store")
def pet_store(
    request: Request,
    customer_id: int = Form(...),
    name: str = Form(""),
    species: str = Form(""),
    gender: str = Form(""),
    dob: str = Form(""),
    weight: str = Form(""),
    sterilization: str = Form(""),
    characteristic: str = Form(""),
    allergy: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO pets (customer_id, pet_name, pet_species, pet_gender, pet_dob, pet_weight, pet_sterilization, pet_characteristic, pet_drug_allergy)
        VALUES (:customer_id, :name, :species, :gender, :dob, :weight, :sterilization, :characteristic, :allergy)
        """,
        {
            "customer_id": customer_id,
            "name": name,
            "species": species or None,
            "gender": gender or None,
            "dob": dob or None,
            "weight": weight or None,
            "sterilization": sterilization or None,
            "characteristic": characteristic or None,
            "allergy": allergy or None,
        },
    )
    set_flash(request, success="Them thu cung thanh cong")
    return RedirectResponse(url="/admin/pets", status_code=302)


@router.get("/pets/edit/{pet_id}", response_class=HTMLResponse)
def pet_edit_page(request: Request, pet_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": pet_id})
    customers = fetch_all("SELECT customer_id, customer_name FROM customers ORDER BY customer_name ASC")
    return templates.TemplateResponse("admin/pet/edit_pet.html", {"request": request, "title": "Chinh sua thu cung", "flash": pop_flash(request), "row": row, "customers": customers, "action": "edit"})


@router.post("/pets/update/{pet_id}")
def pet_update(
    request: Request,
    pet_id: int,
    customer_id: int = Form(...),
    name: str = Form(""),
    species: str = Form(""),
    gender: str = Form(""),
    dob: str = Form(""),
    weight: str = Form(""),
    sterilization: str = Form(""),
    characteristic: str = Form(""),
    allergy: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE pets
        SET customer_id=:customer_id, pet_name=:name, pet_species=:species, pet_gender=:gender, pet_dob=:dob,
            pet_weight=:weight, pet_sterilization=:sterilization, pet_characteristic=:characteristic, pet_drug_allergy=:allergy
        WHERE pet_id=:id
        """,
        {
            "customer_id": customer_id,
            "name": name,
            "species": species or None,
            "gender": gender or None,
            "dob": dob or None,
            "weight": weight or None,
            "sterilization": sterilization or None,
            "characteristic": characteristic or None,
            "allergy": allergy or None,
            "id": pet_id,
        },
    )
    set_flash(request, success="Cap nhat thu cung thanh cong")
    return RedirectResponse(url="/admin/pets", status_code=302)


@router.get("/pets/delete/{pet_id}")
def pet_delete(request: Request, pet_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM pets WHERE pet_id=:id", {"id": pet_id})
    set_flash(request, success="Xoa thu cung thanh cong")
    return RedirectResponse(url="/admin/pets", status_code=302)


@router.get("/appointments", response_class=HTMLResponse)
def appointments_page(request: Request, page: int = Query(1), status: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if status in {"pending", "confirmed", "completed", "cancelled"}:
        where = "WHERE a.status=:status"
        params["status"] = status
    total = fetch_one(f"SELECT COUNT(*) AS total FROM appointments a {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 20)
    params.update({"limit": 20, "offset": offset})
    rows = fetch_all(
        f"""
        SELECT a.*, c.customer_name, p.pet_name, d.doctor_name, s.service_name
        FROM appointments a
        LEFT JOIN customers c ON c.customer_id = a.customer_id
        LEFT JOIN pets p ON p.pet_id = a.pet_id
        LEFT JOIN doctors d ON d.doctor_id = a.doctor_id
        LEFT JOIN service_types s ON s.service_type_id = a.service_type_id
        {where}
        ORDER BY a.appointment_date DESC
        LIMIT :limit OFFSET :offset
        """,
        params,
    )
    return templates.TemplateResponse(
        "admin/appointment/appointments.html",
        {"request": request, "title": "Quan ly lich hen", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "status": status},
    )


@router.get("/appointments/view/{appointment_id}", response_class=HTMLResponse)
def appointment_view(request: Request, appointment_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one(
        """
        SELECT a.*, c.customer_name, c.customer_phone_number, p.pet_name, d.doctor_name, s.service_name
        FROM appointments a
        LEFT JOIN customers c ON c.customer_id = a.customer_id
        LEFT JOIN pets p ON p.pet_id = a.pet_id
        LEFT JOIN doctors d ON d.doctor_id = a.doctor_id
        LEFT JOIN service_types s ON s.service_type_id = a.service_type_id
        WHERE a.appointment_id=:id
        """,
        {"id": appointment_id},
    )
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    services = fetch_all("SELECT service_type_id, service_name FROM service_types ORDER BY service_name ASC")
    return templates.TemplateResponse("admin/appointment/view.html", {"request": request, "title": "Chi tiet lich hen", "flash": pop_flash(request), "row": row, "doctors": doctors, "services": services})


@router.post("/appointments/update/{appointment_id}")
def appointment_update(
    request: Request,
    appointment_id: int,
    doctor_id: int | None = Form(default=None),
    service_type_id: int | None = Form(default=None),
    appointment_date: str = Form(""),
    appointment_type: str = Form(""),
    status: str = Form("pending"),
    notes: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE appointments
        SET doctor_id=:doctor_id, service_type_id=:service_type_id, appointment_date=:appointment_date, appointment_type=:appointment_type, status=:status, notes=:notes
        WHERE appointment_id=:id
        """,
        {
            "doctor_id": doctor_id,
            "service_type_id": service_type_id,
            "appointment_date": appointment_date,
            "appointment_type": appointment_type,
            "status": status,
            "notes": notes or None,
            "id": appointment_id,
        },
    )
    set_flash(request, success="Cap nhat lich hen thanh cong")
    return RedirectResponse(url="/admin/appointments", status_code=302)


@router.post("/appointments/update-status/{appointment_id}")
def appointment_update_status(request: Request, appointment_id: int, status: str = Form("pending")):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("UPDATE appointments SET status=:status WHERE appointment_id=:id", {"status": status, "id": appointment_id})
    set_flash(request, success="Cap nhat trang thai thanh cong")
    return RedirectResponse(url="/admin/appointments", status_code=302)


@router.get("/appointments/delete/{appointment_id}")
def appointment_delete(request: Request, appointment_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM appointments WHERE appointment_id=:id", {"id": appointment_id})
    set_flash(request, success="Xoa lich hen thanh cong")
    return RedirectResponse(url="/admin/appointments", status_code=302)


@router.get("/medicines", response_class=HTMLResponse)
def medicines_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE medicine_name LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM medicines {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(f"SELECT * FROM medicines {where} ORDER BY medicine_id DESC LIMIT :limit OFFSET :offset", params)
    return templates.TemplateResponse("admin/medicine/medicines.html", {"request": request, "title": "Danh sach thuoc", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q})


@router.get("/medicines/add", response_class=HTMLResponse)
def medicine_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/medicine/add_medicine.html", {"request": request, "title": "Them thuoc", "flash": pop_flash(request), "row": None, "action": "add"})


@router.post("/medicines/store")
def medicine_store(request: Request, name: str = Form(""), route: str = Form("PO"), unit_price: int = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        "INSERT INTO medicines (medicine_name, medicine_route, unit_price) VALUES (:name, :route, :unit_price)",
        {"name": name, "route": route, "unit_price": unit_price or 0},
    )
    set_flash(request, success="Them thuoc thanh cong")
    return RedirectResponse(url="/admin/medicines", status_code=302)


@router.get("/medicines/edit/{medicine_id}", response_class=HTMLResponse)
def medicine_edit_page(request: Request, medicine_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM medicines WHERE medicine_id=:id", {"id": medicine_id})
    return templates.TemplateResponse("admin/medicine/edit_medicine.html", {"request": request, "title": "Chinh sua thuoc", "flash": pop_flash(request), "row": row, "action": "edit"})


@router.post("/medicines/update/{medicine_id}")
def medicine_update(request: Request, medicine_id: int, name: str = Form(""), route: str = Form("PO"), unit_price: int = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        "UPDATE medicines SET medicine_name=:name, medicine_route=:route, unit_price=:unit_price WHERE medicine_id=:id",
        {"name": name, "route": route, "unit_price": unit_price or 0, "id": medicine_id},
    )
    set_flash(request, success="Cap nhat thuoc thanh cong")
    return RedirectResponse(url="/admin/medicines", status_code=302)


@router.get("/medicines/delete/{medicine_id}")
def medicine_delete(request: Request, medicine_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM medicines WHERE medicine_id=:id", {"id": medicine_id})
    set_flash(request, success="Xoa thuoc thanh cong")
    return RedirectResponse(url="/admin/medicines", status_code=302)


@router.get("/vaccines", response_class=HTMLResponse)
def vaccines_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE vaccine_name LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM vaccines {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(f"SELECT * FROM vaccines {where} ORDER BY vaccine_id DESC LIMIT :limit OFFSET :offset", params)
    return templates.TemplateResponse("admin/vaccine/vaccines.html", {"request": request, "title": "Danh sach vaccine", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q})


@router.get("/vaccines/add", response_class=HTMLResponse)
def vaccine_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/vaccine/add_vaccine.html", {"request": request, "title": "Them vaccine", "flash": pop_flash(request), "row": None, "action": "add"})


@router.post("/vaccines/store")
def vaccine_store(request: Request, name: str = Form(""), description: str = Form(""), unit_price: int = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        "INSERT INTO vaccines (vaccine_name, description, unit_price) VALUES (:name, :description, :unit_price)",
        {"name": name, "description": description or None, "unit_price": unit_price or 0},
    )
    set_flash(request, success="Them vaccine thanh cong")
    return RedirectResponse(url="/admin/vaccines", status_code=302)


@router.get("/vaccines/edit/{vaccine_id}", response_class=HTMLResponse)
def vaccine_edit_page(request: Request, vaccine_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM vaccines WHERE vaccine_id=:id", {"id": vaccine_id})
    return templates.TemplateResponse("admin/vaccine/edit_vaccine.html", {"request": request, "title": "Chinh sua vaccine", "flash": pop_flash(request), "row": row, "action": "edit"})


@router.post("/vaccines/update/{vaccine_id}")
def vaccine_update(request: Request, vaccine_id: int, name: str = Form(""), description: str = Form(""), unit_price: int = Form(0)):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        "UPDATE vaccines SET vaccine_name=:name, description=:description, unit_price=:unit_price WHERE vaccine_id=:id",
        {"name": name, "description": description or None, "unit_price": unit_price or 0, "id": vaccine_id},
    )
    set_flash(request, success="Cap nhat vaccine thanh cong")
    return RedirectResponse(url="/admin/vaccines", status_code=302)


@router.get("/vaccines/delete/{vaccine_id}")
def vaccine_delete(request: Request, vaccine_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM vaccines WHERE vaccine_id=:id", {"id": vaccine_id})
    set_flash(request, success="Xoa vaccine thanh cong")
    return RedirectResponse(url="/admin/vaccines", status_code=302)


@router.get("/users", response_class=HTMLResponse)
def users_page(request: Request, page: int = Query(1), q: str = Query("")):
    guard = _guard_admin(request)
    if guard:
        return guard
    where = ""
    params: dict[str, object] = {}
    if q:
        where = "WHERE username LIKE :q OR fullname LIKE :q"
        params["q"] = f"%{q}%"
    total = fetch_one(f"SELECT COUNT(*) AS total FROM users {where}", params)["total"]
    page, offset, total_pages = _pager(total, page, 10)
    params.update({"limit": 10, "offset": offset})
    rows = fetch_all(f"SELECT * FROM users {where} ORDER BY id DESC LIMIT :limit OFFSET :offset", params)
    return templates.TemplateResponse("admin/user/users.html", {"request": request, "title": "Danh sach nguoi dung", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages, "q": q, "current_username": request.session.get("username")})


@router.get("/users/add", response_class=HTMLResponse)
def user_add_page(request: Request):
    guard = _guard_admin(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/user/add_user.html", {"request": request, "title": "Them nguoi dung", "flash": pop_flash(request), "row": None, "action": "add"})


@router.post("/users/store")
def user_store(request: Request, username: str = Form(""), password: str = Form(""), fullname: str = Form(""), role: str = Form("staff")):
    guard = _guard_admin(request)
    if guard:
        return guard
    insert_user_with_time_compat(username=username, password=hash_password(password), fullname=fullname, role=role)
    set_flash(request, success="Them nguoi dung thanh cong")
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/users/edit/{user_id}", response_class=HTMLResponse)
def user_edit_page(request: Request, user_id: int):
    guard = _guard_admin(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM users WHERE id=:id", {"id": user_id})
    return templates.TemplateResponse("admin/user/edit_user.html", {"request": request, "title": "Chinh sua nguoi dung", "flash": pop_flash(request), "row": row, "action": "edit"})


@router.post("/users/update/{user_id}")
def user_update(request: Request, user_id: int, username: str = Form(""), fullname: str = Form(""), role: str = Form("staff")):
    guard = _guard_admin(request)
    if guard:
        return guard
    execute("UPDATE users SET username=:username, fullname=:fullname, role=:role WHERE id=:id", {"username": username, "fullname": fullname, "role": role, "id": user_id})
    set_flash(request, success="Cap nhat nguoi dung thanh cong")
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/users/delete/{user_id}")
def user_delete(request: Request, user_id: int):
    guard = _guard_admin(request)
    if guard:
        return guard
    row = fetch_one("SELECT username FROM users WHERE id=:id", {"id": user_id})
    if row and row["username"] == request.session.get("username"):
        set_flash(request, error="Ban khong the xoa chinh minh")
        return RedirectResponse(url="/admin/users", status_code=302)
    execute("DELETE FROM users WHERE id=:id", {"id": user_id})
    set_flash(request, success="Xoa nguoi dung thanh cong")
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/users/change-password", response_class=HTMLResponse)
def change_password_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    return templates.TemplateResponse("admin/user/change_password.html", {"request": request, "title": "Doi mat khau", "flash": pop_flash(request)})


@router.post("/users/update-password")
def update_password(request: Request, old_password: str = Form(""), new_password: str = Form(""), confirm_password: str = Form("")):
    guard = _guard_staff(request)
    if guard:
        return guard
    current = fetch_one("SELECT * FROM users WHERE username=:username", {"username": request.session.get("username")})
    if not current or not verify_password(old_password, current.get("password")):
        set_flash(request, error="Mat khau cu khong dung")
        return RedirectResponse(url="/admin/users/change-password", status_code=302)
    if new_password != confirm_password:
        set_flash(request, error="Mat khau moi va xac nhan khong khop")
        return RedirectResponse(url="/admin/users/change-password", status_code=302)
    execute("UPDATE users SET password=:password WHERE id=:id", {"password": hash_password(new_password), "id": current["id"]})
    set_flash(request, success="Doi mat khau thanh cong")
    return RedirectResponse(url="/admin/users/change-password", status_code=302)


@router.get("/medical-records", response_class=HTMLResponse)
def medical_records_page(request: Request, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    total = fetch_one("SELECT COUNT(*) AS total FROM medical_records")["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT mr.*, c.customer_name, p.pet_name, d.doctor_name,
               (SELECT COUNT(*) FROM medical_record_services mrs WHERE mrs.medical_record_id = mr.medical_record_id) AS total_services,
               (SELECT COUNT(*) FROM medical_record_medicines mrm WHERE mrm.medical_record_id = mr.medical_record_id) AS total_medicines
        FROM medical_records mr
        LEFT JOIN customers c ON c.customer_id = mr.customer_id
        LEFT JOIN pets p ON p.pet_id = mr.pet_id
        LEFT JOIN doctors d ON d.doctor_id = mr.doctor_id
        ORDER BY mr.medical_record_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": 10, "offset": offset},
    )
    return templates.TemplateResponse("admin/medical_record/medical_records.html", {"request": request, "title": "Lich su kham benh", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages})


@router.get("/medical-records/add", response_class=HTMLResponse)
def medical_record_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name, pet_species FROM pets ORDER BY pet_name ASC")
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    services = fetch_all("SELECT service_type_id, service_name, price FROM service_types ORDER BY service_name ASC")
    medicines = fetch_all("SELECT medicine_id, medicine_name, unit_price FROM medicines ORDER BY medicine_name ASC")
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name, unit_price FROM vaccines ORDER BY vaccine_name ASC")
    return templates.TemplateResponse(
        "admin/medical_record/add_medical_record.html",
        {
            "request": request,
            "title": "Them phieu kham",
            "flash": pop_flash(request),
            "row": None,
            "vaccination": None,
            "action": "add",
            "customers": customers,
            "pets": pets,
            "doctors": doctors,
            "services": services,
            "medicines": medicines,
            "vaccines": vaccines,
            "recordServices": [],
            "recordMedicines": [],
        },
    )


@router.post("/medical-records/store")
def medical_record_store(
    request: Request,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    doctor_id: int = Form(...),
    type: str = Form(...),
    visit_date: str = Form(...),
    summary: str = Form(""),
    details: str = Form(""),
    vaccine_name: str = Form(""),
    batch_number: str = Form(""),
    next_injection_date: str = Form(""),
    service_ids: list[str] = Form(default=[], alias="service_ids[]"),
    service_quantities: list[str] = Form(default=[], alias="service_quantities[]"),
    service_unit_prices: list[str] = Form(default=[], alias="service_unit_prices[]"),
    service_total_prices: list[str] = Form(default=[], alias="service_total_prices[]"),
    medicine_ids: list[str] = Form(default=[], alias="medicine_ids[]"),
    medicine_quantities: list[str] = Form(default=[], alias="medicine_quantities[]"),
    medicine_unit_prices: list[str] = Form(default=[], alias="medicine_unit_prices[]"),
    medicine_total_prices: list[str] = Form(default=[], alias="medicine_total_prices[]"),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    normalized_type = _normalize_medical_record_type(type)
    execute(
        """
        INSERT INTO medical_records (customer_id, pet_id, doctor_id, medical_record_type, medical_record_visit_date, medical_record_summary, medical_record_details)
        VALUES (:customer_id, :pet_id, :doctor_id, :type, :visit_date, :summary, :details)
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "doctor_id": doctor_id, "type": normalized_type, "visit_date": visit_date, "summary": summary or None, "details": details or None},
    )
    record = fetch_one("SELECT medical_record_id FROM medical_records ORDER BY medical_record_id DESC LIMIT 1")
    if normalized_type == "Vaccine" and vaccine_name:
        execute(
            """
            INSERT INTO vaccination_records (medical_record_id, vaccine_name, batch_number, next_injection_date)
            VALUES (:medical_record_id, :vaccine_name, :batch_number, :next_injection_date)
            """,
            {"medical_record_id": record["medical_record_id"], "vaccine_name": vaccine_name, "batch_number": batch_number or None, "next_injection_date": next_injection_date or None},
        )
    save_record_services(record["medical_record_id"], service_ids, service_quantities, service_unit_prices, service_total_prices)
    save_record_medicines(record["medical_record_id"], medicine_ids, medicine_quantities, medicine_unit_prices, medicine_total_prices)
    set_flash(request, success="Them phieu kham thanh cong")
    return RedirectResponse(url="/admin/medical-records", status_code=302)


@router.get("/medical-records/edit/{record_id}", response_class=HTMLResponse)
def medical_record_edit_page(request: Request, record_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM medical_records WHERE medical_record_id=:id", {"id": record_id})
    vaccination = fetch_one("SELECT * FROM vaccination_records WHERE medical_record_id=:id", {"id": record_id})
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name, pet_species FROM pets ORDER BY pet_name ASC")
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    services = fetch_all("SELECT service_type_id, service_name, price FROM service_types ORDER BY service_name ASC")
    medicines = fetch_all("SELECT medicine_id, medicine_name, unit_price FROM medicines ORDER BY medicine_name ASC")
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name, unit_price FROM vaccines ORDER BY vaccine_name ASC")
    return templates.TemplateResponse(
        "admin/medical_record/edit_medical_record.html",
        {
            "request": request,
            "title": "Chinh sua phieu kham",
            "flash": pop_flash(request),
            "row": row,
            "vaccination": vaccination,
            "action": "edit",
            "customers": customers,
            "pets": pets,
            "doctors": doctors,
            "services": services,
            "medicines": medicines,
            "vaccines": vaccines,
            "recordServices": load_record_services(record_id),
            "recordMedicines": load_record_medicines(record_id),
        },
    )


@router.post("/medical-records/update/{record_id}")
def medical_record_update(
    request: Request,
    record_id: int,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    doctor_id: int = Form(...),
    type: str = Form(...),
    visit_date: str = Form(...),
    summary: str = Form(""),
    details: str = Form(""),
    vaccine_name: str = Form(""),
    batch_number: str = Form(""),
    next_injection_date: str = Form(""),
    service_ids: list[str] = Form(default=[], alias="service_ids[]"),
    service_quantities: list[str] = Form(default=[], alias="service_quantities[]"),
    service_unit_prices: list[str] = Form(default=[], alias="service_unit_prices[]"),
    service_total_prices: list[str] = Form(default=[], alias="service_total_prices[]"),
    medicine_ids: list[str] = Form(default=[], alias="medicine_ids[]"),
    medicine_quantities: list[str] = Form(default=[], alias="medicine_quantities[]"),
    medicine_unit_prices: list[str] = Form(default=[], alias="medicine_unit_prices[]"),
    medicine_total_prices: list[str] = Form(default=[], alias="medicine_total_prices[]"),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    normalized_type = _normalize_medical_record_type(type)
    old = fetch_one("SELECT medical_record_type FROM medical_records WHERE medical_record_id=:id", {"id": record_id})
    execute(
        """
        UPDATE medical_records
        SET customer_id=:customer_id, pet_id=:pet_id, doctor_id=:doctor_id, medical_record_type=:type,
            medical_record_visit_date=:visit_date, medical_record_summary=:summary, medical_record_details=:details
        WHERE medical_record_id=:id
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "doctor_id": doctor_id, "type": normalized_type, "visit_date": visit_date, "summary": summary or None, "details": details or None, "id": record_id},
    )
    existing = fetch_one("SELECT medical_record_id FROM vaccination_records WHERE medical_record_id=:id", {"id": record_id})
    if normalized_type == "Vaccine":
        if existing:
            execute(
                """
                UPDATE vaccination_records
                SET vaccine_name=:vaccine_name, batch_number=:batch_number, next_injection_date=:next_injection_date
                WHERE medical_record_id=:id
                """,
                {"vaccine_name": vaccine_name, "batch_number": batch_number or None, "next_injection_date": next_injection_date or None, "id": record_id},
            )
        elif vaccine_name:
            execute(
                "INSERT INTO vaccination_records (medical_record_id, vaccine_name, batch_number, next_injection_date) VALUES (:id, :vaccine_name, :batch_number, :next_injection_date)",
                {"id": record_id, "vaccine_name": vaccine_name, "batch_number": batch_number or None, "next_injection_date": next_injection_date or None},
            )
    elif old and old["medical_record_type"] == "Vaccine":
        execute("DELETE FROM vaccination_records WHERE medical_record_id=:id", {"id": record_id})
    save_record_services(record_id, service_ids, service_quantities, service_unit_prices, service_total_prices)
    save_record_medicines(record_id, medicine_ids, medicine_quantities, medicine_unit_prices, medicine_total_prices)
    set_flash(request, success="Cap nhat phieu kham thanh cong")
    return RedirectResponse(url="/admin/medical-records", status_code=302)


@router.get("/medical-records/delete/{record_id}")
def medical_record_delete(request: Request, record_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM medical_record_services WHERE medical_record_id=:id", {"id": record_id})
    execute("DELETE FROM medical_record_medicines WHERE medical_record_id=:id", {"id": record_id})
    execute("DELETE FROM vaccination_records WHERE medical_record_id=:id", {"id": record_id})
    execute("DELETE FROM medical_records WHERE medical_record_id=:id", {"id": record_id})
    set_flash(request, success="Xoa phieu kham thanh cong")
    return RedirectResponse(url="/admin/medical-records", status_code=302)


@router.get("/invoices", response_class=HTMLResponse)
def invoices_page(request: Request, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    total = fetch_one("SELECT COUNT(*) AS total FROM invoices")["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT i.*, c.customer_name, p.pet_name
        FROM invoices i
        LEFT JOIN customers c ON c.customer_id=i.customer_id
        LEFT JOIN pets p ON p.pet_id=i.pet_id
        ORDER BY i.invoice_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": 10, "offset": offset},
    )
    return templates.TemplateResponse("admin/invoice/invoices.html", {"request": request, "title": "Danh sach hoa don", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages})


@router.get("/invoices/add", response_class=HTMLResponse)
def invoice_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    services = fetch_all("SELECT service_type_id, service_name, price FROM service_types ORDER BY service_name ASC")
    medicines = fetch_all("SELECT medicine_id, medicine_name, unit_price FROM medicines ORDER BY medicine_name ASC")
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name, unit_price FROM vaccines ORDER BY vaccine_name ASC")
    records = fetch_all(
        """
        SELECT mr.medical_record_id, mr.customer_id, mr.pet_id, mr.medical_record_visit_date, c.customer_name, p.pet_name
        FROM medical_records mr
        LEFT JOIN customers c ON c.customer_id = mr.customer_id
        LEFT JOIN pets p ON p.pet_id = mr.pet_id
        ORDER BY mr.medical_record_id DESC
        """
    )
    return templates.TemplateResponse(
        "admin/invoice/add_invoice.html",
        {
            "request": request,
            "title": "Them hoa don",
            "flash": pop_flash(request),
            "row": None,
            "details": [],
            "medicineDetails": [],
            "vaccinationDetails": [],
            "action": "add",
            "customers": customers,
            "pets": pets,
            "services": services,
            "serviceTypes": services,
            "medicines": medicines,
            "vaccines": vaccines,
            "medicalRecords": records,
        },
    )


@router.get("/invoices/add-from-visit/{record_id}")
def invoice_add_from_visit(request: Request, record_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    record = fetch_one("SELECT * FROM medical_records WHERE medical_record_id=:id", {"id": record_id})
    if not record:
        set_flash(request, error="Khong tim thay phieu kham")
        return RedirectResponse(url="/admin/invoices", status_code=302)
    service_rows = fetch_all(
        """
        SELECT service_type_id, quantity, unit_price, total_price
        FROM medical_record_services
        WHERE medical_record_id=:id
        ORDER BY record_service_id ASC
        """,
        {"id": record_id},
    )
    medicine_rows = fetch_all(
        """
        SELECT medicine_id, quantity, unit_price, total_price
        FROM medical_record_medicines
        WHERE medical_record_id=:id
        ORDER BY record_medicine_id ASC
        """,
        {"id": record_id},
    )
    subtotal = sum(int(r.get("total_price") or 0) for r in service_rows + medicine_rows)
    execute(
        """
        INSERT INTO invoices (customer_id, pet_id, medical_record_id, invoice_date, discount, subtotal, deposit, total_amount)
        VALUES (:customer_id, :pet_id, :medical_record_id, :invoice_date, 0, :subtotal, 0, :total_amount)
        """,
        {
            "customer_id": record["customer_id"],
            "pet_id": record["pet_id"],
            "medical_record_id": record_id,
            "invoice_date": datetime.now(),
            "subtotal": subtotal,
            "total_amount": subtotal,
        },
    )
    invoice = fetch_one("SELECT invoice_id FROM invoices ORDER BY invoice_id DESC LIMIT 1")
    for row in service_rows:
        execute(
            """
            INSERT INTO invoice_details (invoice_id, service_type_id, quantity, unit_price, total_price)
            VALUES (:invoice_id, :service_type_id, :quantity, :unit_price, :total_price)
            """,
            {
                "invoice_id": invoice["invoice_id"],
                "service_type_id": row["service_type_id"],
                "quantity": int(row.get("quantity") or 1),
                "unit_price": int(row.get("unit_price") or 0),
                "total_price": int(row.get("total_price") or 0),
            },
        )
    for row in medicine_rows:
        execute(
            """
            INSERT INTO invoice_medicine_details (invoice_id, medicine_id, quantity, unit_price, total_price)
            VALUES (:invoice_id, :medicine_id, :quantity, :unit_price, :total_price)
            """,
            {
                "invoice_id": invoice["invoice_id"],
                "medicine_id": row["medicine_id"],
                "quantity": int(row.get("quantity") or 1),
                "unit_price": int(row.get("unit_price") or 0),
                "total_price": int(row.get("total_price") or 0),
            },
        )
    set_flash(request, success="Them hoa don thanh cong")
    return RedirectResponse(url=f"/admin/invoices/edit/{invoice['invoice_id']}", status_code=302)


@router.get("/invoices/edit/{invoice_id}", response_class=HTMLResponse)
def invoice_edit_page(request: Request, invoice_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM invoices WHERE invoice_id=:id", {"id": invoice_id})
    details = fetch_all("SELECT * FROM invoice_details WHERE invoice_id=:id ORDER BY detail_id ASC", {"id": invoice_id})
    medicine_details = load_invoice_medicines(invoice_id)
    vaccination_details = load_invoice_vaccinations(invoice_id)
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    services = fetch_all("SELECT service_type_id, service_name, price FROM service_types ORDER BY service_name ASC")
    medicines = fetch_all("SELECT medicine_id, medicine_name, unit_price FROM medicines ORDER BY medicine_name ASC")
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name, unit_price FROM vaccines ORDER BY vaccine_name ASC")
    records = fetch_all(
        """
        SELECT mr.medical_record_id, mr.customer_id, mr.pet_id, mr.medical_record_visit_date, c.customer_name, p.pet_name
        FROM medical_records mr
        LEFT JOIN customers c ON c.customer_id = mr.customer_id
        LEFT JOIN pets p ON p.pet_id = mr.pet_id
        ORDER BY mr.medical_record_id DESC
        """
    )
    return templates.TemplateResponse(
        "admin/invoice/edit_invoice.html",
        {
            "request": request,
            "title": "Chinh sua hoa don",
            "flash": pop_flash(request),
            "row": row,
            "details": details,
            "medicineDetails": medicine_details,
            "vaccinationDetails": vaccination_details,
            "action": "edit",
            "customers": customers,
            "pets": pets,
            "services": services,
            "serviceTypes": services,
            "medicines": medicines,
            "vaccines": vaccines,
            "medicalRecords": records,
        },
    )


def _save_invoice_details(invoice_id: int, service_ids: list[str], quantities: list[str], unit_prices: list[str], total_prices: list[str]) -> None:
    execute("DELETE FROM invoice_details WHERE invoice_id=:id", {"id": invoice_id})
    for i, service_id in enumerate(service_ids):
        if not service_id:
            continue
        execute(
            """
            INSERT INTO invoice_details (invoice_id, service_type_id, quantity, unit_price, total_price)
            VALUES (:invoice_id, :service_type_id, :quantity, :unit_price, :total_price)
            """,
            {
                "invoice_id": invoice_id,
                "service_type_id": int(service_id),
                "quantity": int(quantities[i]) if i < len(quantities) and quantities[i] else 1,
                "unit_price": int(float(unit_prices[i])) if i < len(unit_prices) and unit_prices[i] else 0,
                "total_price": int(float(total_prices[i])) if i < len(total_prices) and total_prices[i] else 0,
            },
        )


def _save_invoice_medicine_details(
    invoice_id: int, medicine_ids: list[str], quantities: list[str], unit_prices: list[str], total_prices: list[str]
) -> None:
    execute("DELETE FROM invoice_medicine_details WHERE invoice_id=:id", {"id": invoice_id})
    for i, medicine_id in enumerate(medicine_ids):
        if not medicine_id:
            continue
        execute(
            """
            INSERT INTO invoice_medicine_details (invoice_id, medicine_id, quantity, unit_price, total_price)
            VALUES (:invoice_id, :medicine_id, :quantity, :unit_price, :total_price)
            """,
            {
                "invoice_id": invoice_id,
                "medicine_id": int(medicine_id),
                "quantity": int(quantities[i]) if i < len(quantities) and quantities[i] else 1,
                "unit_price": int(float(unit_prices[i])) if i < len(unit_prices) and unit_prices[i] else 0,
                "total_price": int(float(total_prices[i])) if i < len(total_prices) and total_prices[i] else 0,
            },
        )


def _save_invoice_vaccination_details(
    invoice_id: int, vaccine_ids: list[str], quantities: list[str], unit_prices: list[str], total_prices: list[str]
) -> None:
    execute("DELETE FROM invoice_vaccination_details WHERE invoice_id=:id", {"id": invoice_id})
    for i, vaccine_id in enumerate(vaccine_ids):
        if not vaccine_id:
            continue
        execute(
            """
            INSERT INTO invoice_vaccination_details (invoice_id, vaccine_id, quantity, unit_price, total_price)
            VALUES (:invoice_id, :vaccine_id, :quantity, :unit_price, :total_price)
            """,
            {
                "invoice_id": invoice_id,
                "vaccine_id": int(vaccine_id),
                "quantity": int(quantities[i]) if i < len(quantities) and quantities[i] else 1,
                "unit_price": int(float(unit_prices[i])) if i < len(unit_prices) and unit_prices[i] else 0,
                "total_price": int(float(total_prices[i])) if i < len(total_prices) and total_prices[i] else 0,
            },
        )


@router.post("/invoices/store")
def invoice_store(
    request: Request,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    invoice_date: str = Form(...),
    discount: int = Form(0),
    subtotal: int = Form(0),
    deposit: int = Form(0),
    total_amount: int = Form(0),
    pet_enclosure_id: str = Form(""),
    medical_record_id: str = Form(""),
    service_ids: list[str] = Form(default=[]),
    quantities: list[str] = Form(default=[]),
    unit_prices: list[str] = Form(default=[]),
    total_prices: list[str] = Form(default=[]),
    medicine_ids: list[str] = Form(default=[]),
    medicine_quantities: list[str] = Form(default=[]),
    medicine_unit_prices: list[str] = Form(default=[]),
    medicine_total_prices: list[str] = Form(default=[]),
    vaccine_ids: list[str] = Form(default=[]),
    vaccine_quantities: list[str] = Form(default=[]),
    vaccine_unit_prices: list[str] = Form(default=[]),
    vaccine_total_prices: list[str] = Form(default=[]),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO invoices (customer_id, pet_id, pet_enclosure_id, medical_record_id, invoice_date, discount, subtotal, deposit, total_amount)
        VALUES (:customer_id, :pet_id, :pet_enclosure_id, :medical_record_id, :invoice_date, :discount, :subtotal, :deposit, :total_amount)
        """,
        {
            "customer_id": customer_id,
            "pet_id": pet_id,
            "pet_enclosure_id": int(pet_enclosure_id) if pet_enclosure_id else None,
            "medical_record_id": int(medical_record_id) if medical_record_id else None,
            "invoice_date": invoice_date,
            "discount": discount or 0,
            "subtotal": subtotal or 0,
            "deposit": deposit or 0,
            "total_amount": total_amount or 0,
        },
    )
    invoice = fetch_one("SELECT invoice_id FROM invoices ORDER BY invoice_id DESC LIMIT 1")
    _save_invoice_details(invoice["invoice_id"], service_ids, quantities, unit_prices, total_prices)
    _save_invoice_medicine_details(
        invoice["invoice_id"], medicine_ids, medicine_quantities, medicine_unit_prices, medicine_total_prices
    )
    _save_invoice_vaccination_details(
        invoice["invoice_id"], vaccine_ids, vaccine_quantities, vaccine_unit_prices, vaccine_total_prices
    )
    set_flash(request, success="Them hoa don thanh cong")
    return RedirectResponse(url="/admin/invoices", status_code=302)


@router.post("/invoices/update/{invoice_id}")
def invoice_update(
    request: Request,
    invoice_id: int,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    invoice_date: str = Form(...),
    discount: int = Form(0),
    subtotal: int = Form(0),
    deposit: int = Form(0),
    total_amount: int = Form(0),
    pet_enclosure_id: str = Form(""),
    medical_record_id: str = Form(""),
    service_ids: list[str] = Form(default=[]),
    quantities: list[str] = Form(default=[]),
    unit_prices: list[str] = Form(default=[]),
    total_prices: list[str] = Form(default=[]),
    medicine_ids: list[str] = Form(default=[]),
    medicine_quantities: list[str] = Form(default=[]),
    medicine_unit_prices: list[str] = Form(default=[]),
    medicine_total_prices: list[str] = Form(default=[]),
    vaccine_ids: list[str] = Form(default=[]),
    vaccine_quantities: list[str] = Form(default=[]),
    vaccine_unit_prices: list[str] = Form(default=[]),
    vaccine_total_prices: list[str] = Form(default=[]),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE invoices
        SET customer_id=:customer_id, pet_id=:pet_id, pet_enclosure_id=:pet_enclosure_id, medical_record_id=:medical_record_id, invoice_date=:invoice_date,
            discount=:discount, subtotal=:subtotal, deposit=:deposit, total_amount=:total_amount
        WHERE invoice_id=:id
        """,
        {
            "customer_id": customer_id,
            "pet_id": pet_id,
            "pet_enclosure_id": int(pet_enclosure_id) if pet_enclosure_id else None,
            "medical_record_id": int(medical_record_id) if medical_record_id else None,
            "invoice_date": invoice_date,
            "discount": discount or 0,
            "subtotal": subtotal or 0,
            "deposit": deposit or 0,
            "total_amount": total_amount or 0,
            "id": invoice_id,
        },
    )
    _save_invoice_details(invoice_id, service_ids, quantities, unit_prices, total_prices)
    _save_invoice_medicine_details(invoice_id, medicine_ids, medicine_quantities, medicine_unit_prices, medicine_total_prices)
    _save_invoice_vaccination_details(invoice_id, vaccine_ids, vaccine_quantities, vaccine_unit_prices, vaccine_total_prices)
    set_flash(request, success="Cap nhat hoa don thanh cong")
    return RedirectResponse(url="/admin/invoices", status_code=302)


@router.get("/invoices/delete/{invoice_id}")
def invoice_delete(request: Request, invoice_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM invoice_details WHERE invoice_id=:id", {"id": invoice_id})
    execute("DELETE FROM invoice_medicine_details WHERE invoice_id=:id", {"id": invoice_id})
    execute("DELETE FROM invoice_vaccination_details WHERE invoice_id=:id", {"id": invoice_id})
    execute("DELETE FROM invoices WHERE invoice_id=:id", {"id": invoice_id})
    set_flash(request, success="Xoa hoa don thanh cong")
    return RedirectResponse(url="/admin/invoices", status_code=302)


@router.get("/pet-enclosures", response_class=HTMLResponse)
def pet_enclosures_page(request: Request, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    total = fetch_one("SELECT COUNT(*) AS total FROM pet_enclosures")["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT pe.*, c.customer_name, p.pet_name
        FROM pet_enclosures pe
        LEFT JOIN customers c ON c.customer_id=pe.customer_id
        LEFT JOIN pets p ON p.pet_id=pe.pet_id
        ORDER BY pe.pet_enclosure_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": 10, "offset": offset},
    )
    return templates.TemplateResponse("admin/pet_enclosure/pet_enclosures.html", {"request": request, "title": "Danh sach luu chuong", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages})


@router.get("/pet-enclosures/add", response_class=HTMLResponse)
def pet_enclosure_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name, pet_species FROM pets ORDER BY pet_name ASC")
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse("admin/pet_enclosure/add_pet_enclosure.html", {"request": request, "title": "Them luu chuong", "flash": pop_flash(request), "row": None, "action": "add", "customers": customers, "pets": pets, "settings": settings})


@router.get("/pet-enclosures/edit/{enclosure_id}", response_class=HTMLResponse)
def pet_enclosure_edit_page(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM pet_enclosures WHERE pet_enclosure_id=:id", {"id": enclosure_id})
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name, pet_species FROM pets ORDER BY pet_name ASC")
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse("admin/pet_enclosure/edit_pet_enclosure.html", {"request": request, "title": "Chinh sua luu chuong", "flash": pop_flash(request), "row": row, "action": "edit", "customers": customers, "pets": pets, "settings": settings})


@router.post("/pet-enclosures/store")
def pet_enclosure_store(
    request: Request,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    enclosure_number: int = Form(...),
    check_in_date: str = Form(...),
    check_out_date: str = Form(""),
    daily_rate: int = Form(0),
    deposit: int = Form(0),
    emergency_limit: int = Form(0),
    note: str = Form(""),
    status: str = Form("Check In"),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO pet_enclosures (customer_id, pet_id, pet_enclosure_number, check_in_date, check_out_date, daily_rate, deposit, emergency_limit, pet_enclosure_note, pet_enclosure_status)
        VALUES (:customer_id, :pet_id, :num, :check_in, :check_out, :daily_rate, :deposit, :emergency_limit, :note, :status)
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "num": enclosure_number, "check_in": check_in_date, "check_out": check_out_date or None, "daily_rate": daily_rate, "deposit": deposit or 0, "emergency_limit": emergency_limit or 0, "note": note or None, "status": status},
    )
    set_flash(request, success="Them luu chuong thanh cong")
    return RedirectResponse(url="/admin/pet-enclosures", status_code=302)


@router.post("/pet-enclosures/update/{enclosure_id}")
def pet_enclosure_update(
    request: Request,
    enclosure_id: int,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    enclosure_number: int = Form(...),
    check_in_date: str = Form(...),
    check_out_date: str = Form(""),
    daily_rate: int = Form(0),
    deposit: int = Form(0),
    emergency_limit: int = Form(0),
    note: str = Form(""),
    status: str = Form("Check In"),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE pet_enclosures
        SET customer_id=:customer_id, pet_id=:pet_id, pet_enclosure_number=:num, check_in_date=:check_in, check_out_date=:check_out,
            daily_rate=:daily_rate, deposit=:deposit, emergency_limit=:emergency_limit, pet_enclosure_note=:note, pet_enclosure_status=:status
        WHERE pet_enclosure_id=:id
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "num": enclosure_number, "check_in": check_in_date, "check_out": check_out_date or None, "daily_rate": daily_rate, "deposit": deposit or 0, "emergency_limit": emergency_limit or 0, "note": note or None, "status": status, "id": enclosure_id},
    )
    set_flash(request, success="Cap nhat luu chuong thanh cong")
    return RedirectResponse(url="/admin/pet-enclosures", status_code=302)


@router.get("/pet-enclosures/checkout/{enclosure_id}", response_class=HTMLResponse)
def pet_enclosure_checkout_page(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one(
        """
        SELECT pe.*, c.customer_name, p.pet_name
        FROM pet_enclosures pe
        LEFT JOIN customers c ON c.customer_id=pe.customer_id
        LEFT JOIN pets p ON p.pet_id=pe.pet_id
        WHERE pe.pet_enclosure_id=:id
        """,
        {"id": enclosure_id},
    )
    if not row:
        set_flash(request, error="Khong tim thay luu chuong")
        return RedirectResponse(url="/admin/pet-enclosures", status_code=302)
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": row["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": row["pet_id"]})
    check_in = row.get("check_in_date")
    now_dt = datetime.now()
    if isinstance(check_in, datetime):
        delta_days = (now_dt.date() - check_in.date()).days + 1
    else:
        delta_days = 1
    days = max(1, delta_days)
    enclosure_fee = int(row.get("daily_rate") or 0) * days
    overtime_fee = 0
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    services = fetch_all("SELECT service_type_id, service_name, price FROM service_types ORDER BY service_name ASC")
    boarding = fetch_one(
        "SELECT service_type_id FROM service_types WHERE service_name = :name LIMIT 1",
        {"name": "Lưu chuồng theo ngày"},
    )
    boarding_service_id = boarding["service_type_id"] if boarding else None
    return templates.TemplateResponse(
        "admin/pet_enclosure/checkout_invoice.html",
        {
            "request": request,
            "title": "Checkout luu chuong",
            "flash": pop_flash(request),
            "row": row,
            "customer": customer,
            "pet": pet,
            "settings": settings,
            "services": services,
            "serviceTypes": services,
            "boardingServiceId": boarding_service_id,
            "days": days,
            "enclosureFee": enclosure_fee,
            "overtimeFee": overtime_fee,
        },
    )


@router.post("/pet-enclosures/checkout/{enclosure_id}")
def pet_enclosure_checkout_process(
    request: Request,
    enclosure_id: int,
    discount: int = Form(0),
    subtotal: int = Form(0),
    total_amount: int = Form(0),
    service_ids: list[str] = Form(default=[]),
    quantities: list[str] = Form(default=[]),
    unit_prices: list[str] = Form(default=[]),
    total_prices: list[str] = Form(default=[]),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    enclosure = fetch_one("SELECT * FROM pet_enclosures WHERE pet_enclosure_id=:id", {"id": enclosure_id})
    execute(
        "UPDATE pet_enclosures SET check_out_date=:check_out_date, pet_enclosure_status='Check Out' WHERE pet_enclosure_id=:id",
        {"id": enclosure_id, "check_out_date": datetime.now()},
    )
    execute(
        """
        INSERT INTO invoices (customer_id, pet_id, pet_enclosure_id, invoice_date, discount, subtotal, deposit, total_amount)
        VALUES (:customer_id, :pet_id, :pet_enclosure_id, :invoice_date, :discount, :subtotal, :deposit, :total_amount)
        """,
        {"customer_id": enclosure["customer_id"], "pet_id": enclosure["pet_id"], "pet_enclosure_id": enclosure_id, "invoice_date": datetime.now(), "discount": discount, "subtotal": subtotal, "deposit": enclosure["deposit"], "total_amount": total_amount},
    )
    invoice = fetch_one("SELECT invoice_id FROM invoices ORDER BY invoice_id DESC LIMIT 1")
    _save_invoice_details(invoice["invoice_id"], service_ids, quantities, unit_prices, total_prices)
    set_flash(request, success="Checkout thanh cong, da tao hoa don")
    return RedirectResponse(url="/admin/invoices", status_code=302)


@router.get("/pet-enclosures/delete/{enclosure_id}")
def pet_enclosure_delete(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM pet_enclosures WHERE pet_enclosure_id=:id", {"id": enclosure_id})
    set_flash(request, success="Xoa luu chuong thanh cong")
    return RedirectResponse(url="/admin/pet-enclosures", status_code=302)


@router.get("/pet-vaccinations", response_class=HTMLResponse)
def pet_vaccinations_page(request: Request, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    total = fetch_one("SELECT COUNT(*) AS total FROM pet_vaccinations")["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT pv.*, v.vaccine_name, c.customer_name, p.pet_name, d.doctor_name, mr.medical_record_type
        FROM pet_vaccinations pv
        LEFT JOIN vaccines v ON v.vaccine_id=pv.vaccine_id
        LEFT JOIN customers c ON c.customer_id=pv.customer_id
        LEFT JOIN pets p ON p.pet_id=pv.pet_id
        LEFT JOIN doctors d ON d.doctor_id=pv.doctor_id
        LEFT JOIN medical_records mr ON mr.medical_record_id=pv.medical_record_id
        ORDER BY pv.pet_vaccination_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": 10, "offset": offset},
    )
    return templates.TemplateResponse("admin/pet_vaccination/pet_vaccinations.html", {"request": request, "title": "Lich su tiem chung", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages})


@router.get("/pet-vaccinations/add", response_class=HTMLResponse)
def pet_vaccination_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name FROM vaccines ORDER BY vaccine_name ASC")
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    records = fetch_all("SELECT medical_record_id, customer_id, pet_id, medical_record_type, medical_record_visit_date FROM medical_records ORDER BY medical_record_id DESC")
    return templates.TemplateResponse("admin/pet_vaccination/add_pet_vaccination.html", {"request": request, "title": "Them tiem chung", "flash": pop_flash(request), "row": None, "action": "add", "vaccines": vaccines, "customers": customers, "pets": pets, "doctors": doctors, "medicalRecords": records})


@router.get("/pet-vaccinations/edit/{vaccination_id}", response_class=HTMLResponse)
def pet_vaccination_edit_page(request: Request, vaccination_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM pet_vaccinations WHERE pet_vaccination_id=:id", {"id": vaccination_id})
    vaccines = fetch_all("SELECT vaccine_id, vaccine_name FROM vaccines ORDER BY vaccine_name ASC")
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    records = fetch_all("SELECT medical_record_id, customer_id, pet_id, medical_record_type, medical_record_visit_date FROM medical_records ORDER BY medical_record_id DESC")
    return templates.TemplateResponse("admin/pet_vaccination/edit_pet_vaccination.html", {"request": request, "title": "Chinh sua tiem chung", "flash": pop_flash(request), "row": row, "action": "edit", "vaccines": vaccines, "customers": customers, "pets": pets, "doctors": doctors, "medicalRecords": records})


@router.post("/pet-vaccinations/store")
def pet_vaccination_store(
    request: Request,
    vaccine_id: int = Form(...),
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    doctor_id: int = Form(...),
    vaccination_date: str = Form(...),
    next_vaccination_date: str = Form(""),
    notes: str = Form(""),
    medical_record_id: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO pet_vaccinations (vaccine_id, customer_id, pet_id, doctor_id, medical_record_id, vaccination_date, next_vaccination_date, notes)
        VALUES (:vaccine_id, :customer_id, :pet_id, :doctor_id, :medical_record_id, :vaccination_date, :next_vaccination_date, :notes)
        """,
        {"vaccine_id": vaccine_id, "customer_id": customer_id, "pet_id": pet_id, "doctor_id": doctor_id, "medical_record_id": int(medical_record_id) if medical_record_id else None, "vaccination_date": vaccination_date, "next_vaccination_date": next_vaccination_date or None, "notes": notes or None},
    )
    set_flash(request, success="Them tiem chung thanh cong")
    return RedirectResponse(url="/admin/pet-vaccinations", status_code=302)


@router.post("/pet-vaccinations/update/{vaccination_id}")
def pet_vaccination_update(
    request: Request,
    vaccination_id: int,
    vaccine_id: int = Form(...),
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    doctor_id: int = Form(...),
    vaccination_date: str = Form(...),
    next_vaccination_date: str = Form(""),
    notes: str = Form(""),
    medical_record_id: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE pet_vaccinations
        SET vaccine_id=:vaccine_id, customer_id=:customer_id, pet_id=:pet_id, doctor_id=:doctor_id,
            medical_record_id=:medical_record_id, vaccination_date=:vaccination_date, next_vaccination_date=:next_vaccination_date, notes=:notes
        WHERE pet_vaccination_id=:id
        """,
        {"vaccine_id": vaccine_id, "customer_id": customer_id, "pet_id": pet_id, "doctor_id": doctor_id, "medical_record_id": int(medical_record_id) if medical_record_id else None, "vaccination_date": vaccination_date, "next_vaccination_date": next_vaccination_date or None, "notes": notes or None, "id": vaccination_id},
    )
    set_flash(request, success="Cap nhat tiem chung thanh cong")
    return RedirectResponse(url="/admin/pet-vaccinations", status_code=302)


@router.get("/pet-vaccinations/delete/{vaccination_id}")
def pet_vaccination_delete(request: Request, vaccination_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM pet_vaccinations WHERE pet_vaccination_id=:id", {"id": vaccination_id})
    set_flash(request, success="Xoa tiem chung thanh cong")
    return RedirectResponse(url="/admin/pet-vaccinations", status_code=302)


@router.get("/treatment-courses", response_class=HTMLResponse)
def treatment_courses_page(request: Request, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    total = fetch_one("SELECT COUNT(*) AS total FROM treatment_courses")["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT tc.*, c.customer_name, p.pet_name, mr.medical_record_type
        FROM treatment_courses tc
        LEFT JOIN customers c ON c.customer_id=tc.customer_id
        LEFT JOIN pets p ON p.pet_id=tc.pet_id
        LEFT JOIN medical_records mr ON mr.medical_record_id=tc.medical_record_id
        ORDER BY tc.treatment_course_id DESC
        LIMIT :limit OFFSET :offset
        """,
        {"limit": 10, "offset": offset},
    )
    return templates.TemplateResponse("admin/treatment_course/treatment_courses.html", {"request": request, "title": "Danh sach lieu trinh", "flash": pop_flash(request), "rows": rows, "page": page, "total_pages": total_pages})


@router.get("/treatment-courses/add", response_class=HTMLResponse)
def treatment_course_add_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    records = fetch_all("SELECT medical_record_id, customer_id, pet_id, medical_record_type, medical_record_visit_date FROM medical_records ORDER BY medical_record_id DESC")
    return templates.TemplateResponse("admin/treatment_course/add_treatment_course.html", {"request": request, "title": "Them lieu trinh", "flash": pop_flash(request), "row": None, "action": "add", "customers": customers, "pets": pets, "medicalRecords": records})


@router.get("/treatment-courses/edit/{course_id}", response_class=HTMLResponse)
def treatment_course_edit_page(request: Request, course_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    customers = fetch_all("SELECT customer_id, customer_name, customer_phone_number FROM customers ORDER BY customer_name ASC")
    pets = fetch_all("SELECT pet_id, customer_id, pet_name FROM pets ORDER BY pet_name ASC")
    records = fetch_all("SELECT medical_record_id, customer_id, pet_id, medical_record_type, medical_record_visit_date FROM medical_records ORDER BY medical_record_id DESC")
    return templates.TemplateResponse("admin/treatment_course/edit_treatment_course.html", {"request": request, "title": "Chinh sua lieu trinh", "flash": pop_flash(request), "row": row, "action": "edit", "customers": customers, "pets": pets, "medicalRecords": records})


@router.post("/treatment-courses/store")
def treatment_course_store(
    request: Request,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(""),
    status: str = Form("1"),
    medical_record_id: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO treatment_courses (customer_id, pet_id, medical_record_id, start_date, end_date, status)
        VALUES (:customer_id, :pet_id, :medical_record_id, :start_date, :end_date, :status)
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "medical_record_id": int(medical_record_id) if medical_record_id else None, "start_date": start_date, "end_date": end_date or None, "status": status},
    )
    set_flash(request, success="Them lieu trinh thanh cong")
    return RedirectResponse(url="/admin/treatment-courses", status_code=302)


@router.post("/treatment-courses/update/{course_id}")
def treatment_course_update(
    request: Request,
    course_id: int,
    customer_id: int = Form(...),
    pet_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(""),
    status: str = Form("1"),
    medical_record_id: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE treatment_courses
        SET customer_id=:customer_id, pet_id=:pet_id, medical_record_id=:medical_record_id, start_date=:start_date, end_date=:end_date, status=:status
        WHERE treatment_course_id=:id
        """,
        {"customer_id": customer_id, "pet_id": pet_id, "medical_record_id": int(medical_record_id) if medical_record_id else None, "start_date": start_date, "end_date": end_date or None, "status": status, "id": course_id},
    )
    set_flash(request, success="Cap nhat lieu trinh thanh cong")
    return RedirectResponse(url="/admin/treatment-courses", status_code=302)


@router.get("/treatment-courses/complete/{course_id}")
def treatment_course_complete(request: Request, course_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("UPDATE treatment_courses SET status='0', end_date=:end_date WHERE treatment_course_id=:id", {"id": course_id, "end_date": date.today()})
    set_flash(request, success="Ket thuc lieu trinh thanh cong")
    return RedirectResponse(url="/admin/treatment-courses", status_code=302)


@router.get("/treatment-courses/delete/{course_id}")
def treatment_course_delete(request: Request, course_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    set_flash(request, success="Xoa lieu trinh thanh cong")
    return RedirectResponse(url="/admin/treatment-courses", status_code=302)


@router.get("/treatment-courses/{course_id}/sessions", response_class=HTMLResponse)
def treatment_sessions_page(request: Request, course_id: int, page: int = Query(1)):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    total = fetch_one("SELECT COUNT(*) AS total FROM treatment_sessions WHERE treatment_course_id=:id", {"id": course_id})["total"]
    page, offset, total_pages = _pager(total, page, 10)
    rows = fetch_all(
        """
        SELECT ts.*, d.doctor_name
        FROM treatment_sessions ts
        LEFT JOIN doctors d ON d.doctor_id = ts.doctor_id
        WHERE ts.treatment_course_id=:id
        ORDER BY ts.treatment_session_datetime DESC
        LIMIT :limit OFFSET :offset
        """,
        {"id": course_id, "limit": 10, "offset": offset},
    )
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]}) if course else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]}) if course else None
    return templates.TemplateResponse(
        "admin/treatment_course/treatment_sessions.html",
        {
            "request": request,
            "title": "Buoi dieu tri",
            "flash": pop_flash(request),
            "course": course,
            "rows": rows,
            "sessions": rows,
            "customer": customer,
            "pet": pet,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/treatment-courses/{course_id}/sessions/add", response_class=HTMLResponse)
def treatment_session_add_page(request: Request, course_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]}) if course else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]}) if course else None
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    return templates.TemplateResponse(
        "admin/treatment_course/add_treatment_session.html",
        {
            "request": request,
            "title": "Them buoi dieu tri",
            "flash": pop_flash(request),
            "row": None,
            "course_id": course_id,
            "course": course,
            "customer": customer,
            "pet": pet,
            "doctors": doctors,
            "action": "add",
        },
    )


@router.get("/treatment-courses/{course_id}/sessions/edit/{session_id}", response_class=HTMLResponse)
def treatment_session_edit_page(request: Request, course_id: int, session_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]}) if course else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]}) if course else None
    doctors = fetch_all("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_name ASC")
    row = fetch_one("SELECT * FROM treatment_sessions WHERE treatment_session_id=:id", {"id": session_id})
    return templates.TemplateResponse(
        "admin/treatment_course/edit_treatment_session.html",
        {
            "request": request,
            "title": "Chinh sua buoi dieu tri",
            "flash": pop_flash(request),
            "row": row,
            "session": row,
            "course_id": course_id,
            "course": course,
            "customer": customer,
            "pet": pet,
            "doctors": doctors,
            "action": "edit",
        },
    )


@router.post("/treatment-courses/{course_id}/sessions/store")
def treatment_session_store(
    request: Request,
    course_id: int,
    doctor_id: int = Form(...),
    datetime: str = Form(...),
    temperature: str = Form(""),
    weight: str = Form(""),
    pulse_rate: str = Form(""),
    respiratory_rate: str = Form(""),
    overall_notes: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO treatment_sessions (treatment_course_id, doctor_id, treatment_session_datetime, temperature, weight, pulse_rate, respiratory_rate, overall_notes)
        VALUES (:course_id, :doctor_id, :dt, :temperature, :weight, :pulse_rate, :respiratory_rate, :notes)
        """,
        {"course_id": course_id, "doctor_id": doctor_id, "dt": datetime, "temperature": temperature or None, "weight": weight or None, "pulse_rate": pulse_rate or None, "respiratory_rate": respiratory_rate or None, "notes": overall_notes or None},
    )
    set_flash(request, success="Them buoi dieu tri thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions", status_code=302)


@router.post("/treatment-courses/{course_id}/sessions/update/{session_id}")
def treatment_session_update(
    request: Request,
    course_id: int,
    session_id: int,
    doctor_id: int = Form(...),
    datetime: str = Form(...),
    temperature: str = Form(""),
    weight: str = Form(""),
    pulse_rate: str = Form(""),
    respiratory_rate: str = Form(""),
    overall_notes: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        UPDATE treatment_sessions
        SET doctor_id=:doctor_id, treatment_session_datetime=:dt, temperature=:temperature, weight=:weight,
            pulse_rate=:pulse_rate, respiratory_rate=:respiratory_rate, overall_notes=:notes
        WHERE treatment_session_id=:id
        """,
        {"doctor_id": doctor_id, "dt": datetime, "temperature": temperature or None, "weight": weight or None, "pulse_rate": pulse_rate or None, "respiratory_rate": respiratory_rate or None, "notes": overall_notes or None, "id": session_id},
    )
    set_flash(request, success="Cap nhat buoi dieu tri thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions", status_code=302)


@router.get("/treatment-courses/{course_id}/sessions/delete/{session_id}")
def treatment_session_delete(request: Request, course_id: int, session_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM diagnoses WHERE treatment_session_id=:id", {"id": session_id})
    execute("DELETE FROM prescriptions WHERE treatment_session_id=:id", {"id": session_id})
    execute("DELETE FROM treatment_sessions WHERE treatment_session_id=:id", {"id": session_id})
    set_flash(request, success="Xoa buoi dieu tri thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions", status_code=302)


@router.get("/treatment-courses/{course_id}/sessions/{session_id}/diagnosis", response_class=HTMLResponse)
def diagnosis_page(request: Request, course_id: int, session_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    session_row = fetch_one("SELECT * FROM treatment_sessions WHERE treatment_session_id=:id", {"id": session_id})
    diagnosis = fetch_one("SELECT * FROM diagnoses WHERE treatment_session_id=:id LIMIT 1", {"id": session_id})
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]}) if course else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]}) if course else None
    doctor = fetch_one("SELECT * FROM doctors WHERE doctor_id=:id", {"id": session_row["doctor_id"]}) if session_row and session_row.get("doctor_id") else None
    return templates.TemplateResponse(
        "admin/treatment_course/diagnosis.html",
        {
            "request": request,
            "title": "Chan doan",
            "flash": pop_flash(request),
            "course_id": course_id,
            "course": course,
            "session": session_row,
            "diagnosis": diagnosis,
            "customer": customer,
            "pet": pet,
            "doctor": doctor,
        },
    )


@router.post("/treatment-courses/{course_id}/sessions/{session_id}/diagnosis/save")
def diagnosis_save(
    request: Request,
    course_id: int,
    session_id: int,
    diagnosis_name: str = Form(""),
    diagnosis_type: str = Form("1"),
    clinical_tests: str = Form(""),
    notes: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    existing = fetch_one("SELECT diagnosis_id FROM diagnoses WHERE treatment_session_id=:id LIMIT 1", {"id": session_id})
    if existing:
        execute(
            """
            UPDATE diagnoses
            SET diagnosis_name=:diagnosis_name, diagnosis_type=:diagnosis_type, clinical_tests=:clinical_tests, notes=:notes
            WHERE diagnosis_id=:id
            """,
            {"diagnosis_name": diagnosis_name, "diagnosis_type": diagnosis_type, "clinical_tests": clinical_tests or None, "notes": notes or None, "id": existing["diagnosis_id"]},
        )
    else:
        execute(
            """
            INSERT INTO diagnoses (treatment_session_id, diagnosis_name, diagnosis_type, clinical_tests, notes)
            VALUES (:session_id, :diagnosis_name, :diagnosis_type, :clinical_tests, :notes)
            """,
            {"session_id": session_id, "diagnosis_name": diagnosis_name, "diagnosis_type": diagnosis_type, "clinical_tests": clinical_tests or None, "notes": notes or None},
        )
    set_flash(request, success="Luu chan doan thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions/{session_id}/diagnosis", status_code=302)


@router.get("/treatment-courses/{course_id}/sessions/{session_id}/prescription", response_class=HTMLResponse)
def prescription_page(request: Request, course_id: int, session_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    session_row = fetch_one("SELECT * FROM treatment_sessions WHERE treatment_session_id=:id", {"id": session_id})
    medicines = fetch_all("SELECT medicine_id, medicine_name FROM medicines ORDER BY medicine_name ASC")
    rows = fetch_all(
        """
        SELECT p.*, m.medicine_name, m.medicine_route
        FROM prescriptions p
        LEFT JOIN medicines m ON m.medicine_id=p.medicine_id
        WHERE p.treatment_session_id=:id
        ORDER BY p.prescription_id DESC
        """,
        {"id": session_id},
    )
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]}) if course else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]}) if course else None
    doctor = fetch_one("SELECT * FROM doctors WHERE doctor_id=:id", {"id": session_row["doctor_id"]}) if session_row and session_row.get("doctor_id") else None
    return templates.TemplateResponse(
        "admin/treatment_course/prescription.html",
        {
            "request": request,
            "title": "Don thuoc",
            "flash": pop_flash(request),
            "course_id": course_id,
            "session_id": session_id,
            "course": course,
            "session": session_row,
            "rows": rows,
            "prescriptions": rows,
            "medicines": medicines,
            "customer": customer,
            "pet": pet,
            "doctor": doctor,
        },
    )


@router.post("/treatment-courses/{course_id}/sessions/{session_id}/prescription/add")
def prescription_add(
    request: Request,
    course_id: int,
    session_id: int,
    medicine_id: int = Form(...),
    treatment_type: str = Form("uống"),
    dosage: str = Form("0"),
    unit: str = Form("mg"),
    frequency: str = Form(""),
    status: str = Form("1"),
    notes: str = Form(""),
):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute(
        """
        INSERT INTO prescriptions (treatment_session_id, medicine_id, treatment_type, dosage, unit, frequency, status, notes)
        VALUES (:session_id, :medicine_id, :treatment_type, :dosage, :unit, :frequency, :status, :notes)
        """,
        {"session_id": session_id, "medicine_id": medicine_id, "treatment_type": treatment_type, "dosage": dosage or 0, "unit": unit, "frequency": frequency or None, "status": status, "notes": notes or None},
    )
    set_flash(request, success="Them thuoc vao don thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions/{session_id}/prescription", status_code=302)


@router.get("/treatment-courses/{course_id}/sessions/{session_id}/prescription/delete/{prescription_id}")
def prescription_delete(request: Request, course_id: int, session_id: int, prescription_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    execute("DELETE FROM prescriptions WHERE prescription_id=:id", {"id": prescription_id})
    set_flash(request, success="Xoa thuoc khoi don thanh cong")
    return RedirectResponse(url=f"/admin/treatment-courses/{course_id}/sessions/{session_id}/prescription", status_code=302)


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    guard = _guard_admin(request)
    if guard:
        return guard
    row = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse("admin/settings/settings.html", {"request": request, "title": "Cai dat chung", "flash": pop_flash(request), "row": row})


@router.post("/settings/update")
def settings_update(
    request: Request,
    clinic_name: str = Form(""),
    clinic_address_1: str = Form(""),
    clinic_address_2: str = Form(""),
    phone_number_1: str = Form(""),
    phone_number_2: str = Form(""),
    representative_name: str = Form(""),
    default_daily_rate: int = Form(0),
    checkout_hour: str = Form("18:00:00"),
    overtime_fee_per_hour: int = Form(0),
    signing_place: str = Form(""),
):
    guard = _guard_admin(request)
    if guard:
        return guard
    existing = fetch_one("SELECT setting_id FROM general_settings LIMIT 1")
    if existing:
        execute(
            """
            UPDATE general_settings
            SET clinic_name=:clinic_name, clinic_address_1=:clinic_address_1, clinic_address_2=:clinic_address_2,
                phone_number_1=:phone_number_1, phone_number_2=:phone_number_2, representative_name=:representative_name,
                default_daily_rate=:default_daily_rate, checkout_hour=:checkout_hour, overtime_fee_per_hour=:overtime_fee_per_hour,
                signing_place=:signing_place
            WHERE setting_id=:id
            """,
            {"clinic_name": clinic_name, "clinic_address_1": clinic_address_1, "clinic_address_2": clinic_address_2 or None, "phone_number_1": phone_number_1, "phone_number_2": phone_number_2 or None, "representative_name": representative_name or None, "default_daily_rate": default_daily_rate or 0, "checkout_hour": checkout_hour, "overtime_fee_per_hour": overtime_fee_per_hour or 0, "signing_place": signing_place or None, "id": existing["setting_id"]},
        )
    set_flash(request, success="Cap nhat cai dat thanh cong")
    return RedirectResponse(url="/admin/settings", status_code=302)


@router.get("/print/invoice/{invoice_id}", response_class=HTMLResponse)
def print_invoice(request: Request, invoice_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    invoice = fetch_one("SELECT * FROM invoices WHERE invoice_id=:id", {"id": invoice_id})
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": invoice["customer_id"]}) if invoice else None
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": invoice["pet_id"]}) if invoice else None
    details = fetch_all(
        """
        SELECT d.*, s.service_name
        FROM invoice_details d
        LEFT JOIN service_types s ON s.service_type_id=d.service_type_id
        WHERE d.invoice_id=:id
        """,
        {"id": invoice_id},
    )
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse("admin/print/invoice.html", {"request": request, "title": "In hoa don", "invoice": invoice, "customer": customer, "pet": pet, "details": details, "settings": settings, "flash": pop_flash(request)})


@router.get("/print/medical-record/{record_id}", response_class=HTMLResponse)
def print_medical_record(request: Request, record_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    record = fetch_one("SELECT * FROM medical_records WHERE medical_record_id=:id", {"id": record_id})
    if not record:
        set_flash(request, error="Khong tim thay phieu kham")
        return RedirectResponse(url="/admin/medical-records", status_code=302)
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": record["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": record["pet_id"]})
    doctor = fetch_one("SELECT * FROM doctors WHERE doctor_id=:id", {"id": record["doctor_id"]})
    vaccination = fetch_one("SELECT * FROM vaccination_records WHERE medical_record_id=:id", {"id": record_id})
    record_services = fetch_all(
        """
        SELECT rs.*, st.service_name
        FROM medical_record_services rs
        LEFT JOIN service_types st ON st.service_type_id = rs.service_type_id
        WHERE rs.medical_record_id=:id
        ORDER BY rs.record_service_id ASC
        """,
        {"id": record_id},
    )
    record_medicines = fetch_all(
        """
        SELECT rm.*, m.medicine_name, m.medicine_route
        FROM medical_record_medicines rm
        LEFT JOIN medicines m ON m.medicine_id = rm.medicine_id
        WHERE rm.medical_record_id=:id
        ORDER BY rm.record_medicine_id ASC
        """,
        {"id": record_id},
    )
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse(
        "admin/print/medical_record.html",
        {
            "request": request,
            "title": "In phieu kham",
            "record": record,
            "customer": customer,
            "pet": pet,
            "doctor": doctor,
            "vaccination": vaccination,
            "record_services": record_services,
            "record_medicines": record_medicines,
            "settings": settings,
            "flash": pop_flash(request),
        },
    )


@router.get("/print/treatment-session/{course_id}/{session_id}", response_class=HTMLResponse)
def print_treatment_session(request: Request, course_id: int, session_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    course = fetch_one("SELECT * FROM treatment_courses WHERE treatment_course_id=:id", {"id": course_id})
    session_row = fetch_one("SELECT * FROM treatment_sessions WHERE treatment_session_id=:id", {"id": session_id})
    if not course or not session_row:
        set_flash(request, error="Khong tim thay du lieu dieu tri")
        return RedirectResponse(url="/admin/treatment-courses", status_code=302)
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": course["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": course["pet_id"]})
    doctor = fetch_one("SELECT * FROM doctors WHERE doctor_id=:id", {"id": session_row["doctor_id"]})
    diagnosis = fetch_one("SELECT * FROM diagnoses WHERE treatment_session_id=:id LIMIT 1", {"id": session_id})
    prescriptions = fetch_all(
        """
        SELECT p.*, m.medicine_name, m.medicine_route
        FROM prescriptions p
        LEFT JOIN medicines m ON m.medicine_id=p.medicine_id
        WHERE p.treatment_session_id=:id
        ORDER BY p.prescription_id ASC
        """,
        {"id": session_id},
    )
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse(
        "admin/print/treatment_session.html",
        {
            "request": request,
            "title": "In phieu dieu tri",
            "course": course,
            "session_row": session_row,
            "customer": customer,
            "pet": pet,
            "doctor": doctor,
            "diagnosis": diagnosis,
            "prescriptions": prescriptions,
            "settings": settings,
            "flash": pop_flash(request),
        },
    )


@router.get("/print/pet-enclosure/{enclosure_id}", response_class=HTMLResponse)
def print_pet_enclosure(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    enclosure = fetch_one("SELECT * FROM pet_enclosures WHERE pet_enclosure_id=:id", {"id": enclosure_id})
    if not enclosure:
        set_flash(request, error="Khong tim thay luu chuong")
        return RedirectResponse(url="/admin/pet-enclosures", status_code=302)
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": enclosure["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": enclosure["pet_id"]})
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse(
        "admin/print/pet_enclosure.html",
        {
            "request": request,
            "title": "In phieu luu chuong",
            "enclosure": enclosure,
            "customer": customer,
            "pet": pet,
            "settings": settings,
            "flash": pop_flash(request),
        },
    )


@router.get("/printing-template", response_class=HTMLResponse)
def printing_template_page(request: Request):
    return RedirectResponse(url="/admin/printing-template/pet-enclosure", status_code=302)


@router.get("/printing-template/pet-enclosure", response_class=HTMLResponse)
def printing_template_pet_enclosure_page(request: Request):
    guard = _guard_staff(request)
    if guard:
        return guard
    enclosures = fetch_all(
        """
        SELECT pe.pet_enclosure_id, pe.check_in_date, pe.check_out_date, pe.pet_enclosure_status,
               c.customer_name, p.pet_name, i.invoice_id
        FROM pet_enclosures pe
        LEFT JOIN customers c ON c.customer_id = pe.customer_id
        LEFT JOIN pets p ON p.pet_id = pe.pet_id
        LEFT JOIN invoices i ON i.pet_enclosure_id = pe.pet_enclosure_id
        ORDER BY pe.pet_enclosure_id DESC
        """
    )
    return templates.TemplateResponse(
        "admin/printing_template/pet_enclosure_printing.html",
        {"request": request, "title": "Mau in luu chuong", "flash": pop_flash(request), "enclosures": enclosures},
    )


@router.get("/printing-template/pet-enclosure/load-commit/{enclosure_id}", response_class=HTMLResponse)
def printing_template_pet_enclosure_load_commit(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    enclosure = fetch_one("SELECT * FROM pet_enclosures WHERE pet_enclosure_id=:id", {"id": enclosure_id})
    if not enclosure:
        return templates.TemplateResponse(
            "admin/printing_template/load_commit.html",
            {"request": request, "title": "Giay cam ket", "error_message": "Khong tim thay luu chuong"},
        )
    invoice = fetch_one("SELECT * FROM invoices WHERE pet_enclosure_id=:id ORDER BY invoice_id DESC LIMIT 1", {"id": enclosure_id})
    if not invoice:
        return templates.TemplateResponse(
            "admin/printing_template/load_commit.html",
            {"request": request, "title": "Giay cam ket", "error_message": "Luu chuong nay chua co hoa don"},
        )
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": enclosure["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": enclosure["pet_id"]})
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    boarding_service = fetch_one(
        "SELECT price FROM service_types WHERE service_name=:name LIMIT 1",
        {"name": "Lưu chuồng theo ngày"},
    )
    boarding_daily_rate = int((boarding_service or {}).get("price") or 0)
    display_daily_rate = boarding_daily_rate if boarding_daily_rate > 0 else int(enclosure.get("daily_rate") or 0)
    return templates.TemplateResponse(
        "admin/printing_template/load_commit.html",
        {
            "request": request,
            "title": "Giay cam ket",
            "invoice": invoice,
            "enclosure": enclosure,
            "customer": customer,
            "pet": pet,
            "settings": settings,
            "displayDailyRate": display_daily_rate,
        },
    )


@router.get("/printing-template/pet-enclosure/load-invoice/{enclosure_id}", response_class=HTMLResponse)
def printing_template_pet_enclosure_load_invoice(request: Request, enclosure_id: int):
    guard = _guard_staff(request)
    if guard:
        return guard
    invoice = fetch_one("SELECT * FROM invoices WHERE pet_enclosure_id=:id ORDER BY invoice_id DESC LIMIT 1", {"id": enclosure_id})
    if not invoice:
        return templates.TemplateResponse(
            "admin/printing_template/load_invoice.html",
            {"request": request, "title": "Mau in hoa don", "error_message": "Luu chuong nay chua co hoa don"},
        )
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": invoice["customer_id"]})
    pet = fetch_one("SELECT * FROM pets WHERE pet_id=:id", {"id": invoice["pet_id"]})
    details = fetch_all(
        """
        SELECT d.*, s.service_name
        FROM invoice_details d
        LEFT JOIN service_types s ON s.service_type_id=d.service_type_id
        WHERE d.invoice_id=:id
        """,
        {"id": invoice["invoice_id"]},
    )
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse(
        "admin/printing_template/load_invoice.html",
        {
            "request": request,
            "title": "Mau in hoa don",
            "invoice": invoice,
            "customer": customer,
            "pet": pet,
            "details": details,
            "settings": settings,
        },
    )
