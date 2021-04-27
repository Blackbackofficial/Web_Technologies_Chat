from django.conf.urls import url

from health_checks.views import ping, time, status

urlpatterns = [
    url(r'^ping/', ping),
    url(r'^time/', time),
    url(r'^status/', status),
]
