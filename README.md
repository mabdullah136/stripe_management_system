# (work in progress) Stripe Subscription Management

This project provides a **Stripe-powered subscription management system** using Django. It allows customers to subscribe to various plans, handle payments via Stripe, and manage their subscriptions efficiently.

## Features

- **Customer & Subscription Management**: Customers can subscribe, upgrade, or cancel their plans.
- **Stripe Integration**: Handles subscription creation, modification, and payment processing.
- **Admin Dashboard**: Manage customers, plans, and subscriptions via Django Admin.
- **Billing Periods & Status Tracking**: Supports monthly billing with active, canceled, and past-due statuses.

## Technologies Used

- **Django** - Backend framework
- **Django REST Framework (DRF)** - API handling
- **Stripe API** - Payment processing
- **PostgreSQL / MySQL** (Recommended) - Database
- **Docker (Optional)** - Containerization

---

## Remaining Items

- stripe webhook setup
- Subscription API

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone git@github.com:AhmadMinhas/stripe_arb.git](https://github.com/mabdullah136/stripe_management_system.git)
cd stripe_management_system
pyhton3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py run server
