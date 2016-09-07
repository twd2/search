# encoding=utf-8
import os
import jieba

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchengine.settings")
import django
django.setup()
from search.models import *


if __name__ == '__main__':
    word_records = []
    for word in Word.objects.filter(rank=2).all():
        print(word)
        word.pk = None
        word_records.append(word)
    Word.objects.bulk_create(word_records)