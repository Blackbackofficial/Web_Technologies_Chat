from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, UserRegistrationForm, AskForm, AnswerForm
from django.contrib import auth
from .models import UserProfile, Question, Tag, Likes, Answer
from django.core.paginator import Paginator, EmptyPage


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


@csrf_exempt
def add_like(request):
    if request.method == 'POST':
        ans_id = request.POST['answer_id']
        questions = Question.objects.get(pk=ans_id)
        like_dis = request.POST['answer']
        if check(request, like_dis, questions):
            return JsonResponse({'rating': questions.rating_num})
        return JsonResponse({'rating': "Answered"})


def index(request, mod=0):
    if mod == 1:
        page = paginate(request, Question.objects.hot(), 'hot')
        title = 'Популярные'
        hot = None
        new = 'Новые'
    else:
        page = paginate(request, Question.objects.new(), '')
        title = 'Новые'
        hot = 'Популярные'
        new = None
    title_page = title + ':'
    like = Likes.objects.all().filter(id_user=request.user.id)
    # for page.object_list range
    return render(request, 'chat/index.html', {
        'avatar': avatar(request), 'like': like,
        'title': title, 'title_page': title_page, 'hot': hot, 'new': new,
        'page': page, 'posts': page.object_list, 'paginator': page.paginator
    })


def questions_hot(request):
    return index(request, 1)


def login(request):
    return render(request, 'chat/login.html')


def signup(request):
    return render(request, 'chat/signup.html')


def question(request, quest_num=1):
    error = []
    if quest_num is None:
        raise Http404("No questions provided")
    if request.method == "POST":
        form = AnswerForm(request.POST)
        error = form.validate()
        if len(error) == 0:
            quest = Question.objects.get(id=quest_num)
            quest.answer = quest.answer + 1
            quest.save()
            Answer.objects.create(content=request.POST.get('text'), question=quest, author=request.user)
    q = Question.objects.get(id=quest_num)
    form = AnswerForm()
    page = paginate(request, q.answers.all())
    user_name = None
    if request.user.is_authenticated:
        user_name = request.user.first_name
    page.paginator.baseurl = '/question/' + str(quest_num) + '/?page='
    return render(request, 'chat/question.html',
                  {'posts': page.paginator.page(page.paginator.num_pages).object_list, 'avatar': avatar(request),
                   'paginator': page.paginator, 'page': page.paginator.page(page.paginator.num_pages),
                   'id': quest_num, 'question': q, 'form': form, 'user_name': user_name, 'errors': error})


def questions_tag(request, tag):
    if tag is None:
        raise Http404("No tag provided")

    page = paginate(request, Question.objects.by_tag(tag))
    if page.end_index() == 0:
        raise Http404("No tag provided")

    page.paginator.baseurl = '/tag/' + tag + '/?page='
    return render(request, "chat/tag.html", {'posts': page.object_list, 'avatar': avatar(request),
                                             'paginator': page.paginator, 'page': page, 'tag': tag})


def make_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/?continue=relog')
    if request.method == "POST":
        user = auth.authenticate(username=request.POST.get('login'), password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/?continue=login')
        return HttpResponseRedirect('/login/?error=login')
    else:
        error = request.GET.get('error')
        form = LoginForm()
    return render(request, 'chat/login.html', {'form': form, 'error': error})


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return HttpResponseRedirect('/?continue=logout')


def registration(request):
    error_fields = []
    if request.user.is_authenticated:
        return HttpResponseRedirect('/?continue=relog')
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        error_fields = form.validate()
        data = get_data(request)
        if len(error_fields) > 0:
            form = UserRegistrationForm()
            return render(request, 'chat/signup.html', {'form': form, 'errors': error_fields})
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
            return HttpResponseRedirect('/?continue=reg')
    form = UserRegistrationForm()
    return render(request, 'chat/signup.html', {'form': form, 'errors': error_fields})


def ask_quest(request):
    error = []
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Ошибка доступа'})
    if request.method == "POST":
        form = AskForm(request.POST)
        error = form.validate()
        if len(error) == 0:
            quest = Question.objects.create(title=request.POST.get('title'), text=request.POST.get('text'), author=request.user)
            tags = request.POST.get('tags').split(",")
            for tag in tags:
                tag = (str(tag)).replace(' ', '')
                Tag.objects.add_qst(tag, quest)
            quest.save()
            return HttpResponseRedirect('/question/{}/'.format(quest.id))
    form = AskForm()
    return render(request, 'chat/ask.html', {'form': form, 'avatar': avatar(request), 'errors': error})


def settings(request):
    success = error = []
    flag = False
    if request.user.is_authenticated:
        if request.method == "POST":
            form = UserRegistrationForm(request.POST)
            error = form.validate()
            data = get_data(request)
            flag = True
            request.user.username = data['username']
            request.user.set_password(data['password1'])
            request.user.email = data['email']
            request.user.first_name = data['first_name']
            request.user.last_name = data['last_name']
            request.user.userprofile.avatar = data['avatar']
            request.user.save()
            request.user.userprofile.save()
            user = auth.authenticate(username=data['username'], password=data['password1'])
            if user is not None:
                auth.login(request, user)
        # auto filed
        user_data = User.objects.get(id=request.user.id)
        first_name = user_data.first_name
        last_name = user_data.last_name
        username = user_data.username
        email = user_data.email
        form = UserRegistrationForm({'first_name': first_name, 'last_name': last_name, 'username': username, 'email': email})
        if len(error) == 0 and flag:
            success.append('Сохранено')
        else:
            success = None
        return render(request, 'chat/settings.html', {'form': form, 'avatar': avatar(request),
                                                      'errors': error, 'success': success})
    return HttpResponseRedirect('/?continue=notlogin')


# static
def avatar(request):
    ava = None
    if request.user.is_authenticated:
        ava = UserProfile.objects.get(user_id=request.user.id).avatar.url
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


def check(request, like_dis, questions):
    try:
        Likes.objects.get(id_question=questions, id_user=request.user)
        return False
    except ObjectDoesNotExist:
        s_like = 2
        if like_dis == 'like':
            questions.rating_num = questions.rating_num + 1
            s_like = 1
            questions.save()
        else:
            if questions.rating_num > 0:
                questions.rating_num = questions.rating_num - 1
                questions.save()
        like = Likes(id_question=questions, id_user=request.user, value=s_like)
        like.save()
        return True
