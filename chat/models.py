from django.db import models
from django.contrib.auth.models import User
from chat.managers import UserManager


class UserProfile(models.Model):
    avatar = models.ImageField(null=True, blank=True, verbose_name=u"аватар", upload_to='chat/static/images/')
    register_date = models.DateField(null=False, blank=True, auto_now_add=True, verbose_name=u"дата регистрации")
    rating = models.IntegerField(blank=True, default=0, verbose_name=u"рейтинг")
    user = models.OneToOneField(User, related_name='userprofile', null=False, verbose_name="user",
                                on_delete=models.DO_NOTHING)
    objects = UserManager()

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = u'пользователь'
        verbose_name_plural = u'пользователи'
