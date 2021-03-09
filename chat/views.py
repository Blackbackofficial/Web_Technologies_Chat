from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.db import IntegrityError
from .forms import LoginForm, UserRegistrationForm, AskForm
from django.contrib import auth
from .models import UserProfile, Question, Tag
from django.core.paginator import Paginator, EmptyPage
import re


def paginate(request, qs, url=None):
    try:
        limit = int(request.GET.get('limit', 5))
    except ValueError:
        limit = 5
    if limit > 100:
        limit = 5
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(qs, limit)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    if url == 'hot':
        paginator.baseurl = '/hot/?page='
    elif url == 'new':
        paginator.baseurl = '/new/?page='
    else:
        paginator.baseurl = '/?page='
    paginator.startdiv = page.number - 2
    paginator.enddiv = page.number + 2
    return page


def index(request, mod=0):
    if mod == 1:
        page = paginate(request, Question.objects.hot(), 'hot')
        title = 'Популярные'
        hot = None
        new = 'Новые'
    elif mod == 2:
        page = paginate(request, Question.objects.new(), 'new')
        title = 'Новые'
        hot = 'Популярные'
        new = None
    else:
        page = paginate(request, Question.objects.all(), '')
        title = 'Все вопросы'
        hot = 'Популярные'
        new = 'Новые'
    title_page = title + ':'
    return render(request, 'chat/index.html', {
        'avatar': avatar(request),
        'title': title, 'title_page': title_page, 'hot': hot, 'new': new,
        'page': page, 'posts': page.object_list, 'paginator': page.paginator
    })


def questions_hot(request):
    return index(request, 1)


def questions_new(request):
    return index(request, 2)


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
        data = get_data(request)
        if not data['first_name'] or len(data['first_name']) == 0:
            error_fields.append(data["first_name"])
        if not data['last_name'] or len(data['last_name']) == 0:
            error_fields.append("last_name")
        if not data['username'] or len(data['username']) == 0:
            error_fields.append("username")
        if not data['email'] or len(data['email']) == 0:
            error_fields.append("email")
        if not data['password1'] or len(data['password1']) == 0:
            error_fields.append("password")
        if not data['password2'] or len(data['password2']) == 0:
            error_fields.append("password2")

        if data['password1'] != data['password2']:
            error_fields.append("Пароли не совпадают")

        if len(error_fields) > 0:
            form = UserRegistrationForm()
            return render(request, 'chat/registration.html', {'form': form, 'errors': error_fields})

        try:
            validators.validate_email(data['email'])
        except ValidationError:
            error_fields.append("Неверный формат почты")

        if not re.compile("^([A-Za-z0-9]+)+$").match(data['username']):
            error_fields.append("Неверный формат логина")
        user = None
        try:
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password1'])
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()
            user_pk = User.objects.get(id=user.pk)
            add_avatar = UserProfile(user=user_pk, avatar=data['avatar'])
            add_avatar.save()
        except IntegrityError:
            error_fields.append("Нарушена уникальность вводимых данных")

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
            data = get_data(request)
            if data['password1'] != data['password2']:
                return JsonResponse({'status': 'error',
                                     'message': 'Отсутсвует обязательный параметр',
                                     'fields': ['password', 'password2']})
            request.user.username = data['username']
            request.user.set_password(data['password1'])
            request.user.email = data['email']
            request.user.first_name = data['first_name']
            request.user.last_name = data['last_name']
            request.user.save()
            user = auth.authenticate(username=data['username'], password=data['password1'])
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


def get_data(request):
    data = dict()
    data['first_name'] = request.POST.get("first_name")
    data['last_name'] = request.POST.get("last_name")
    data['username'] = request.POST.get("username")
    data['email'] = request.POST.get("email")
    data['password1'] = request.POST.get("password")
    data['password2'] = request.POST.get("password2")
    data['avatar'] = request.FILES.get("avatar")
    return data
