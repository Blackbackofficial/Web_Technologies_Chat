from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from Chat_Django.settings import MEDIA_URL, MEDIA_ROOT
from .views import index, make_login, logout, registration, ask_quest, settings, questions_hot, questions_new, add_like,\
    dismiss_like

urlpatterns = [
    path('', index, name="index"),
    path('add_like/', add_like, name='add_like'),
    path('dismiss_like/', dismiss_like, name='add_like'),
    path('hot/', questions_hot, name='hot'),
    path('new/', questions_new, name='new'),
    path('login/', make_login, name="login"),
    path('signup/', registration, name="signup"),
    path('logout/', logout, name="logout"),
    path('ask/', ask_quest, name='ask'),
    path('profile/edit/', settings, name='settings'),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
