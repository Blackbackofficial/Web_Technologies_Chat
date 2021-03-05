import re

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import IntegrityError
from .forms import LoginForm, UserRegistrationForm
from django.contrib import auth
from .models import UserProfile


def index(request):
    avatar = None
    if request.user.is_authenticated:
        avatar = UserProfile.objects.get(user_id=request.user.id).avatar.url
        avatar = avatar.replace("/chat/", "")
    return render(request, 'chat/index.html', {
        'avatar': avatar,
        'title': 'Главная страница'})


def login(request):
    return render(request, 'chat/login.html')


def signup(request):
    return render(request, 'chat/registration.html')


def make_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/?continue=relog')
    if request.method == "POST":
        login = request.POST.get('login')
        password = request.POST.get('password')
        user = auth.authenticate(username=login, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/?continue=login')
        return HttpResponseRedirect('/login/?error=login')
    else:
        error = request.GET.get('error')
        form = LoginForm()
    return render(request, 'chat/login.html',
                  {'form': form, 'error': error})


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect('/?continue=logout')


def registration(request):
    error_fields = []
    if request.user.is_authenticated:
        return HttpResponseRedirect('/?continue=relog')
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        login_user = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")
        avatar = request.FILES.get("avatar")

        if not first_name or len(first_name) == 0:
            error_fields.append("first_name")
        if not last_name or len(last_name) == 0:
            error_fields.append("last_name")
        if not login_user or len(login_user) == 0:
            error_fields.append("username")
        if not email or len(email) == 0:
            error_fields.append("email")
        if not password1 or len(password1) == 0:
            error_fields.append("password")
        if not password2 or len(password2) == 0:
            error_fields.append("password2")

        if password1 != password2:
            error_fields.append("Пароли не совпадают")

        if len(error_fields) > 0:
            form = UserRegistrationForm()
            return render(request, 'chat/registration.html', {'form': form, 'errors': error_fields})

        try:
            validators.validate_email(email)
        except ValidationError:
            error_fields.append("Неверный формат почты")

        if not re.compile("^([A-Za-z0-9]+)+$").match(login_user):
            error_fields.append("Неверный формат логина")
        user = None
        try:
            user = User.objects.create_user(username=login_user, email=email, password=password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user_pk = User.objects.get(id=user.pk)
            add_avatar = UserProfile(user=user_pk, avatar=avatar)
            add_avatar.save()
        except IntegrityError:
            error_fields.append("Нарушена уникальность вводимых данных")
        except:
            error_fields.append("Неизвестная ошибка сервера")
        if user is not None:
            return HttpResponseRedirect('/?continue=reg')
        else:
            error_fields.append("Неизвестная ошибка")
    form = UserRegistrationForm()
    return render(request, 'chat/registration.html', {'form': form, 'errors': error_fields})
