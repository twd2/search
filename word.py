# encoding=utf-8
import os
import jieba
import collections
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchengine.settings")
import django
django.setup()
from search.models import *


if __name__ == '__main__':
    words = collections.defaultdict(list)
    for page in Page.objects.all():
        print 'Page {0}'.format(page.id)
        for word in jieba.cut_for_search(page.title):
            words[word].append(page.id)
        for word in jieba.cut_for_search(page.content):
            words[word].append(page.id)
    with open('index.txt', 'w') as f:
        f.write(json.dumps(words))