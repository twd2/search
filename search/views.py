# encoding=utf-8
from django.shortcuts import render
from django.db import connection
from django.utils import html
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import HttpResponseForbidden
import re
import jieba
import math
import time
from search.models import *

jieba.initialize()


def index(request):
    return render(request, 'index.html', {'title': 'Main'})


PAGE_PER_PAGE = 10
_cache = {}


def search(request):
    p = int(request.GET.get('p', 1))
    q = request.GET['q']
    if len(q) > 100:
        return HttpResponseForbidden('query too long')
    words = list(filter(lambda s: s.strip() != '', set(jieba.lcut_for_search(q))))
    print(' '.join(words))
    query = '%s, ' * len(words)
    query = query[:-2]

    keyword_query = ('  SELECT `page_id` FROM `search_word` '
                     + '  WHERE `word` IN (' + query + ') '
                     + '  GROUP BY `page_id` ')
    t1 = time.time()
    if q not in _cache:
        cursor = connection.cursor()
        cursor.execute('SELECT count(*) FROM ('
                       + keyword_query
                       + ')', words)
        _cache[q] = count = cursor.fetchone()[0]
    else:
        count = _cache[q]
    print(time.time() - t1)
    t1 = time.time()
    order_by = 'count(`word`)'
    results = list(Page.objects.raw('SELECT `search_page`.* FROM `search_page` '
                                    + 'INNER JOIN ('
                                    + keyword_query
                                    # + '  ORDER BY ' + order_by + ' DESC'
                                    + '  LIMIT %s, %s'
                                    + ') AS `words` ON `search_page`.`id` = `words`.`page_id`',
                                    words + [PAGE_PER_PAGE * (p - 1), PAGE_PER_PAGE]))
    print(time.time() - t1)
    regex = reduce(lambda x, y: x + y, map(lambda s: re.escape(s) + '|', words))[:-1]
    regex = '^([\s\S]*?)((' + regex + ')([\s\S]*?))+$'
    rx = re.compile(regex, re.UNICODE)
    # print(regex)
    # for n, g in rx.match(u'我是中文清华大学我是中文。\n我是中文清华大学我是中文。我是中文清华大学我是中文。').groupdict().items():
    #     print(n, g)
    def short(s):
        if len(s) > 10:
            return s[:5] + '...' + s[-5:]
        else:
            return s
    def highlight(s):
        return u'<span class="keyword">{0}</span>'.format(s)
    def repl(m):
        s = ''
        for i, g in enumerate(m.groups()):
            print(i)
            print(g)
            if i == 0:
                s += short(g)
            elif (i - 1) % 3 == 1:
                s += highlight(g)
            elif (i - 1) % 3 == 2:
                s += short(g)
        return s
    t1 = time.time()
    for result in results:
        end = 0
        new_start = 0
        result.title_highlighted = html.escape(result.title)
        for word in words:
            def highlight(s):
                return s.replace(word,
                                 u'<span class="keyword">{0}</span>'.format(word))
            result.title_highlighted = highlight(result.title_highlighted)
        result.content_highlighted = html.escape(re.sub(r'\s', '', result.content))
        # print(rx.match(result.content_highlighted))
        result.content_highlighted = rx.sub(repl, result.content_highlighted)
        # print(result.content_hightlighted)
        # c = ''
        # print ''
        # for n, g in m.groupdict().items():
        #     print(n)
            # print(m[0])
            # print(rx.sub(repl, m[0]))
            # if word.rank == 2:
            #     # title
            #     pass
            # else:
            #     # content
            #     pass
    print(time.time() - t1)
    page_count = int(math.ceil(count / float(PAGE_PER_PAGE)))
    return render(request, 'search.html',
                  {'title': q, 'q': q, 'p': p, 'word_count': len(words),
                   'pages': list(range(max(1, p - 5), min(p + 5, page_count) + 1)),
                   'count': count, 'page_count': page_count,
                   'count_current_page': len(results), 'results': results})
