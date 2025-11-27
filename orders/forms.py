from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone
from .models import Order


class OrderForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Телефон должен быть в формате: '+79999999999'. Максимум 15 цифр."
    )

    customer_phone = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+79999999999'
        })
    )

    delivery_time = forms.DateTimeField(
        label='Время доставки',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_phone',
            'customer_email',
            'delivery_address',
            'delivery_time',
            'payment_method',
            'comment'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите полный адрес доставки'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительные пожелания к заказу'
            }),
        }
        labels = {
            'customer_name': 'Имя',
            'customer_email': 'Email',
            'delivery_address': 'Адрес доставки',
            'payment_method': 'Способ оплаты',
            'comment': 'Комментарий к заказу',
        }

    def clean_delivery_time(self):
        delivery_time = self.cleaned_data['delivery_time']
        if delivery_time <= timezone.now():
            raise forms.ValidationError('Время доставки должно быть в будущем')
        return delivery_time