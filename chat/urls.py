from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from Chat_Django.settings import MEDIA_URL, MEDIA_ROOT
from .views import index, make_login, logout, registration, ask_quest, settings, questions_hot, add_like, question, \
    questions_tag

urlpatterns = [
    path('', index, name="index"),
    path('add_like/', add_like, name='add_like'),
    path('hot/', questions_hot, name='hot'),
    path('question/<int:quest_num>/', question, name='questions'),
    path('login/', make_login, name="login"),
    path('signup/', registration, name="signup"),
    path('logout/', logout, name="logout"),
    path('ask/', ask_quest, name='ask'),
    path('profile/edit/', settings, name='settings'),
    path('tag/<str:tag>/', questions_tag, name='tag'),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
