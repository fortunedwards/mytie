# My Tie - Business Management System

A Django-based internal web application for managing premium necktie business operations with comprehensive order tracking and financial reporting.

## Features

### 👥 Customer Management
- Customer contact information (name, phone, address)
- Customer lifetime value tracking
- Order history and statistics per customer
- Customer search and sorting capabilities
- Automatic customer creation during order placement

### 📝 Order Management System
- Comprehensive order creation with detailed cost tracking
- Automatic order numbering system
- Order editing and deletion capabilities
- Delivery fee management (customer/business/shared payment)
- Cost price and selling price tracking per tie
- Packaging box tracking
- Order date management with flexible date formats

### 💰 Financial Reporting & Analytics
- Revenue tracking and profit calculations
- Expense management with custom categories
- Business delivery cost tracking
- Net profit and margin calculations
- Monthly revenue reporting
- Expense categorization and editing
- Financial dashboard with key metrics

### 📊 Dashboard & Analytics
- Total customers, orders, and ties sold
- Recent order activity
- Top customers by lifetime value
- Current month revenue tracking
- Key performance indicators

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements/base.txt
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

- **Customer**: Customer information with calculated metrics (lifetime value, total orders, profit analysis)
- **Order**: Complete order tracking with cost analysis, delivery fees, and profit calculations
- **Product**: Basic product catalog (currently simplified for tie-specific business)
- **OrderItem**: Individual products within orders (supports future expansion)
- **Expense**: Business expenses with flexible categorization and date tracking

## Key Business Logic

### Order Processing
- Automatic order number generation
- Flexible delivery fee handling (customer pays, business pays, or shared)
- Real-time profit calculation including delivery costs
- Support for bulk tie orders with per-tie cost tracking

### Financial Calculations
- Customer lifetime value and profitability analysis
- Order-level profit margins with delivery cost considerations
- Comprehensive expense tracking with custom categories
- Net profit calculations across all business operations

## Security Features

- CSRF protection
- Secure session management
- HTTPS enforcement (production ready)
- Login attempt limiting (configured)
- Secure password validation
- XSS and clickjacking protection

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Django built-in auth system
- **Image Handling**: Pillow for product images

## Project Structure

```
My Tie/
├── src/
│   ├── apps/core/          # Main business logic
│   │   ├── models.py       # Database models
│   │   ├── views.py        # Business logic & views
│   │   ├── forms.py        # Form handling
│   │   ├── urls.py         # URL routing
│   │   └── migrations/     # Database migrations
│   ├── config/             # Django configuration
│   └── manage.py
├── templates/core/         # HTML templates
├── static/images/          # Static assets
├── requirements/           # Dependency management
│   ├── base.txt           # Core dependencies
│   ├── development.txt    # Dev dependencies
│   └── production.txt     # Production dependencies
└── README.md
```

## Application URLs

- `/dashboard/` - Main dashboard with key metrics
- `/customers/` - Customer management and search
- `/orders/` - Order creation, editing, and tracking
- `/financial-report/` - Financial analytics and expense management
- `/customers/<id>/orders/` - Individual customer order history

## License

Private project for internal business use.