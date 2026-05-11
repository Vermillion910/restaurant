import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Пароль должен содержать от 6 до 12 символов'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Повторите пароль ещё раз'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Логин'
        self.fields['email'].label = 'Электронная почта'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        if len(username) < 3:
            raise forms.ValidationError('Логин слишком короткий. Минимум 3 символа')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже зарегистрирован')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 6:
            raise forms.ValidationError('Пароль слишком короткий. Минимум 6 символов')
        if len(password1) > 12:
            raise forms.ValidationError('Пароль слишком длинный. Максимум 12 символов')
        return password1


class ReservationForm(forms.ModelForm):
    TIME_CHOICES = [
        ('10:00', '10:00'), ('11:00', '11:00'), ('12:00', '12:00'),
        ('13:00', '13:00'), ('14:00', '14:00'), ('15:00', '15:00'),
        ('16:00', '16:00'), ('17:00', '17:00'), ('18:00', '18:00'),
        ('19:00', '19:00'), ('20:00', '20:00'), ('21:00', '21:00'),
    ]

    GUESTS_CHOICES = [(i, f'{i} гост{"ь" if i == 1 else "я" if i in [2,3,4] else "ей"}') for i in range(1, 21)]

    date = forms.DateField(
        label='Дата бронирования',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': datetime.date.today().strftime('%Y-%m-%d')
        })
    )

    time = forms.ChoiceField(choices=TIME_CHOICES, label='Время', widget=forms.Select(attrs={'class': 'form-control'}))
    guests_count = forms.ChoiceField(choices=GUESTS_CHOICES, label='Количество гостей', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'guests_count', 'first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone': 'Контактный телефон',
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < datetime.date.today():
            raise forms.ValidationError('Нельзя забронировать на прошедшую дату')
        return date


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия'}),
        }
        labels = {
            'username': 'Логин',
            'email': 'Электронная почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже зарегистрирован')
        return email