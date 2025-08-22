# Furlink Backend

A Django-based backend for a pet hostel management system, supporting user registration (pet owner/keeper), pet management, and JWT authentication.

## Features
- Custom user model with KYC and address fields (Nepal context)
- Role-based registration (Pet Owner, Pet Keeper)
- Pet CRUD with owner/keeper linkage
- JWT authentication (Simple JWT)
- Django admin for all models

## Requirements
- Python 3.12+
- Django 5.2+
- djangorestframework
- djangorestframework-simplejwt
- Pillow

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Furlink_Backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST auth/register/` — Register as pet owner or keeper
- `POST auth/login/` — Obtain JWT token (username, password)


### Pet Management
- `GET/POST pet/pets/` — List or create pets
- `GET/PUT/DELETE pet/pets/<id>/` — Retrieve, update, or delete a pet

## Notes
- Media and static files are served in development only.
- Adjust `ALLOWED_HOSTS` and `DEBUG` for production.
- For KYC and image fields, Pillow must be installed.

## License
MIT

