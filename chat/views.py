from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def index(request):
    return render(request, 'chat/index.html', {
                      'title': 'Главная страница'})


def login(request):
    return render(request, 'chat/login.html')


