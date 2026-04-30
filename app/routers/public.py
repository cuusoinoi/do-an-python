from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.templating import Jinja2Templates

from app.db import fetch_all, fetch_one
from app.session import pop_flash

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
def root_redirect():
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/customer", status_code=302)


@router.get("/customer", response_class=HTMLResponse)
def customer_home(request: Request):
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    services = fetch_all("SELECT * FROM service_types ORDER BY service_type_id DESC")
    doctors = fetch_all("SELECT * FROM doctors ORDER BY doctor_id DESC")
    return templates.TemplateResponse(
        "customer/home.html",
        {
            "request": request,
            "title": "UIT Petcare - Phong kham thu y va spa thu cung",
            "settings": settings,
            "services": services,
            "doctors": doctors,
            "flash": pop_flash(request),
            "session": request.session,
        },
    )


@router.get("/customer/services", response_class=HTMLResponse)
def customer_services(request: Request):
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    services = fetch_all("SELECT * FROM service_types ORDER BY service_type_id DESC")
    return templates.TemplateResponse(
        "customer/services.html",
        {
            "request": request,
            "title": "Dich vu - UIT Petcare",
            "settings": settings,
            "services": services,
            "flash": pop_flash(request),
            "session": request.session,
        },
    )


@router.get("/customer/contact", response_class=HTMLResponse)
def customer_contact(request: Request):
    settings = fetch_one("SELECT * FROM general_settings LIMIT 1")
    return templates.TemplateResponse(
        "customer/contact.html",
        {
            "request": request,
            "title": "Lien he - UIT Petcare",
            "settings": settings,
            "flash": pop_flash(request),
            "session": request.session,
        },
    )


@router.get("/customer/api/home-data", response_class=JSONResponse)
def customer_home_data():
    services = fetch_all("SELECT service_type_id FROM service_types")
    doctors = fetch_all("SELECT doctor_id FROM doctors")
    return {
        "success": True,
        "data": {
            "totalServices": len(services),
            "totalDoctors": len(doctors),
        },
    }
