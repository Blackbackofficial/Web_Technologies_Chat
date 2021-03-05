from django.urls import path
from .views import index, login, make_login, logout, registration


urlpatterns = [
    path('', index, name="index"),
    path('login/', make_login, name="login"),
    path('signup/', registration, name="signup"),
    path('logout/', logout, name="logout"),
]