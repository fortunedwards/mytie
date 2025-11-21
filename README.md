# My Tie - Business Management System

A Django-based internal web application for managing premium necktie business operations.

## Features

### 📦 Product Management
- Product catalog with SKU, name, description, and pricing
- Product availability tracking (sold/available status)
- Image management

### 👥 Customer Relationship Management
- Customer contact information storage
- Order history tracking
- Quick customer search

### 📝 Order Management System
- Order creation and tracking
- Status management (New → Processing → Shipped → Delivered → Returned)
- Order search by ID, customer name, or email
- Status filtering
- Delivery fee tracking per order

### 💰 Financial Reporting
- Revenue tracking and analysis
- Expense management with custom categories
- Profit calculations
- Financial health dashboard

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python src/manage.py migrate
```

3. Create superuser:
```bash
python src/manage.py createsuperuser
```

4. Run the development server:
```bash
python src/manage.py runserver
```

5. Access the application at: http://127.0.0.1:8000/

## Database Models

- **Product**: Necktie catalog items with availability status
- **Customer**: Customer information and contact details
- **Order**: Purchase transactions with status tracking and delivery info
- **OrderItem**: Individual products within orders
- **Expense**: Business expenses with custom categories

## Security Features

- CSRF protection
- Session security
- HTTPS enforcement (production)
- Login attempt limiting
- Secure password validation

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Authentication**: Django built-in auth system

## Project Structure

```
My Tie/
├── src/
│   ├── apps/core/          # Main application
│   ├── config/             # Django settings
│   ├── templates/          # HTML templates
│   └── manage.py
├── static/                 # Static files (CSS, JS, images)
├── requirements.txt
└── README.md
```

## License

Private project for internal business use.