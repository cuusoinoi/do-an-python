import subprocess
from pathlib import Path

import pymysql

from app.config import settings


def _split_sql(sql_text: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
    if buffer:
        statements.append("\n".join(buffer).strip())
    return statements


def _database_ready() -> bool:
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'users'")
            users_table = cur.fetchone()
            if not users_table:
                return False
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            return count > 0
    finally:
        conn.close()


def _import_with_mysql_client(dump_path: Path) -> bool:
    cmd = [
        "mysql",
        f"-h{settings.db_host}",
        f"-P{settings.db_port}",
        f"-u{settings.db_user}",
        f"-p{settings.db_password}",
    ]
    try:
        with dump_path.open("r", encoding="utf-8") as f:
            subprocess.run(cmd, stdin=f, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _import_with_pymysql(dump_path: Path) -> None:
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        sql_text = dump_path.read_text(encoding="utf-8")
        statements = _split_sql(sql_text)
        with conn.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
    finally:
        conn.close()


def main() -> None:
    dump_path = settings.resolved_dump_path
    if not dump_path.exists():
        raise FileNotFoundError(f"SQL dump not found: {dump_path}")
    if _database_ready():
        print("Database already initialized, skip import.")
        return
    if _import_with_mysql_client(dump_path):
        print("Database imported via mysql client.")
        return
    _import_with_pymysql(dump_path)
    print("Database imported via PyMySQL.")


if __name__ == "__main__":
    main()
