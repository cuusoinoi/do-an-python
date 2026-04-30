from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import Jinja2Templates

from app.db import execute, fetch_all, fetch_one
from app.session import pop_flash, set_flash

router = APIRouter(prefix="/customer/booking", tags=["booking"])
templates = Jinja2Templates(directory="templates")


def _guard_customer(request: Request):
    if request.session.get("role") != "customer":
        set_flash(request, error="Vui long dang nhap de dat lich")
        return RedirectResponse(url="/customer/login", status_code=302)
    return None


@router.get("/", response_class=HTMLResponse)
def booking_page(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer_id = request.session["customer_id"]
    pets = fetch_all("SELECT * FROM pets WHERE customer_id=:id ORDER BY pet_id DESC", {"id": customer_id})
    doctors = fetch_all("SELECT * FROM doctors ORDER BY doctor_id DESC")
    services = fetch_all("SELECT * FROM service_types ORDER BY service_type_id DESC")
    return templates.TemplateResponse(
        "customer/booking/index.html",
        {
            "request": request,
            "title": "Dat lich hen - UIT Petcare",
            "flash": pop_flash(request),
            "pets": pets,
            "doctors": doctors,
            "services": services,
            "session": request.session,
        },
    )


@router.post("/create")
def booking_create(
    request: Request,
    pet_id: int = Form(...),
    doctor_id: int | None = Form(default=None),
    service_id: int | None = Form(default=None),
    appointment_date: str = Form(""),
    appointment_time: str = Form(""),
    appointment_type: str = Form(""),
    notes: str = Form(""),
):
    guard = _guard_customer(request)
    if guard:
        return guard
    if not appointment_date or not appointment_time or not appointment_type:
        set_flash(request, error="Vui long dien day du thong tin")
        return RedirectResponse(url="/customer/booking", status_code=302)
    pet = fetch_one(
        "SELECT pet_id FROM pets WHERE pet_id=:pet_id AND customer_id=:customer_id LIMIT 1",
        {"pet_id": pet_id, "customer_id": request.session["customer_id"]},
    )
    if not pet:
        set_flash(request, error="Thu cung khong hop le")
        return RedirectResponse(url="/customer/booking", status_code=302)
    execute(
        """
        INSERT INTO appointments
        (customer_id, pet_id, doctor_id, service_type_id, appointment_date, appointment_type, status, notes)
        VALUES (:customer_id, :pet_id, :doctor_id, :service_type_id, :appointment_date, :appointment_type, 'pending', :notes)
        """,
        {
            "customer_id": request.session["customer_id"],
            "pet_id": pet_id,
            "doctor_id": doctor_id,
            "service_type_id": service_id,
            "appointment_date": f"{appointment_date} {appointment_time}:00",
            "appointment_type": appointment_type,
            "notes": notes or None,
        },
    )
    set_flash(request, success="Dat lich thanh cong")
    return RedirectResponse(url="/customer/dashboard", status_code=302)


@router.get("/my-appointments", response_class=HTMLResponse)
def my_appointments(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    appointments = fetch_all(
        """
        SELECT a.*, p.pet_name, d.doctor_name, s.service_name
        FROM appointments a
        LEFT JOIN pets p ON p.pet_id = a.pet_id
        LEFT JOIN doctors d ON d.doctor_id = a.doctor_id
        LEFT JOIN service_types s ON s.service_type_id = a.service_type_id
        WHERE a.customer_id=:customer_id
        ORDER BY a.appointment_date DESC
        """,
        {"customer_id": request.session["customer_id"]},
    )
    return templates.TemplateResponse(
        "customer/booking/my_appointments.html",
        {
            "request": request,
            "title": "Lich hen cua toi - UIT Petcare",
            "flash": pop_flash(request),
            "appointments": appointments,
            "session": request.session,
        },
    )
