# UIT Petcare Python

Backend and web application for UIT Petcare using FastAPI and MySQL.

## Requirements

- Python 3.11+
- MySQL at `localhost:3306`
- MySQL account:
  - username: `mysql`
  - password: `123456`

## Setup

1. Create and activate virtual environment.
2. Install dependencies:

   `python -m pip install -r requirements.txt`

3. Copy `.env.example` to `.env`.
4. Run database initialization and server:

   `python run_dev.py`

5. Run database smoke check (optional):

   `python -m scripts.smoke_check`

6. Run route smoke check (optional):

   `python -m scripts.route_smoke`

## Main URLs

- Customer: `http://127.0.0.1:8000/customer`
- Customer login: `http://127.0.0.1:8000/customer/login`
- Admin login: `http://127.0.0.1:8000/admin`
- Admin dashboard: `http://127.0.0.1:8000/admin/dashboard`
- Admin settings: `http://127.0.0.1:8000/admin/settings`

## Credentials

- Admin:
  - username: `admin`
  - password: `123456`
- Customer:
  - phone: `0901234567`
  - OTP: `123456`
