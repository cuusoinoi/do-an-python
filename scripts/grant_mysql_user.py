import pymysql


def main() -> None:
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE USER IF NOT EXISTS 'mysql'@'%' IDENTIFIED BY '123456'")
            cur.execute("ALTER USER 'mysql'@'%' IDENTIFIED BY '123456'")
            cur.execute("GRANT ALL PRIVILEGES ON *.* TO 'mysql'@'%' WITH GRANT OPTION")
            cur.execute("FLUSH PRIVILEGES")
        print("mysql user granted")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
