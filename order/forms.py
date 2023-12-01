from django import forms

from item.models import Item
from order.models import Order
from pricing.models.discount import Discount
from pricing.models.tax import Tax


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'items':
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=Item.objects.all(), )
                self.fields[field_name].widget.attrs['class'] = 'form-control'
            if field_name == 'discount':
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=Discount.objects.all(), required=False)
                self.fields[field_name].widget.attrs['class'] = 'form-control'
            if field_name == 'tax':
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=Tax.objects.all(), required=False)
                self.fields[field_name].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Order
        exclude = ('created_at', 'total_price', 'payment_status',)
