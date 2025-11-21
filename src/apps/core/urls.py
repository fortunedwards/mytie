from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customers/', views.customers, name='customers'),
    path('orders/', views.orders, name='orders'),
    path('orders/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('orders/update/', views.update_order, name='update_order'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('customers/<int:customer_id>/orders/', views.customer_orders, name='customer_orders'),
    path('financial-report/', views.financial_report, name='financial_report'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/update/', views.update_expense, name='update_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
]