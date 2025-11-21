from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from .models import Product, Customer, Order, OrderItem, Expense
from .forms import OrderCreateForm, ExpenseForm

@login_required
def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    
    # Basic metrics
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_ties_sold = sum(order.number_of_ties for order in Order.objects.all())
    
    # Recent activity
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Current month revenue
    today = timezone.now().date()
    month_start = today.replace(day=1)
    month_orders = Order.objects.filter(created_at__date__gte=month_start)
    current_month_revenue = sum(order.total_amount for order in month_orders)
    current_month = month_start.strftime('%b %Y')
    

    
    # Top customers
    customers = Customer.objects.all()
    top_customers = sorted(customers, key=lambda c: c.customer_lifetime_value(), reverse=True)[:5]
    
    # Alerts
    alerts = []
    
    context = {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_ties_sold': total_ties_sold,
        'recent_orders': recent_orders,
        'current_month_revenue': current_month_revenue,
        'current_month': current_month,

        'top_customers': top_customers,
        'alerts': alerts,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def customers(request):
    sort_by = request.GET.get('sort', 'name')
    search_query = request.GET.get('search', '')
    
    customers = Customer.objects.all()
    
    # Search functionality
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    
    if sort_by == 'first_order':
        customers_list = sorted(customers, key=lambda c: c.first_order_date() or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        paginator = Paginator(customers_list, 20)
    elif sort_by == 'ties':
        customers_list = sorted(customers, key=lambda c: c.total_ties_bought(), reverse=True)
        paginator = Paginator(customers_list, 20)
    else:  # alphabetical
        customers = customers.order_by('first_name', 'last_name')
        paginator = Paginator(customers, 20)
    
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/customers.html', {
        'customers': page_obj,
        'sort_by': sort_by,
        'search_query': search_query,
        'page_obj': page_obj
    })

@login_required
def orders(request):
    if request.method == 'POST':
        try:
            # Handle form data from modal
            name_parts = request.POST.get('name', '').split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Calculate delivery fee from customer and business amounts
            customer_delivery = Decimal(str(request.POST.get('customer_delivery_amount', 0)))
            business_delivery = Decimal(str(request.POST.get('business_delivery_amount', 0)))
            total_delivery_fee = customer_delivery + business_delivery
            
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone=request.POST.get('phone'),
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': '',  # No email required
                    'address': request.POST.get('address'),
                }
            )
            
            # Create order
            from django.utils import timezone
            from datetime import datetime
            date_str = request.POST.get('order_date')
            try:
                order_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                order_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            order_datetime = timezone.make_aware(datetime.combine(order_date, datetime.min.time()))
            
            # Calculate costs
            number_of_ties = int(request.POST.get('number_of_ties'))
            cost_price_per_tie = Decimal(str(request.POST.get('cost_price_per_tie', 0)))
            total_cost = cost_price_per_tie * number_of_ties
            
            order = Order.objects.create(
                customer=customer,
                number_of_ties=number_of_ties,
                cost_price_per_tie=cost_price_per_tie,
                total_amount=Decimal(str(request.POST.get('total_cost_of_ties'))),
                total_cost=total_cost,
                gross_profit=0,  # Will be calculated by calculate_profit method
                delivery_fee=total_delivery_fee,
                delivery_payment_type=request.POST.get('delivery_payment_type'),
                customer_delivery_amount=customer_delivery,
                business_delivery_amount=business_delivery,
                packaging_boxes=int(request.POST.get('packaging_boxes', 0)),
                created_at=order_datetime
            )
            
            messages.success(request, f'Order {order.order_number} created successfully for {customer.first_name} {customer.last_name}! Total: ₦{order.total_amount:,.2f}')
            return redirect('orders')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    form = OrderCreateForm()
    
    orders = Order.objects.all().order_by('-created_at')
    customers = Customer.objects.all()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/orders.html', {
        'orders': page_obj,
        'customers': customers, 
        'form': form,
        'page_obj': page_obj
    })

