from django.db import models
from django.contrib.auth.models import User
from chat.managers import UserManager, QuestionManager, TagManager


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


class Likes(models.Model):
    id_question = models.IntegerField(verbose_name='id', default=0)
    id_user = models.IntegerField(verbose_name='id лайкнувшего', default=0)

    def __str__(self):
        return self.id_question


class Question(models.Model):
    title = models.CharField(max_length=30, verbose_name="заголовок")
    text = models.TextField(max_length=255, verbose_name="текст")
    author = models.ForeignKey(User, verbose_name="автор", on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField("Tag")
    rating_num = models.IntegerField(verbose_name='рейтинг', default=0)
    added_on = models.DateTimeField(verbose_name='дата и время добавления', auto_now_add=True)
    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name="имя")
    objects = TagManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
