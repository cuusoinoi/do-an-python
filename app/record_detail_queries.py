from app.db import execute, fetch_all


def load_record_services(record_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT service_type_id, quantity, unit_price, total_price
        FROM medical_record_services
        WHERE medical_record_id=:id
        ORDER BY record_service_id ASC
        """,
        {"id": record_id},
    )


def save_record_services(record_id: int, service_ids: list[str], quantities: list[str], unit_prices: list[str], total_prices: list[str]) -> None:
    execute("DELETE FROM medical_record_services WHERE medical_record_id=:id", {"id": record_id})
    for i, service_id in enumerate(service_ids):
        if not service_id:
            continue
        execute(
            """
            INSERT INTO medical_record_services (medical_record_id, service_type_id, quantity, unit_price, total_price)
            VALUES (:medical_record_id, :service_type_id, :quantity, :unit_price, :total_price)
            """,
            {
                "medical_record_id": record_id,
                "service_type_id": int(service_id),
                "quantity": int(quantities[i]) if i < len(quantities) and quantities[i] else 1,
                "unit_price": int(float(unit_prices[i])) if i < len(unit_prices) and unit_prices[i] else 0,
                "total_price": int(float(total_prices[i])) if i < len(total_prices) and total_prices[i] else 0,
            },
        )


def load_record_medicines(record_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT medicine_id, quantity, unit_price, total_price
        FROM medical_record_medicines
        WHERE medical_record_id=:id
        ORDER BY record_medicine_id ASC
        """,
        {"id": record_id},
    )


def save_record_medicines(record_id: int, medicine_ids: list[str], quantities: list[str], unit_prices: list[str], total_prices: list[str]) -> None:
    execute("DELETE FROM medical_record_medicines WHERE medical_record_id=:id", {"id": record_id})
    for i, medicine_id in enumerate(medicine_ids):
        if not medicine_id:
            continue
        execute(
            """
            INSERT INTO medical_record_medicines (medical_record_id, medicine_id, quantity, unit_price, total_price)
            VALUES (:medical_record_id, :medicine_id, :quantity, :unit_price, :total_price)
            """,
            {
                "medical_record_id": record_id,
                "medicine_id": int(medicine_id),
                "quantity": int(quantities[i]) if i < len(quantities) and quantities[i] else 1,
                "unit_price": int(float(unit_prices[i])) if i < len(unit_prices) and unit_prices[i] else 0,
                "total_price": int(float(total_prices[i])) if i < len(total_prices) and total_prices[i] else 0,
            },
        )


def load_invoice_medicines(invoice_id: int) -> list[dict]:
    return fetch_all("SELECT * FROM invoice_medicine_details WHERE invoice_id=:id ORDER BY detail_id ASC", {"id": invoice_id})


def load_invoice_vaccinations(invoice_id: int) -> list[dict]:
    return fetch_all("SELECT * FROM invoice_vaccination_details WHERE invoice_id=:id ORDER BY detail_id ASC", {"id": invoice_id})