@login_required
def customer_orders(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = Order.objects.filter(customer=customer)
    return render(request, 'core/customer_orders.html', {'customer': customer, 'orders': orders})

@login_required
def financial_report(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            
            # Handle expense type (existing or custom)
            expense_type = request.POST.get('expense_type')
            if expense_type == '__new__':
                expense.expense_type = request.POST.get('custom_expense_type')
            else:
                expense.expense_type = expense_type
            
            # Handle date field
            date_str = request.POST.get('date')
            if date_str:
                from datetime import datetime
                try:
                    expense.date = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    expense.date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                # Default to today if no date provided
                from django.utils import timezone
                expense.date = timezone.now()
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('financial_report')
    else:
        form = ExpenseForm()
    
    # Get all data
    customers = Customer.objects.all()
    orders = Order.objects.all()
    expenses = Expense.objects.all()
    
    # Calculate total revenue as total income from sales
    total_revenue = sum(order.total_amount for order in orders)
    
    # Calculate expenses
    general_expenses = expenses.filter(order__isnull=True).aggregate(Sum('amount'))['amount__sum'] or 0
    order_expenses = expenses.filter(order__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0
    business_delivery = sum(order.business_delivery_amount for order in orders)
    packaging_expenses = expenses.filter(expense_type='packaging').aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = general_expenses + order_expenses + business_delivery + packaging_expenses
    
    # Get existing expense descriptions and types for autocomplete
    expense_descriptions = list(expenses.values_list('description', flat=True).distinct())
    existing_expense_types = list(expenses.values_list('expense_type', flat=True).distinct())
    
    context = {
        'form': form,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': total_revenue - total_expenses,
        'net_margin': ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0,
        'expenses_percentage': (total_expenses / total_revenue * 100) if total_revenue > 0 else 0,
        'order_count': orders.count(),
        'general_expenses': general_expenses,
        'order_expenses': order_expenses,
        'business_delivery': business_delivery,
        'packaging_expenses': packaging_expenses,
        'expense_descriptions': expense_descriptions,
        'existing_expense_types': existing_expense_types,
        'recent_expenses': expenses.order_by('-date')[:10],
    }
    
    return render(request, 'core/financial_report.html', context)

@login_required
def edit_order(request, order_id):
    from django.http import JsonResponse
    order = get_object_or_404(Order, id=order_id)
    
    data = {
        'success': True,
        'order': {
            'id': order.id,
            'customer': {
                'first_name': order.customer.first_name,
                'last_name': order.customer.last_name,
                'phone': order.customer.phone,
                'address': order.customer.address,
            },
            'created_at': order.created_at.isoformat(),
            'number_of_ties': order.number_of_ties,
            'cost_price_per_tie': str(order.cost_price_per_tie),
            'total_amount': str(order.total_amount),
            'delivery_payment_type': order.delivery_payment_type,
            'customer_delivery_amount': str(order.customer_delivery_amount),
            'business_delivery_amount': str(order.business_delivery_amount),
            'packaging_boxes': order.packaging_boxes,
        }
    }
    return JsonResponse(data)

@login_required
def update_order(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            
            # Update customer info
            name_parts = request.POST.get('name', '').split(' ', 1)
            order.customer.first_name = name_parts[0]
            order.customer.last_name = name_parts[1] if len(name_parts) > 1 else ''
            order.customer.phone = request.POST.get('phone')
            order.customer.address = request.POST.get('address')
            order.customer.save()
            
            # Update order info
            customer_delivery = Decimal(str(request.POST.get('customer_delivery_amount', 0)))
            business_delivery = Decimal(str(request.POST.get('business_delivery_amount', 0)))
            total_delivery_fee = customer_delivery + business_delivery
            
            from django.utils import timezone
            from datetime import datetime
            date_str = request.POST.get('order_date')
            try:
                order_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                order_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            order_datetime = timezone.make_aware(datetime.combine(order_date, datetime.min.time()))
            
            number_of_ties = int(request.POST.get('number_of_ties'))
            cost_price_per_tie = Decimal(str(request.POST.get('cost_price_per_tie', 0)))
            total_cost = cost_price_per_tie * number_of_ties
            
            order.number_of_ties = number_of_ties
            order.cost_price_per_tie = cost_price_per_tie
            order.total_amount = Decimal(str(request.POST.get('total_cost_of_ties')))
            order.total_cost = total_cost
            order.gross_profit = 0  # Will be calculated by calculate_profit method
            order.delivery_fee = total_delivery_fee
            order.delivery_payment_type = request.POST.get('delivery_payment_type')
            order.customer_delivery_amount = customer_delivery
            order.business_delivery_amount = business_delivery
            order.packaging_boxes = int(request.POST.get('packaging_boxes', 0))
            order.created_at = order_datetime
            order.save()
            
            messages.success(request, f'Order {order.order_number} updated successfully! Total: ₦{order.total_amount:,.2f}')
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
    
    return redirect('orders')

@login_required
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id)
            order_number = order.order_number
            order.delete()
            messages.success(request, f'Order {order_number} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting order: {str(e)}')
    return redirect('orders')

@login_required
def edit_expense(request, expense_id):
    from django.http import JsonResponse
    expense = get_object_or_404(Expense, id=expense_id)
    
    data = {
        'success': True,
        'expense': {
            'id': expense.id,
            'amount': str(expense.amount),
            'date': expense.date.strftime('%Y-%m-%d'),
            'expense_type': expense.expense_type,
            'description': expense.description,
        }
    }
    return JsonResponse(data)

@login_required
def update_expense(request):
    if request.method == 'POST':
        try:
            expense_id = request.POST.get('expense_id')
            expense = get_object_or_404(Expense, id=expense_id)
            
            expense.amount = Decimal(str(request.POST.get('amount')))
            
            # Handle expense type (existing or custom)
            expense_type = request.POST.get('expense_type')
            if expense_type == '__new__':
                expense.expense_type = request.POST.get('custom_expense_type')
            else:
                expense.expense_type = expense_type
                
            expense.description = request.POST.get('description')
            
            # Handle date field if provided
            date_str = request.POST.get('date')
            if date_str:
                from datetime import datetime
                try:
                    expense.date = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    expense.date = datetime.strptime(date_str, '%Y-%m-%d')
            
            expense.save()
            messages.success(request, 'Expense updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating expense: {str(e)}')
    
    return redirect('financial_report')

@login_required
def delete_expense(request, expense_id):
    if request.method == 'POST':
        try:
            expense = get_object_or_404(Expense, id=expense_id)
            description = expense.description
            expense.delete()
            messages.success(request, f'Expense "{description}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting expense: {str(e)}')
    return redirect('financial_report')

