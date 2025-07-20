# 💬 Django Messaging App
This repository contains a Django project (`messaging_app`) designed to implement core messaging functionalities. This initial setup focuses on scaffolding the project, integrating Django REST Framework, and creating the foundational `chats` application.

---
## Project Structure
```
messaging_app/
├── messaging_app/          # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Project settings (INSTALLED_APPS, etc.)
│   ├── urls.py             # Main URL configurations
│   ├── wsgi.py
│   └── asgi.py
├── chats/                  # Django app for messaging features
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # (To be defined in future tasks)
│   ├── tests.py
│   └── views.py            # (To be defined in future tasks)
├── manage.py               # Django's command-line utility
└── README.md               # This file
```

---
## Setup and Installation

Follow these steps to get the project up and running:
1. Navigate to the project root:
```bash
cd messaging_app
```
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: ./venv\Scripts\activate
```
3. Install Django and Django REST Framework:
```bash
pip install django django-rest-framework
```
4. Verify `INSTALLED_APPS` in `messaging_app/settings.py`:
Ensure that `rest_framework` and `chats` are listed in your `INSTALLED_APPS`. This should have been done if you followed the steps above and used the provided `settings.py` content.
5. Run Initial Migrations:
This step sets up Django's built-in database tables (for users, sessions, etc.).
```bash
python manage.py migrate
```
6. Start the Development Server (Optional, for verification):
```bash
python manage.py runserver
```

You can visit `http://127.0.0.1:8000/` in your browser to see the default Django welcome page.

