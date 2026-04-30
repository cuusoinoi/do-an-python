from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.templating import Jinja2Templates
from datetime import datetime

from app.db import execute, fetch_all, fetch_one
from app.session import pop_flash, set_flash

router = APIRouter(prefix="/customer/dashboard", tags=["customer-dashboard"])
templates = Jinja2Templates(directory="templates")


def _guard_customer(request: Request):
    if request.session.get("role") != "customer":
        set_flash(request, error="Vui long dang nhap")
        return RedirectResponse(url="/customer/login", status_code=302)
    return None


@router.get("/", response_class=HTMLResponse)
def dashboard_index(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer_id = request.session["customer_id"]
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": customer_id})
    pets = fetch_all("SELECT * FROM pets WHERE customer_id=:id ORDER BY pet_id DESC", {"id": customer_id})
    total_appointments = fetch_one(
        "SELECT COUNT(*) AS total FROM appointments WHERE customer_id=:id", {"id": customer_id}
    )["total"]
    total_invoices = fetch_one("SELECT COUNT(*) AS total FROM invoices WHERE customer_id=:id", {"id": customer_id})[
        "total"
    ]
    upcoming_appointments = fetch_all(
        """
        SELECT a.*, p.pet_name
        FROM appointments a
        LEFT JOIN pets p ON p.pet_id = a.pet_id
        WHERE a.customer_id=:id
          AND a.appointment_date >= :now
          AND a.status IN ('pending', 'confirmed')
        ORDER BY a.appointment_date ASC
        LIMIT 5
        """,
        {"id": customer_id, "now": datetime.now()},
    )
    return templates.TemplateResponse(
        "customer/dashboard/index.html",
        {
            "request": request,
            "title": "Dashboard - UIT Petcare",
            "flash": pop_flash(request),
            "customer": customer,
            "pets": pets,
            "total_pets": len(pets),
            "total_appointments": total_appointments,
            "total_invoices": total_invoices,
            "upcoming_appointments": upcoming_appointments,
            # Keep camelCase keys for parity with original PHP views/scripts.
            "totalPets": len(pets),
            "totalAppointments": total_appointments,
            "totalInvoices": total_invoices,
            "upcomingAppointments": upcoming_appointments,
            "session": request.session,
        },
    )


@router.get("/api/data", response_class=JSONResponse)
def dashboard_data(request: Request):
    guard = _guard_customer(request)
    if guard:
        return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})
    customer_id = request.session["customer_id"]
    total_pets = fetch_one("SELECT COUNT(*) AS total FROM pets WHERE customer_id=:id", {"id": customer_id})["total"]
    total_appointments = fetch_one(
        "SELECT COUNT(*) AS total FROM appointments WHERE customer_id=:id", {"id": customer_id}
    )["total"]
    total_invoices = fetch_one("SELECT COUNT(*) AS total FROM invoices WHERE customer_id=:id", {"id": customer_id})[
        "total"
    ]
    upcoming_rows = fetch_all(
        """
        SELECT a.*, p.pet_name
        FROM appointments a
        LEFT JOIN pets p ON p.pet_id = a.pet_id
        WHERE a.customer_id=:id
          AND a.appointment_date >= :now
          AND a.status IN ('pending', 'confirmed')
        ORDER BY a.appointment_date ASC
        LIMIT 5
        """,
        {"id": customer_id, "now": datetime.now()},
    )
    upcoming_appointments = []
    for row in upcoming_rows:
        status = row.get("status") or "pending"
        if status == "confirmed":
            status_bg = "#d4edda"
            status_color = "#155724"
            status_text = "Đã xác nhận"
        else:
            status_bg = "#fff3cd"
            status_color = "#856404"
            status_text = "Chờ xác nhận"
        upcoming_appointments.append(
            {
                "appointment_date": row.get("appointment_date").strftime("%d/%m/%Y %H:%M")
                if row.get("appointment_date")
                else "",
                "pet_name": row.get("pet_name") or "N/A",
                "appointment_type": row.get("appointment_type") or "",
                "status": status,
                "status_bg": status_bg,
                "status_color": status_color,
                "status_text": status_text,
            }
        )
    return {
        "success": True,
        "data": {
            "totalPets": total_pets,
            "totalAppointments": total_appointments,
            "totalInvoices": total_invoices,
            "upcomingAppointments": upcoming_appointments,
        },
    }


