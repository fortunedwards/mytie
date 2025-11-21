from django.contrib import admin
from .models import Product, Customer, Order, OrderItem, Expense

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'unit_price', 'cost_price', 'profit_margin', 'availability_status', 'sold']
    search_fields = ['name', 'sku']
    list_filter = ['sold']
    
    def availability_status(self, obj):
        return obj.availability_status
    availability_status.short_description = 'Status'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'total_ties_bought', 'total_amount_paid']
    search_fields = ['first_name', 'last_name', 'phone']
    fieldsets = (
        ('Customer Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'delivery_fee', 'delivery_payment_type', 'created_at']
    list_filter = ['status', 'delivery_payment_type', 'created_at']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__email']
    inlines = [OrderItemInline, ExpenseInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'customer', 'status', 'number_of_ties', 'cost_price_per_tie')}),
        ('Amounts', {'fields': ('total_amount', 'total_cost', 'gross_profit')}),
        ('Delivery', {'fields': ('delivery_fee', 'delivery_payment_type', 'customer_delivery_amount', 'business_delivery_amount', 'packaging_boxes')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('updated_at',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_total()
        obj.save()

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'expense_type', 'order', 'date']
    list_filter = ['expense_type', 'date']
    search_fields = ['description']