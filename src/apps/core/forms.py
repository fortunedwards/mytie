from django import forms
from .models import Expense

class OrderCreateForm(forms.Form):
    # Customer Info
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    
    # Order Details
    order_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    number_of_ties = forms.IntegerField(min_value=1)
    total_cost_of_ties = forms.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery Info
    delivery_payment_type = forms.ChoiceField(choices=[('customer', 'Customer Paid'), ('business', 'Business Paid'), ('shared', 'Shared Payment')])
    customer_delivery_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    business_delivery_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    
    # Packaging Info
    packaging_boxes = forms.IntegerField(min_value=0, initial=0)
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 10:
            raise forms.ValidationError('Phone number must be at least 10 digits')
        return phone
    
    def clean_total_cost_of_ties(self):
        cost = self.cleaned_data['total_cost_of_ties']
        if cost <= 0:
            raise forms.ValidationError('Total cost must be greater than zero')
        return cost
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_payment_type')
        customer_amount = cleaned_data.get('customer_delivery_amount', 0)
        business_amount = cleaned_data.get('business_delivery_amount', 0)
        if delivery_type == 'shared' and (customer_amount == 0 and business_amount == 0):
            raise forms.ValidationError('For shared payment, at least one delivery amount must be specified')
        
        return cleaned_data

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY', 'pattern': r'\d{2}/\d{2}/\d{4}'}),
        required=False
    )
    
    class Meta:
        model = Expense
        fields = ['amount', 'expense_type', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'list': 'expense-descriptions'})
        }

