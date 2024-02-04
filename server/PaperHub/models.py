# models.py
from django.db import models
from django.contrib.auth.models import User


class PaperHubUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='user')
    favorite_articles = models.ManyToManyField('elasticsearchApp.Article', related_name='favorited_by', blank=True)
    saved_articles = models.ManyToManyField('elasticsearchApp.Article', related_name='saved_by', blank=True)

    def __str__(self):
        return self.user.username

class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='moderator')
    

    def __str__(self):
        return self.user.username

class Admin(models.Model):
    AdminFname = models.CharField(max_length=100)
    AdminLname = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='admin')

    def __str__(self):
        return self.user.username
