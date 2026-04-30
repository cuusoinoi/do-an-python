from app.db import fetch_one


def check_database() -> list[str]:
    required_tables = [
        "users",
        "customers",
        "pets",
        "appointments",
        "medical_records",
        "invoices",
        "invoice_details",
        "pet_enclosures",
        "service_types",
        "medicines",
        "vaccines",
        "pet_vaccinations",
        "treatment_courses",
        "treatment_sessions",
        "diagnoses",
        "prescriptions",
        "general_settings",
    ]
    results: list[str] = []
    for table in required_tables:
        row = fetch_one(f"SELECT COUNT(*) AS total FROM {table}")
        total = row["total"] if row else 0
        results.append(f"{table}: {total}")
    return results


def main() -> None:
    print("Database smoke check")
    print("-" * 24)
    for line in check_database():
        print(line)
    admin_user = fetch_one("SELECT username FROM users WHERE username='admin' LIMIT 1")
    if admin_user:
        print("admin_user: ok")
    else:
        print("admin_user: missing")
    sample_customer = fetch_one(
        "SELECT customer_phone_number FROM customers WHERE customer_phone_number='0901234567' LIMIT 1"
    )
    if sample_customer:
        print("customer_sample: ok")
    else:
        print("customer_sample: missing")


if __name__ == "__main__":
    main()
