from django.db import models
from django.core.cache import cache


class UserManager(models.Manager):
    def get_user(self, login):
        try:
            return self.get(login=login)
        except self.DoesNotExist:
            return None


class QuestionManager(models.Manager):
    def hot(self):
        return self.order_by('-rating_num')

    def new(self):
        return self.order_by('-added_on')

    def by_tag(self, tag):
        return self.filter(tags__name__iexact=tag).order_by('-rating_num')


class TagManager(models.Manager):
    def add_qst(self, tag_str, question):
        tag, created = self.get_or_create(name=tag_str)
        question.tags.add(tag)
        return tag

    def by_tag(self, tag_str):
        return self.filter(title=tag_str).first().questions.all()

    def popular(self):
        return cache.get('test')