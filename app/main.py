from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import admin_auth, admin_core, booking, customer_auth, customer_dashboard, public

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, max_age=60 * 60 * 8)

app.include_router(public.router)
app.include_router(customer_auth.router)
app.include_router(customer_dashboard.router)
app.include_router(booking.router)
app.include_router(admin_auth.router)
app.include_router(admin_core.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
