from django.db import models

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    publication_date = models.DateField(null=True, blank=True)
    likes = models.IntegerField(default=0)
    search = models.IntegerField(default=0)

    def __str__(self):
        return self.id
