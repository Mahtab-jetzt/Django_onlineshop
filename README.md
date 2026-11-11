Django Online Shop API

A backend-only online shopping REST API built with Django and Django REST Framework.

Features

- User registration, login, and JWT authentication
- User profile management
- Product management (CRUD)
- Product search, filtering, and ordering
- Categories and product images
- Shopping cart management
- Order creation and order history
- Zarinpal sandbox payment integration
- Django Admin panel
- Swagger API documentation

Tech Stack

- Python 3.12
- Django 6.1
- Django REST Framework
- SQLite
- Simple JWT
- Zarinpal Payment Gateway
- drf-spectacular
- Pillow
- python-dotenv

Installation & Setup

1. Clone the repository

git clone https://github.com/Mahtab-jetzt/Django_onlineshop.git
cd Django_onlineshop

2. Create a virtual environment

Windows (PowerShell):

python -m venv env
.\env\Scripts\Activate.ps1

Linux / macOS:

python3 -m venv env
source env/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

A ".env.example" file is provided in the project root.

Create your own ".env" file by copying the example:

Windows:

Copy-Item .env.example .env

Linux / macOS:

cp .env.example .env

Open ".env" and configure the required values.

For payment testing, use your Zarinpal sandbox credentials. Refer to ".env.example" for the required environment variable names.

Important: Never commit your ".env" file or expose secret credentials.

5. Apply database migrations

python manage.py migrate

6. Load sample data

python manage.py seed_data

This command creates sample categories, products, and product images.

7. Create an admin account

python manage.py createsuperuser

8. Run the development server

python manage.py runserver

The API will be available at:

"http://127.0.0.1:8000/"

API Endpoints

Service| Base URL
Admin Panel| "/admin/"
Users| "/api/v1/users/"
Products| "/api/v1/products/"
Cart| "/api/v1/cart/"
Orders| "/api/v1/orders/"
Payments| "/api/v1/payments/"
Swagger Documentation| "/api/docs/"
OpenAPI Schema| "/api/schema/"
Health Check| "/health/"

Postman Collection

A Postman collection is included in:

"Docs/postman/api_check.json"

To import the collection:

1. Open Postman.
2. Click Import.
3. Select Files.
4. Choose "Docs/postman/api_check.json".
5. Import the collection.
6. Set the base URL to "http://127.0.0.1:8000" if needed.
7. Log in and provide a valid JWT access token for protected endpoints.
8. Run the requests to test the API.

Payment Testing

The project integrates with the Zarinpal Sandbox payment environment.

Before testing payments:

- Configure the required Zarinpal variables in ".env".
- Use valid sandbox credentials.
- Run the Django development server.
- Create an order before starting a payment.

Do not use production credentials for local testing.

Project Structure

Django_onlineshop/
├── config/
├── users/
├── products/
├── cart/
├── orders/
├── payments/
├── Docs/
│   └── postman/
│       └── api_check.json
├── media/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md

Notes

- SQLite is used as the default database.
- Media files are stored locally during development.
- The ".env" file is excluded from version control.
- This project is designed as a backend REST API.