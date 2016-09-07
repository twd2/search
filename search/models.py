from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Page(models.Model):
    title = models.CharField(max_length=1024)
    content = models.TextField()
    update_at = models.DateTimeField()  # UTC
    download_at = models.DateTimeField()  # UTC
    url = models.CharField(max_length=1024, unique=True)
    hash = models.CharField(max_length=1024, default='')
    rank = models.IntegerField(default=1)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Word(models.Model):
    word = models.CharField(max_length=100, db_index=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    rank = models.IntegerField(default=1)

    class Meta:
        unique_together = (('word', 'page',),)

    def __str__(self):
        return self.word