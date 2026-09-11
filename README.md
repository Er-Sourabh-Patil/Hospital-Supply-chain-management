# Hospital Supply Chain Analytics System

A clean Flask + SQLite student project for managing hospital medical supplies and analyzing purchases, inventory, suppliers, departments, and stock consumption.

## Technology Stack
- Python
- Flask
- SQLite
- Flask-SQLAlchemy / SQLAlchemy
- HTML, CSS, Bootstrap 5
- Jinja2
- JavaScript + Chart.js
- Werkzeug password hashing

## Features
- Session-based login and simple roles
- Supplier CRUD
- Medical supply CRUD
- Batch-level inventory
- Purchase orders and receiving
- Department management
- Department supply requests
- Approve/reject/issue workflow
- Low-stock and expiry alerts
- Dashboard KPIs and Chart.js visualizations
- SQLAlchemy analytics
- Inventory, expiry, purchase and request reports
- Search/filtering
- Sample healthcare data

## Demo Accounts
- Admin: `admin@example.com` / `admin123`
- Inventory Manager: `manager@example.com` / `manager123`
- Department Staff: `staff@example.com` / `staff123`
- Assistant Manager: `assistant@example.com` / `assistant123`
- Ward Staff: `ward@example.com` / `ward123`

## Installation

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed the database:

```bash
python seed.py
```

Run the application:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Business Logic
- Current stock = sum of quantities across inventory batches.
- Low stock when current stock <= minimum stock.
- Near expiry when expiry is within 30 days.
- Expired when expiry date is before today.
- Purchase subtotal = quantity × unit price.
- Receiving a purchase order creates inventory batches and increases stock.
- Issuing an approved request decreases stock using earliest-expiry batches first.
- Stock cannot be issued when insufficient inventory exists.

## Project Structure

```text
hospital_supply_chain/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── seed.py
├── database/
│   └── hospital.db          # created by seed.py
├── models/
│   ├── __init__.py
│   └── models.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── suppliers.py
│   ├── supplies.py
│   ├── inventory.py
│   ├── purchases.py
│   ├── requests.py
│   ├── departments.py
│   ├── analytics.py
│   └── reports.py
├── templates/
└── static/
```

## Notes
This project intentionally uses a simple Flask architecture with blueprints. It does not use MySQL, React, Docker, microservices, REST APIs, repository layers, or unnecessary dependencies.
