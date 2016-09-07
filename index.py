# encoding=utf-8
import os
import jieba

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchengine.settings")
import django
django.setup()
from search.models import *


if __name__ == '__main__':
    for page in Page.objects.all():
        if page.word_set.exists():
            continue
        print 'Page {0}'.format(page.id)
        word_records = []
        words = set()
        for word, start, end in jieba.tokenize(page.title, mode='search'):
            if word.strip() != '' and word not in words:
                word_records.append(Word(page=page, word=word, start=start, end=end, rank=2))
                words.add(word)
        for word, start, end in jieba.tokenize(page.content, mode='search'):
            if word.strip() != '' and word not in words:
                word_records.append(Word(page=page, word=word, start=start, end=end, rank=1))
                words.add(word)
        print '{0} words'.format(len(words))
        Word.objects.bulk_create(word_records)