@router.get("/pets", response_class=HTMLResponse)
def pets_page(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    pets = fetch_all(
        "SELECT * FROM pets WHERE customer_id=:customer_id ORDER BY pet_id DESC",
        {"customer_id": request.session["customer_id"]},
    )
    return templates.TemplateResponse(
        "customer/dashboard/pets.html",
        {
            "request": request,
            "title": "Thu cung cua toi - UIT Petcare",
            "flash": pop_flash(request),
            "pets": pets,
            "session": request.session,
        },
    )


@router.get("/pets/add", response_class=HTMLResponse)
def add_pet_page(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    return templates.TemplateResponse(
        "customer/dashboard/add_pet.html",
        {"request": request, "title": "Them thu cung - UIT Petcare", "flash": pop_flash(request), "session": request.session},
    )


@router.post("/pets/add")
def add_pet(
    request: Request,
    pet_name: str = Form(""),
    pet_species: str = Form(""),
    pet_gender: str = Form(""),
    pet_dob: str = Form(""),
    pet_weight: str = Form(""),
):
    guard = _guard_customer(request)
    if guard:
        return guard
    if not pet_name:
        set_flash(request, error="Ten thu cung la bat buoc")
        return RedirectResponse(url="/customer/dashboard/pets/add", status_code=302)
    execute(
        """
        INSERT INTO pets (customer_id, pet_name, pet_species, pet_gender, pet_dob, pet_weight)
        VALUES (:customer_id, :pet_name, :pet_species, :pet_gender, :pet_dob, :pet_weight)
        """,
        {
            "customer_id": request.session["customer_id"],
            "pet_name": pet_name,
            "pet_species": pet_species or None,
            "pet_gender": pet_gender or None,
            "pet_dob": pet_dob or None,
            "pet_weight": pet_weight or None,
        },
    )
    set_flash(request, success="Them thu cung thanh cong")
    return RedirectResponse(url="/customer/dashboard/pets", status_code=302)


@router.get("/invoices", response_class=HTMLResponse)
def invoices_page(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    invoices = fetch_all(
        """
        SELECT i.*, p.pet_name
        FROM invoices i
        JOIN pets p ON p.pet_id = i.pet_id
        WHERE i.customer_id=:customer_id
        ORDER BY i.invoice_date DESC
        """,
        {"customer_id": request.session["customer_id"]},
    )
    return templates.TemplateResponse(
        "customer/dashboard/invoices.html",
        {"request": request, "title": "Hoa don - UIT Petcare", "flash": pop_flash(request), "invoices": invoices, "session": request.session},
    )


@router.get("/invoices/view/{invoice_id}", response_class=HTMLResponse)
def invoice_detail(request: Request, invoice_id: int):
    guard = _guard_customer(request)
    if guard:
        return guard
    invoice = fetch_one(
        """
        SELECT i.*, p.pet_name, p.pet_species, c.customer_name, c.customer_phone_number, c.customer_address
        FROM invoices i
        JOIN pets p ON p.pet_id = i.pet_id
        JOIN customers c ON c.customer_id = i.customer_id
        WHERE i.invoice_id=:invoice_id AND i.customer_id=:customer_id
        LIMIT 1
        """,
        {"invoice_id": invoice_id, "customer_id": request.session["customer_id"]},
    )
    if not invoice:
        set_flash(request, error="Khong tim thay hoa don hoac ban khong co quyen xem")
        return RedirectResponse(url="/customer/dashboard/invoices", status_code=302)
    details = fetch_all(
        """
        SELECT d.*, s.service_name
        FROM invoice_details d
        LEFT JOIN service_types s ON s.service_type_id = d.service_type_id
        WHERE d.invoice_id=:invoice_id
        """,
        {"invoice_id": invoice_id},
    )
    return templates.TemplateResponse(
        "customer/dashboard/view_invoice.html",
        {
            "request": request,
            "title": "Chi tiet hoa don - UIT Petcare",
            "flash": pop_flash(request),
            "invoice": invoice,
            "details": details,
            "session": request.session,
        },
    )


@router.get("/medical-records", response_class=HTMLResponse)
def medical_records_page(request: Request, pet_id: int | None = Query(default=None)):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer_id = request.session["customer_id"]
    pets = fetch_all("SELECT * FROM pets WHERE customer_id=:id ORDER BY pet_id DESC", {"id": customer_id})
    if pet_id:
        records = fetch_all(
            """
            SELECT mr.*, p.pet_name, d.doctor_name
            FROM medical_records mr
            LEFT JOIN pets p ON p.pet_id = mr.pet_id
            LEFT JOIN doctors d ON d.doctor_id = mr.doctor_id
            WHERE mr.pet_id = :pet_id
            ORDER BY mr.medical_record_visit_date DESC
            """,
            {"pet_id": pet_id},
        )
    else:
        records = fetch_all(
            """
            SELECT mr.*, p.pet_name, d.doctor_name
            FROM medical_records mr
            LEFT JOIN pets p ON p.pet_id = mr.pet_id
            LEFT JOIN doctors d ON d.doctor_id = mr.doctor_id
            WHERE mr.customer_id=:customer_id
            ORDER BY mr.medical_record_visit_date DESC
            """,
            {"customer_id": customer_id},
        )
    return templates.TemplateResponse(
        "customer/dashboard/medical_records.html",
        {
            "request": request,
            "title": "Lich su kham benh - UIT Petcare",
            "flash": pop_flash(request),
            "records": records,
            "pets": pets,
            "selected_pet_id": pet_id,
            "session": request.session,
        },
    )


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer = fetch_one("SELECT * FROM customers WHERE customer_id=:id", {"id": request.session["customer_id"]})
    return templates.TemplateResponse(
        "customer/dashboard/profile.html",
        {
            "request": request,
            "title": "Thong tin ca nhan - UIT Petcare",
            "flash": pop_flash(request),
            "customer": customer,
            "session": request.session,
        },
    )


@router.post("/profile")
def profile_update(
    request: Request,
    customer_name: str = Form(""),
    customer_email: str = Form(""),
    customer_address: str = Form(""),
):
    guard = _guard_customer(request)
    if guard:
        return guard
    execute(
        """
        UPDATE customers
        SET customer_name=:name, customer_email=:email, customer_address=:address
        WHERE customer_id=:id
        """,
        {"name": customer_name, "email": customer_email or None, "address": customer_address or None, "id": request.session["customer_id"]},
    )
    request.session["fullname"] = customer_name or request.session.get("fullname")
    set_flash(request, success="Cap nhat thong tin thanh cong")
    return RedirectResponse(url="/customer/dashboard/profile", status_code=302)


@router.get("/prescriptions", response_class=HTMLResponse)
def prescriptions_page(request: Request, pet_id: int | None = Query(default=None)):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer_id = request.session["customer_id"]
    pets = fetch_all("SELECT * FROM pets WHERE customer_id=:id ORDER BY pet_id DESC", {"id": customer_id})
    if pet_id:
        rows = fetch_all(
            """
            SELECT pr.*, m.medicine_name, m.medicine_route, ts.treatment_session_datetime, p.pet_name
            FROM prescriptions pr
            JOIN medicines m ON m.medicine_id = pr.medicine_id
            JOIN treatment_sessions ts ON ts.treatment_session_id = pr.treatment_session_id
            JOIN treatment_courses tc ON tc.treatment_course_id = ts.treatment_course_id
            JOIN pets p ON p.pet_id = tc.pet_id
            WHERE tc.pet_id=:pet_id
            ORDER BY ts.treatment_session_datetime DESC
            """,
            {"pet_id": pet_id},
        )
    else:
        rows = fetch_all(
            """
            SELECT pr.*, m.medicine_name, m.medicine_route, ts.treatment_session_datetime, p.pet_name
            FROM prescriptions pr
            JOIN medicines m ON m.medicine_id = pr.medicine_id
            JOIN treatment_sessions ts ON ts.treatment_session_id = pr.treatment_session_id
            JOIN treatment_courses tc ON tc.treatment_course_id = ts.treatment_course_id
            JOIN pets p ON p.pet_id = tc.pet_id
            WHERE tc.customer_id=:customer_id
            ORDER BY ts.treatment_session_datetime DESC
            """,
            {"customer_id": customer_id},
        )
    return templates.TemplateResponse(
        "customer/dashboard/prescriptions.html",
        {
            "request": request,
            "title": "Don thuoc - UIT Petcare",
            "flash": pop_flash(request),
            "rows": rows,
            "pets": pets,
            "selected_pet_id": pet_id,
            "session": request.session,
        },
    )


@router.get("/vaccinations", response_class=HTMLResponse)
def vaccinations_page(request: Request, pet_id: int | None = Query(default=None)):
    guard = _guard_customer(request)
    if guard:
        return guard
    customer_id = request.session["customer_id"]
    pets = fetch_all("SELECT * FROM pets WHERE customer_id=:id ORDER BY pet_id DESC", {"id": customer_id})
    if pet_id:
        rows = fetch_all(
            """
            SELECT pv.*, v.vaccine_name, d.doctor_name
            FROM pet_vaccinations pv
            JOIN vaccines v ON v.vaccine_id = pv.vaccine_id
            LEFT JOIN doctors d ON d.doctor_id = pv.doctor_id
            WHERE pv.pet_id=:pet_id
            ORDER BY pv.vaccination_date DESC
            """,
            {"pet_id": pet_id},
        )
    else:
        rows = fetch_all(
            """
            SELECT pv.*, v.vaccine_name, d.doctor_name, p.pet_name
            FROM pet_vaccinations pv
            JOIN vaccines v ON v.vaccine_id = pv.vaccine_id
            LEFT JOIN doctors d ON d.doctor_id = pv.doctor_id
            LEFT JOIN pets p ON p.pet_id = pv.pet_id
            WHERE pv.customer_id=:customer_id
            ORDER BY pv.vaccination_date DESC
            """,
            {"customer_id": customer_id},
        )
    return templates.TemplateResponse(
        "customer/dashboard/vaccinations.html",
        {
            "request": request,
            "title": "Lich tiem chung - UIT Petcare",
            "flash": pop_flash(request),
            "rows": rows,
            "pets": pets,
            "selected_pet_id": pet_id,
            "session": request.session,
        },
    )
