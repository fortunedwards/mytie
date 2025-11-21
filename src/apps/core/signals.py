from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    # Trigger order save to recalculate total and profit
    order = instance.order
    order.calculate_total()
    order.save()