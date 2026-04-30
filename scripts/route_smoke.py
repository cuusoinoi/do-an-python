from fastapi.testclient import TestClient

from app.main import app


ROUTES = [
    "/",
    "/customer",
    "/customer/api/home-data",
    "/customer/services",
    "/customer/contact",
    "/customer/login",
    "/customer/register",
    "/customer/dashboard",
    "/customer/dashboard/api/data",
    "/customer/dashboard/profile",
    "/customer/dashboard/pets",
    "/customer/dashboard/pets/add",
    "/customer/dashboard/medical-records",
    "/customer/dashboard/prescriptions",
    "/customer/dashboard/vaccinations",
    "/customer/dashboard/invoices",
    "/customer/booking",
    "/customer/booking/my-appointments",
    "/admin",
    "/admin/dashboard",
    "/admin/customers",
    "/admin/pets",
    "/admin/doctors",
    "/admin/medical-records",
    "/admin/pet-enclosures",
    "/admin/invoices",
    "/admin/appointments",
    "/admin/service-types",
    "/admin/users",
    "/admin/medicines",
    "/admin/vaccines",
    "/admin/pet-vaccinations",
    "/admin/treatment-courses",
    "/admin/settings",
    "/admin/printing-template",
]


def main() -> None:
    client = TestClient(app)
    failures: list[str] = []
    for route in ROUTES:
        response = client.get(route, follow_redirects=False)
        if response.status_code not in {200, 302, 307, 401, 403}:
            failures.append(f"{route} -> {response.status_code}")
        else:
            print(f"OK  {route} -> {response.status_code}")

    if failures:
        print("\nRoute smoke failures:")
        for item in failures:
            print(item)
        raise SystemExit(1)

    print("\nAll listed routes passed smoke check.")


if __name__ == "__main__":
    main()
