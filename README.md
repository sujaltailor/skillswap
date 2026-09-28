# SkillSwap

A Django web application for people to share skills. Users can list skills they teach and want to learn, find other members, and send skill-exchange requests.

## Features

- User registration, login, and dashboard
- Profiles with skills to teach and skills to learn
- Skill discovery and exchange requests
- Accept or reject incoming requests
- Custom staff dashboard for managing users
- Django administration interface

## Requirements

- Python 3.14 (the project environment currently uses Python 3.14)
- pip

Dependencies are listed in `requirements.txt`.

## Setup (Windows PowerShell)

From the project directory:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/skill/home/` for the app. The Django admin is available at `http://127.0.0.1:8000/admin/`.

## Main Routes

- `/skill/register/` - create a user account
- `/skill/login/` - sign in
- `/skill/dashboard/` - user dashboard
- `/skill/find-skills/` - find members by skills
- `/skill/requests/` - view exchange requests
- `/skill/admin-login/` - custom staff login
- `/skill/admin-dashboard/` - custom staff dashboard
- `/admin/` - Django administration

## Configuration and Data

The development database is SQLite and is created locally as `db.sqlite3` when migrations run. It is excluded from Git so local user data is not published.

Set `DJANGO_SECRET_KEY` in the environment for deployments. The fallback key in settings is for local development only and must not be used in production. Set `DEBUG = False` and configure `ALLOWED_HOSTS` before deploying.

## Tests

Run the Django test suite with:

```powershell
python manage.py test
```

## Deploy to Render

1. Create a new Blueprint in Render and connect this GitHub repository.
2. Render reads `render.yaml` to create the web service and PostgreSQL database.
3. Wait for the first deploy to finish, then open the service URL.

The included Blueprint uses Render's free web and PostgreSQL plans for a demo.
The free PostgreSQL database expires after 30 days, so upgrade it before storing
data you need to keep. The generated `DJANGO_SECRET_KEY` is configured by Render.
