from django.db import models


class UserManager(models.Manager):
    def get_user(self, login):
        try:
            return self.get(login=login)
        except self.DoesNotExist:
            return None


