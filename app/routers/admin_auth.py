from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import Jinja2Templates
from datetime import date, datetime, timedelta

from app.db import fetch_all, fetch_one
from app.security import verify_password
from app.session import CUSTOMER_HOME_PATH, pop_flash, redirect_if_customer_session, set_flash

router = APIRouter(prefix="/admin", tags=["admin-auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def admin_login_page(request: Request):
    r = redirect_if_customer_session(request)
    if r:
        return r
    if request.session.get("username") and request.session.get("role") in {"admin", "staff"}:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(
        "admin/login.html",
        {
            "request": request,
            "title": "Dang nhap - UIT Petcare",
            "flash": pop_flash(request),
        },
    )


@router.post("/login")
def admin_login(request: Request, username: str = Form(""), password: str = Form("")):
    if not username or not password:
        set_flash(request, error="Vui long nhap day du thong tin")
        return RedirectResponse(url="/admin", status_code=302)
    user = fetch_one("SELECT * FROM users WHERE username = :username LIMIT 1", {"username": username})
    if not user or not verify_password(password, user.get("password")):
        set_flash(request, error="Sai ten dang nhap hoac mat khau")
        return RedirectResponse(url="/admin", status_code=302)
    if user.get("role") == "customer":
        customer = fetch_one(
            "SELECT customer_id FROM customers WHERE customer_phone_number = :phone LIMIT 1",
            {"phone": user["username"]},
        )
        request.session["user_id"] = user["id"]
        request.session["username"] = user["username"]
        request.session["fullname"] = user["fullname"]
        request.session["role"] = "customer"
        if customer:
            request.session["customer_id"] = customer["customer_id"]
        else:
            request.session.pop("customer_id", None)
        set_flash(request, success="Tai khoan khach hang - chuyen den khu vuc khach")
        return RedirectResponse(url=CUSTOMER_HOME_PATH, status_code=302)
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["fullname"] = user["fullname"]
    request.session["role"] = user["role"]
    request.session.pop("customer_id", None)
    set_flash(request, success="Dang nhap thanh cong")
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    r = redirect_if_customer_session(request)
    if r:
        return r
    if request.session.get("role") not in {"admin", "staff"}:
        set_flash(request, error="Vui long dang nhap")
        return RedirectResponse(url="/admin", status_code=302)
    def _percent_change(current: float, previous: float) -> float:
        if previous <= 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0

    today = date.today()
    start_7_days = today - timedelta(days=6)
    start_current_30 = today - timedelta(days=29)
    start_previous_30 = today - timedelta(days=59)
    end_previous_30 = today - timedelta(days=30)

    customer_count = fetch_one("SELECT COUNT(*) AS total FROM customers")["total"]
    pet_count = fetch_one("SELECT COUNT(*) AS total FROM pets")["total"]
    medical_record_count = fetch_one("SELECT COUNT(*) AS total FROM medical_records")["total"]
    pet_enclosure_count = fetch_one("SELECT COUNT(*) AS total FROM pet_enclosures")["total"]
    invoice_revenue = float(fetch_one("SELECT COALESCE(SUM(total_amount), 0) AS total FROM invoices")["total"] or 0)

    medical_current = fetch_one(
        "SELECT COUNT(*) AS total FROM medical_records WHERE DATE(medical_record_visit_date) >= :d",
        {"d": start_current_30},
    )["total"]
    medical_previous = fetch_one(
        "SELECT COUNT(*) AS total FROM medical_records WHERE DATE(medical_record_visit_date) BETWEEN :d1 AND :d2",
        {"d1": start_previous_30, "d2": end_previous_30},
    )["total"]
    enclosure_current = fetch_one(
        "SELECT COUNT(*) AS total FROM pet_enclosures WHERE DATE(check_in_date) >= :d",
        {"d": start_current_30},
    )["total"]
    enclosure_previous = fetch_one(
        "SELECT COUNT(*) AS total FROM pet_enclosures WHERE DATE(check_in_date) BETWEEN :d1 AND :d2",
        {"d1": start_previous_30, "d2": end_previous_30},
    )["total"]
    revenue_current = float(
        fetch_one("SELECT COALESCE(SUM(total_amount), 0) AS total FROM invoices WHERE DATE(invoice_date) >= :d", {"d": start_current_30})["total"]
        or 0
    )
    revenue_previous = float(
        fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) AS total FROM invoices WHERE DATE(invoice_date) BETWEEN :d1 AND :d2",
            {"d1": start_previous_30, "d2": end_previous_30},
        )["total"]
        or 0
    )

    medical_percent_change = _percent_change(float(medical_current), float(medical_previous))
    enclosure_percent_change = _percent_change(float(enclosure_current), float(enclosure_previous))
    revenue_percent_change = _percent_change(revenue_current, revenue_previous)

    date_rows = fetch_all(
        """
        SELECT DATE(medical_record_visit_date) AS d, COUNT(*) AS total
        FROM medical_records
        WHERE DATE(medical_record_visit_date) >= :start_date
        GROUP BY DATE(medical_record_visit_date)
        """,
        {"start_date": start_7_days},
    )
    date_map = {row["d"].strftime("%Y-%m-%d"): int(row["total"]) for row in date_rows}
    dates = []
    counts = []
    for i in range(7):
        d = start_7_days + timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        dates.append(d.strftime("%d/%m"))
        counts.append(date_map.get(key, 0))

    checkin_rows = fetch_all(
        """
        SELECT DATE(check_in_date) AS d, COUNT(*) AS total
        FROM pet_enclosures
        WHERE DATE(check_in_date) >= :start_date
        GROUP BY DATE(check_in_date)
        """,
        {"start_date": start_7_days},
    )
    checkout_rows = fetch_all(
        """
        SELECT DATE(check_out_date) AS d, COUNT(*) AS total
        FROM pet_enclosures
        WHERE check_out_date IS NOT NULL AND DATE(check_out_date) >= :start_date
        GROUP BY DATE(check_out_date)
        """,
        {"start_date": start_7_days},
    )
    checkin_map = {row["d"].strftime("%d/%m"): int(row["total"]) for row in checkin_rows}
    checkout_map = {row["d"].strftime("%d/%m"): int(row["total"]) for row in checkout_rows}
    checkin_checkout_data = {}
    for label in dates:
        checkin_checkout_data[label] = {"checkin": checkin_map.get(label, 0), "checkout": checkout_map.get(label, 0)}

    monthly_rows = fetch_all(
        """
        SELECT DATE_FORMAT(invoice_date, '%Y-%m') AS ym, COALESCE(SUM(total_amount), 0) AS total
        FROM invoices
        WHERE invoice_date >= :from_date
        GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
        ORDER BY ym ASC
        """,
        {"from_date": (today.replace(day=1) - timedelta(days=330))},
    )
    monthly_revenue_stats = {row["ym"]: float(row["total"] or 0) for row in monthly_rows}
    cur = today.replace(day=1)
    months = []
    for _ in range(12):
        months.append(cur.strftime("%Y-%m"))
        cur = (cur.replace(day=1) - timedelta(days=1)).replace(day=1)
    months.reverse()
    monthly_revenue_stats = {m: monthly_revenue_stats.get(m, 0.0) for m in months}

    service_rows = fetch_all(
        """
        SELECT COALESCE(st.service_name, 'Khac') AS service_name, COALESCE(SUM(d.total_price), 0) AS total
        FROM invoice_details d
        LEFT JOIN service_types st ON st.service_type_id = d.service_type_id
        GROUP BY COALESCE(st.service_name, 'Khac')
        ORDER BY total DESC
        LIMIT 12
        """
    )
    service_names = [row["service_name"] for row in service_rows]
    service_revenues = [float(row["total"] or 0) for row in service_rows]

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "title": "Dashboard - UIT Petcare",
            "flash": pop_flash(request),
            "session": request.session,
            "customerCount": customer_count,
            "petCount": pet_count,
            "medicalRecordCount": medical_record_count,
            "petEnclosureCount": pet_enclosure_count,
            "invoiceRevenue": invoice_revenue,
            "medicalPercentChange": medical_percent_change,
            "enclosurePercentChange": enclosure_percent_change,
            "revenuePercentChange": revenue_percent_change,
            "dates": dates,
            "counts": counts,
            "checkinCheckoutData": checkin_checkout_data,
            "monthlyRevenueStats": monthly_revenue_stats,
            "serviceNames": service_names,
            "serviceRevenues": service_revenues,
        },
    )
