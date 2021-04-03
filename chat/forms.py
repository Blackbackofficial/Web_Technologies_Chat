import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core import validators
from .models import UserProfile, Question, Answer


class LoginForm(forms.ModelForm):
    login = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_login(self):
        login = self

    class Meta:
        model = User
        fields = ('login', 'password')


class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    avatar = forms.ImageField(label='Загрузите аватар')

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'avatar')

    def validation(self):
        error_fields = []
        if not self.data.get('first_name') or len(self.data.get('first_name')) == 0:
            error_fields.append("Невалидное ФИО")
        if not self.data.get('last_name') or len(self.data.get('last_name')) == 0:
            error_fields.append("Невалидное ФИО")
        if not self.data.get('username') or len(self.data.get('username')) == 0 and not re.compile("^([A-Za-z0-9]+)+$").match(self.data.get('username')):
            error_fields.append("Невалидный логин")
        if not self.data.get('email') or len(self.data.get('email')) == 0:
            error_fields.append("Невалидный email")
        if not self.data.get('password') or len(self.data.get('password')) == 0:
            error_fields.append("Невалидный пароль")
        if not self.data.get('password2') or len(self.data.get('password2')) == 0:
            error_fields.append("Невалидный пароль")
        if self.data.get('password') != self.data.get('password2'):
            error_fields.append("Пароли не совпадают")
        try:
            validators.validate_email(self.data.get('email'))
        except ValidationError:
            error_fields.append("Неверный формат почты")
        return error_fields


class AskForm(forms.Form):
    title = forms.CharField(label='Титул', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Суть вопроса'}))
    text = forms.CharField(label='Текст', widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Подробнее о вопросе'}))
    tags = forms.CharField(label='Теги', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Указывайте через запятую'}))

    class Meta:
        model = Question
        fields = ('title', 'tags')

    def clean(self):
        return self.cleaned_data

    def validation(self):
        error = []
        title = self.data.get("title")
        if len(title) > 30:
            error.append('Слишком длинный титутл вопроса')
        text = self.data.get("text")
        if len(text) > 255:
            error.append('Слишком длинное тело вопроса')
        tags = self.data.get("tags")
        if len(tags) >= 20:
            error.append('Слишком длинный тег')
        return error


class AnswerForm(forms.Form):
    text = forms.CharField(label='Ваш ответ:', widget=forms.Textarea(
        attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Введите свой ответ'}))

    class Meta:
        model = Answer
        fields = 'text'
