import re

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from .forms import LoginForm, UserRegistrationForm, AskForm
from django.contrib import auth
from .models import UserProfile, Question, Tag


def index(request):
    return render(request, 'chat/index.html', {
        'avatar': avatar(request),
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


def ask_quest(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Ошибка доступа'})
    if request.method == "POST":
        title = request.POST.get("title")
        text = request.POST.get("text")
        tags = request.POST.get("tags")

        qst = Question.objects.create(title=title,
                                      text=text,
                                      author=request.user)
        tags = tags.split(",")
        for tag in tags:
            tag = (str(tag)).replace(' ', '')
            Tag.objects.add_qst(tag, qst)
        qst.save()
        return HttpResponseRedirect('/?page=1000000000')
    form = AskForm()
    return render(request, 'chat/newquestion.html', {'form': form, 'avatar': avatar(request)})


def settings(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password")
            password2 = request.POST.get("password2")
            if password1 != password2:
                return JsonResponse({'status': 'error',
                                     'message': 'Отсутсвует обязательный параметр',
                                     'fields': ['password', 'password2']})
            request.user.username = username
            request.user.set_password(password1)
            request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            user = auth.authenticate(username=username, password=password1)
            if user is not None:
                auth.login(request, user)
            return HttpResponseRedirect('/?continue=saveset')
        # auto filed
        user_data = User.objects.get(id=request.user.id)
        first_name = user_data.first_name
        last_name = user_data.last_name
        username = user_data.username
        email = user_data.email
        form = UserRegistrationForm({'first_name': first_name, 'last_name': last_name, 'username': username,
                                     'email': email})
        return render(request, 'chat/settings.html', {'form': form, 'avatar': avatar(request)})
    return HttpResponseRedirect('/?continue=notlogin')


# static
def avatar(request):
    ava = None
    if request.user.is_authenticated:
        ava = UserProfile.objects.get(user_id=request.user.id).avatar.url
        ava = ava.replace("/chat", "")
    return ava
