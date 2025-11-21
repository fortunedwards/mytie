from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def currency(value):
    """Format number with commas for currency display"""
    if value is None:
        return "0"
    try:
        # Convert to float and format with commas
        num = float(value)
        return "{:,.0f}".format(num)
    except (ValueError, TypeError):
        return str(value)

@register.filter
def currency_decimal(value):
    """Format number with commas and 2 decimal places"""
    if value is None:
        return "0.00"
    try:
        num = float(value)
        return "{:,.2f}".format(num)
    except (ValueError, TypeError):
        return str(value)