from django.db import models
from django.db.models import Index
from datetime import datetime

class Product(models.Model):
    name = models.CharField(max_length=200, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    image = models.ImageField(upload_to='ties/', blank=True, null=True)
    sold = models.BooleanField(default=False, help_text="Mark as sold when tie is purchased")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        indexes = [Index(fields=['sku']), Index(fields=['sold'])]
    
    def __str__(self):
        return f"{self.name or 'Tie'} ({self.sku})"
    
    def profit_margin(self):
        return self.unit_price - self.cost_price
    
    @property
    def availability_status(self):
        return "Sold" if self.sold else "Available"

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def total_orders(self):
        return self.order_set.count()
    
    def total_ties_bought(self):
        return sum(order.number_of_ties for order in self.order_set.all())
    
    def total_cost_of_ties(self):
        return sum(order.total_amount for order in self.order_set.all())
    
    def total_delivery_paid_by_customer(self):
        return sum(order.customer_delivery_amount for order in self.order_set.all())
    
    def total_delivery_paid_by_business(self):
        return sum(order.business_delivery_amount for order in self.order_set.all())
    
    def total_delivery_fees(self):
        return sum(order.delivery_fee for order in self.order_set.all())
    
    def total_amount_paid(self):
        base_amount = self.total_cost_of_ties()
        return base_amount + self.total_delivery_paid_by_customer()
    
    def selling_price_per_tie(self):
        ties_count = self.total_ties_bought()
        if ties_count == 0:
            return 0
        return (self.total_amount_paid() - self.total_delivery_paid_by_customer()) / ties_count
    
    def cost_price_per_tie(self):
        ties_count = self.total_ties_bought()
        if ties_count == 0:
            return 0
        total_cost = sum(item.product.cost_price * item.quantity for order in self.order_set.all() for item in order.orderitem_set.all())
        return total_cost / ties_count
    
    def first_order_date(self):
        first_order = self.order_set.order_by('created_at').first()
        return first_order.created_at if first_order else None
    
    def latest_order_number(self):
        latest_order = self.order_set.order_by('-created_at').first()
        return latest_order.order_number if latest_order else 'No orders'
    
    def customer_lifetime_value(self):
        return self.total_amount_paid()
    

    
    class Meta:
        indexes = [Index(fields=['phone']), Index(fields=['first_name', 'last_name'])]
    
    def profit_made(self):
        revenue = self.total_cost_of_ties()
        total_cost_price = sum(item.product.cost_price * item.quantity for order in self.order_set.all() for item in order.orderitem_set.all())
        business_expenses = self.total_delivery_paid_by_business()
        return revenue - total_cost_price - business_expenses
    


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'New Order'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]
    
    DELIVERY_CHOICES = [
        ('customer', 'Customer Paid'),
        ('business', 'Business Paid'),
        ('shared', 'Shared Payment'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    number_of_ties = models.PositiveIntegerField(default=1)
    cost_price_per_tie = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_payment_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='customer')
    customer_delivery_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business_delivery_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    packaging_boxes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Get all existing order numbers and find the highest numeric one
            existing_orders = Order.objects.exclude(id=self.id).values_list('order_number', flat=True)
            max_num = 0
            for order_num in existing_orders:
                try:
                    num = int(order_num)
                    if num > max_num:
                        max_num = num
                except (ValueError, TypeError):
                    continue
            
            new_num = str(max_num + 1).zfill(5)
            self.order_number = new_num
        super().save(*args, **kwargs)
    

    
    class Meta:
        indexes = [
            Index(fields=['created_at']),
            Index(fields=['customer']),
            Index(fields=['status']),
            Index(fields=['order_number'])
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer}"
    
    def calculate_total(self):
        self.total_amount = sum(item.subtotal() for item in self.orderitem_set.all())
        self.total_cost = sum(item.cost_total() for item in self.orderitem_set.all())
        self.gross_profit = self.calculate_profit()
        return self.total_amount
    
    def calculate_profit(self):
        base_profit = self.total_amount - self.total_cost
        
        if self.delivery_payment_type == 'business':
            # Business paid delivery, subtract full delivery fee
            return base_profit - self.delivery_fee
        elif self.delivery_payment_type == 'shared':
            # Shared payment, subtract only business portion
            return base_profit - self.business_delivery_amount
        else:
            # Customer paid, no delivery fee deduction
            return base_profit
    
    def profit_margin_percent(self):
        if self.total_amount > 0:
            return (self.calculate_profit() / self.total_amount) * 100
        return 0
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def subtotal(self):
        return self.quantity * self.product.unit_price
    
    def cost_total(self):
        return self.quantity * self.product.cost_price
    
    def profit(self):
        return self.subtotal() - self.cost_total()
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"