# Invoicely Pro Backend
## Description
### Invoicely Pro is an invoice management application. This repository contains the Django backend for the application.
## Features

1. User authentication and authorization
2. Invoice creation, editing, and deletion
3. Itemized list of products/services with quantity, rate, and amount
4. Summary section with subtotal, tax, discount, shipment, amount paid, and balance due
5. Download invoice as PDF
6. Share invoice via link
7. API Endpoints

POST /api/v1/invoices/ - Create a new invoice
GET /api/v1/invoices/ - List all invoices
GET /api/v1/invoices/{id}/ - Retrieve an invoice by ID
PUT /api/v1/invoices/{id}/ - Update an invoice
DELETE /api/v1/invoices/{id}/ - Delete an invoice
POST /api/v1/invoices/{id}/download/ - Download an invoice as PDF
POST /api/v1/invoices/{id}/share/ - Share an invoice via link
Requirements
Python 3.10+
Django 5.0+
MYSQL
Setup
Clone the repository: git clone https://github.com/your-username/invoicely-pro-backend.git
Install dependencies: pip install -r requirements.txt
Create a PostgreSQL database and update settings.py with the database credentials
Run migrations: python manage.py migrate
Start the development server: python manage.py runserver
Contributing
Contributions are welcome! Please submit a pull request with your changes.
License
This project is licensed under the MIT License. See LICENSE.txt for details.
Contact
Oladapo Odedeyi dapoodedeyi@example.com
