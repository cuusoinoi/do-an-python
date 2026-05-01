# Route parity checklist

This checklist tracks route-level parity between the original and current implementation.

## Customer

- [x] `/customer`
- [x] `/customer/api/home-data`
- [x] `/customer/services`
- [x] `/customer/contact`
- [x] `/customer/login` (GET/POST)
- [x] `/customer/register` (GET/POST)
- [x] `/customer/logout`
- [x] `/customer/dashboard`
- [x] `/customer/dashboard/api/data`
- [x] `/customer/dashboard/profile` (GET/POST)
- [x] `/customer/dashboard/pets`
- [x] `/customer/dashboard/pets/add` (GET/POST)
- [x] `/customer/dashboard/medical-records`
- [x] `/customer/dashboard/prescriptions`
- [x] `/customer/dashboard/vaccinations`
- [x] `/customer/dashboard/invoices`
- [x] `/customer/dashboard/invoices/view/{id}`
- [x] `/customer/booking`
- [x] `/customer/booking/create`
- [x] `/customer/booking/my-appointments`

## Admin auth

- [x] `/admin`
- [x] `/admin/login`
- [x] `/admin/logout`
- [x] `/admin/dashboard`

## Admin modules

- [x] `customers` (index/add/store/edit/update/delete)
- [x] `pets` (index/add/store/edit/update/delete)
- [x] `doctors` (index/add/store/edit/update/delete)
- [x] `medical-records` (index/add/store/edit/update/delete)
- [x] `pet-enclosures` (index/add/store/edit/update/delete/checkout)
- [x] `invoices` (index/add/store/edit/update/delete)
- [x] `appointments` (index/view/update/update-status/delete)
- [x] `service-types` (index/add/store/edit/update/delete)
- [x] `users` (index/add/store/edit/update/delete/change-password/update-password)
- [x] `medicines` (index/add/store/edit/update/delete)
- [x] `vaccines` (index/add/store/edit/update/delete)
- [x] `pet-vaccinations` (index/add/store/edit/update/delete)
- [x] `treatment-courses` (index/add/store/edit/update/delete/complete)
- [x] `treatment sessions` (list/add/store/edit/update/delete)
- [x] `diagnosis` (view/save)
- [x] `prescription` (view/add/delete)
- [x] `settings` (view/update)
- [x] `print` (invoice/medical-record/treatment-session/pet-enclosure)
- [x] `printing-template` (index redirect + pet-enclosure/load-commit/load-invoice)

## Final parity pass

- [ ] pixel-level UI consistency across templates
- [ ] JS behavior parity on all list/forms
- [ ] route-by-route manual smoke tested
