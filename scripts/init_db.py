import subprocess
import sys
from pathlib import Path

import pymysql
import pymysql.err

from app.config import settings


def _print_mysql_connection_help(exc: BaseException) -> None:
    msg = (
        "Khong ket noi duoc MySQL.\n"
        f"  Dang thu: {settings.db_host}:{settings.db_port} (user: {settings.db_user}, database: {settings.db_name})\n\n"
        "Hay kiem tra:\n"
        "  - MySQL da duoc cai va dang chay (Windows: Services -> MySQL, hoac mo XAMPP/WAMP va Start MySQL).\n"
        "  - Port trong .env dung voi cau hinh may (mac dinh 3306).\n"
        "  - User/password trong .env dung voi tai khoan MySQL tren may ban.\n\n"
        f"Loi ky thuat: {exc}"
    )
    print(msg, file=sys.stderr)


def _connect_mysql(*, database: str | None = None):
    kwargs: dict = {
        "host": settings.db_host,
        "port": settings.db_port,
        "user": settings.db_user,
        "password": settings.db_password,
        "charset": "utf8mb4",
        "connect_timeout": 8,
    }
    if database is not None:
        kwargs["database"] = database
    try:
        return pymysql.connect(**kwargs)
    except pymysql.err.OperationalError as e:
        code = e.args[0] if e.args else None
        if code == 1049:
            raise
        if code in (2002, 2003, 1045):
            _print_mysql_connection_help(e)
            raise SystemExit(1) from e
        raise


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
    try:
        conn = _connect_mysql(database=settings.db_name)
    except pymysql.err.OperationalError as e:
        if e.args and e.args[0] == 1049:
            return False
        raise
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
    conn = _connect_mysql(database=None)
    conn.autocommit(True)
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
