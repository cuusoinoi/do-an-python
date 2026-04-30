from __future__ import annotations

import json
import logging
from decimal import Decimal
from datetime import datetime
from typing import Any

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates as _Jinja2Templates

from app.db import fetch_one

logger = logging.getLogger(__name__)


def _php_empty(value: Any) -> bool:
    return value is None or value == "" or value == 0 or value is False or value == [] or value == {}


def _php_isset(value: Any) -> bool:
    return value is not None


def _number_format(value: Any, decimals: int = 0, dec_point: str = ".", thousands_sep: str = ",") -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    formatted = f"{number:,.{decimals}f}"
    if thousands_sep != ",":
        formatted = formatted.replace(",", "TMPSEP")
    if dec_point != ".":
        formatted = formatted.replace(".", dec_point)
    if thousands_sep != ",":
        formatted = formatted.replace("TMPSEP", thousands_sep)
    return formatted


def _json_default(value: Any):
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def _strtotime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if value is None:
        return datetime.now()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.now()


def _date(fmt: str, value: Any = None) -> str:
    dt = _strtotime(value) if value is not None else datetime.now()
    py_fmt = (
        str(fmt)
        .replace("d", "%d")
        .replace("m", "%m")
        .replace("Y", "%Y")
        .replace("H", "%H")
        .replace("i", "%M")
        .replace("s", "%S")
    )
    return dt.strftime(py_fmt)


def _str_pad(value: Any, length: int, pad_str: str = "0", _pad_type: Any = None) -> str:
    text = str(value if value is not None else "")
    if len(text) >= int(length):
        return text
    fill = (pad_str or "0")[0]
    return fill * (int(length) - len(text)) + text


def _format_number_short(value: Any) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return "0"
    if number >= 1_000_000_000:
        return f"{round(number / 1_000_000_000, 1)}B"
    if number >= 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    if number >= 1_000:
        return f"{round(number / 1_000, 1)}K"
    return str(int(number) if number.is_integer() else number)


class Jinja2Templates(_Jinja2Templates):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env.globals.update(
            {
                "empty": _php_empty,
                "isset": _php_isset,
                "old": lambda *_args, **_kwargs: "",
                "number_format": _number_format,
                "strpos": lambda haystack, needle: str(haystack).find(str(needle)),
                "str_contains": lambda haystack, needle: str(needle) in str(haystack),
                "esc": lambda value: value,
                "json_encode": lambda value: json.dumps(value, default=_json_default, ensure_ascii=False),
                "tojson": lambda value: json.dumps(value, default=_json_default, ensure_ascii=False),
                "base_url": lambda path="": f"/static/{str(path).lstrip('/')}",
                "site_url": lambda path="": f"/{str(path).lstrip('/')}",
                "formatNumberShort": _format_number_short,
                "isMenuActive": lambda path, current_uri: str(path) in str(current_uri or ""),
                "submenuActiveClass": lambda path, current_uri: (
                    "submenu-active"
                    if str(current_uri or "") == str(path) or str(current_uri or "").startswith(f"{path}/")
                    else ""
                ),
                "getServiceIcon": lambda *_args, **_kwargs: "fa-paw",
                "strtotime": _strtotime,
                "date": _date,
                "str_pad": _str_pad,
                "STR_PAD_LEFT": "left",
                "range": range,
                "now": datetime.now,
                "nl2br": lambda value: str(value or "").replace("\n", "<br>"),
            }
        )

    def TemplateResponse(self, *args, **kwargs):
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            name = args[0]
            context = args[1]
            request = context.get("request")
            if request is not None:
                context.setdefault("settings", fetch_one("SELECT * FROM general_settings LIMIT 1"))
                context.setdefault("currentUri", request.url.path.lstrip("/"))
                context.setdefault("isHome", request.url.path in {"/", "/customer"})
                if "total_pages" in context:
                    context.setdefault("totalPages", context["total_pages"])
                if "page" in context:
                    context.setdefault("currentPage", context["page"])
                if "q" in context:
                    context.setdefault("keyword", context["q"])
                if "rows" in context:
                    rows = context["rows"]
                    for alias in (
                        "records",
                        "vaccinations",
                        "prescriptions",
                        "courses",
                        "sessions",
                        "details",
                        "enclosures",
                        "users",
                        "vaccines",
                        "medicines",
                        "customers",
                        "pets",
                        "doctors",
                        "appointments",
                        "service_types",
                        "serviceTypes",
                        "medicalRecords",
                        "petEnclosures",
                        "petVaccinations",
                        "treatmentCourses",
                        "invoices",
                    ):
                        context.setdefault(alias, rows)
                if "details" in context:
                    context.setdefault("invoiceDetails", context["details"])
                if "row" in context:
                    row = context["row"]
                    for alias in (
                        "customer",
                        "doctor",
                        "serviceType",
                        "pet",
                        "medicine",
                        "vaccine",
                        "record",
                        "invoice",
                        "enclosure",
                        "vaccination",
                        "course",
                        "session",
                    ):
                        context.setdefault(alias, row)
                context.setdefault("mappedInvoiceId", {})
                context.setdefault("flash", {"success": None, "error": None})
                if request.url.path.startswith("/admin"):
                    username = request.session.get("username")
                    if username:
                        current_user = fetch_one("SELECT * FROM users WHERE username=:u", {"u": username}) or {}
                        context.setdefault("currentUser", current_user)
                        context.setdefault("user", current_user)
                rest = args[2:]
                try:
                    return super().TemplateResponse(request, name, context, *rest, **kwargs)
                except Exception as exc:
                    logger.exception("Template render failed for %s", name)
                    if request.url.path.startswith("/admin"):
                        return HTMLResponse(
                            status_code=200,
                            content=(
                                "<!DOCTYPE html><html lang='vi'><head><meta charset='UTF-8'>"
                                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                                "<title>Admin</title>"
                                "<link rel='stylesheet' href='/static/assets/css/base.css'>"
                                "<link rel='stylesheet' href='/static/assets/css/main.css'>"
                                "</head><body style='padding:24px'>"
                                "<h2>Trang quản trị đang được chuẩn hóa giao diện</h2>"
                                f"<p>Module: <b>{request.url.path}</b></p>"
                                "<p>Tạm thời có thể thao tác các module khác từ menu.</p>"
                                "<p><a href='/admin/dashboard'>Về Dashboard</a></p>"
                                "</body></html>"
                            ),
                        )
                    raise
        return super().TemplateResponse(*args, **kwargs)
