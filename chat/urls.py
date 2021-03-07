from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from Chat_Django.settings import MEDIA_URL, MEDIA_ROOT
from .views import index, make_login, logout, registration, ask_quest

urlpatterns = [
    path('', index, name="index"),
    path('login/', make_login, name="login"),
    path('signup/', registration, name="signup"),
    path('logout/', logout, name="logout"),
    path('ask/', ask_quest, name='ask'),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
