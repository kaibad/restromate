# Restomate

A role-based **Restaurant Management System** built with Django. Restomate helps a restaurant run its day-to-day flow: waiters take orders at tables, the kitchen prepares them, billing handles receipts and payments, and the owner manages everything.

> **Status:** In early development. The first milestone is the username/password login system with role support.

---

## Roles

| Role               | Responsibility                                                                 |
| ------------------ | ------------------------------------------------------------------------------ |
| **Owner**          | Full access. Creates and manages all user accounts (Django superadmin).        |
| **Waiter**         | Views tables, selects a table, picks menu items, places orders, serves ready orders. |
| **Kitchen Helper** | Views incoming orders and marks them as ready.                                 |
| **Billing**        | Views tables marked for billing, shows the receipt, confirms payment, prints the bill. |

> There is **no public sign-up**. Accounts are created only by the Owner/superadmin.

---

## Order Flow (Overview)

1. **Waiter** logs in, opens the tables page, selects a table, and places an order from the menu.
2. **Kitchen Helper** sees the new orders and marks them as **ready**.
3. **Waiter** sees the ready status, serves the order, and marks it as **served**.
4. **Billing** sees tables marked for billing, opens the receipt for a table, confirms payment, and prints the bill.

---

## Sequence Diagram

![Restomate Sequence Diagram](docs/images/sequence-diagram.png)

> Placeholder: replace `docs/images/sequence-diagram.png` with the exported diagram.

---

## Authentication Plan (First Milestone)

- Username and password login.
- Custom user model extending Django's `AbstractUser`, with a `role` field.
- Roles: `OWNER`, `WAITER`, `KITCHEN`, `BILLING`.
- After login, users are redirected to the page for their role.
- Pages are protected by role-based access checks.
- Accounts are created by the Owner/superadmin only.

Example (draft):

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        WAITER = "WAITER", "Waiter"
        KITCHEN = "KITCHEN", "Kitchen Helper"
        BILLING = "BILLING", "Billing"

    role = models.CharField(max_length=20, choices=Role.choices)
```

> Set the custom user model **before the first migration** (`AUTH_USER_MODEL = "accounts.User"`).

---

## Tech Stack (Proposal)

| Layer            | Choice                                        |
| ---------------- | --------------------------------------------- |
| Language         | Python 3                                      |
| Framework        | Django                                        |
| Database         | SQLite (development), PostgreSQL (production) |
| Frontend         | Django Templates + Tailwind CSS or Bootstrap  |
| Live updates     | HTMX polling for order and table status; Django Channels later if needed |
| Authentication   | Django auth with a custom user model          |
| App server       | Gunicorn                                      |
| Web server       | Nginx                                         |
| Containerization | Docker and Docker Compose                     |

---

## Planned Django Apps

| App        | Purpose                                      |
| ---------- | -------------------------------------------- |
| `accounts` | Custom user model, login/logout, role checks |
| `tables`   | Restaurant tables and their status           |
| `menu`     | Menu categories and items                    |
| `orders`   | Orders, order items, and order status        |
| `billing`  | Receipts, payments, and bill printing        |

---

## Roadmap

- [ ] Project setup (`restomate`) and `accounts` app
- [ ] Custom user model with roles
- [ ] Username/password login and logout
- [ ] Role-based redirects and access control
- [ ] Owner-managed account creation
- [ ] Tables and menu management
- [ ] Waiter: place orders
- [ ] Kitchen: view orders and mark as ready
- [ ] Waiter: mark orders as served
- [ ] Billing: receipt, payment confirmation, and print bill

---

## Getting Started

```bash
# Clone the repository
git clone <repo-url>
cd restomate

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create the owner (superadmin) account
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

---

## License

To be decided.
