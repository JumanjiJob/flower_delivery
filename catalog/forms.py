from django import forms
from .models import Product, Category


class ProductFilterForm(forms.Form):
    category = forms.ChoiceField(
        required=False,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        label='Цена от',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
    )
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        label='Цена до',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = [('', 'Все категории')] + [
            (cat.id, cat.name) for cat in Category.objects.filter(is_active=True)
        ]
        self.fields['category'].choices = categories