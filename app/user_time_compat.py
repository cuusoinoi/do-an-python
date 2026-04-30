from datetime import datetime

from app.db import execute


def insert_user_with_time_compat(username: str, password: str, fullname: str, role: str, now: datetime | None = None) -> None:
    created_time = now or datetime.now()
    try:
        execute(
            """
            INSERT INTO users (username, password, fullname, role, created_at)
            VALUES (:username, :password, :fullname, :role, :created_at)
            """,
            {
                "username": username,
                "password": password,
                "fullname": fullname,
                "role": role,
                "created_at": created_time,
            },
        )
    except Exception:
        execute(
            """
            INSERT INTO users (username, password, fullname, role, create_at)
            VALUES (:username, :password, :fullname, :role, :create_at)
            """,
            {
                "username": username,
                "password": password,
                "fullname": fullname,
                "role": role,
                "create_at": created_time,
            },
        )
