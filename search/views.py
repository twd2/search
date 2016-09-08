# encoding=utf-8
from django.shortcuts import render
from django.db import connection
from django.utils import html
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.views import generic
import re
import jieba
import math
import time
import json
from search.models import *

jieba.initialize()


def main(request):
    return render(request, 'index.html', {'title': 'Main'})


RESULT_PER_PAGE = 10
_cache = {}


def search(request):
    p = int(request.GET.get('p', 1))
    q = request.GET['q']
    sort = bool(request.GET.get('sort', True))
    if len(q) > 100:
        return HttpResponseForbidden('query too long')
    words = list(sorted(filter(lambda s: s.strip() != '', set(jieba.lcut_for_search(q))),
                        key=lambda s: -len(s)))
    cache_key = ' '.join(words)
    print(cache_key)
    query = '%s, ' * len(words)
    query = query[:-2]

    keyword_query = ('  SELECT `page_id` FROM `search_word` '
                     + '  WHERE `word` IN (' + query + ') '
                     + '  GROUP BY `page_id` HAVING count(`word`) >= %s')
    time_start = time.time()
    if cache_key not in _cache:
        cursor = connection.cursor()
        cursor.execute('SELECT count(*) FROM ('
                       + keyword_query
                       + ')', words + [len(words)])
        _cache[cache_key] = count = cursor.fetchone()[0]
    else:
        count = _cache[cache_key]
    print('count time {0}s'.format(time.time() - time_start))
    time_start = time.time()
    order_by = 'sum(`rank`)'
    sort_query = '  ORDER BY ' + order_by + ' DESC'
    if not sort:
        sort_query = ''
    results = list(Page.objects.raw('SELECT `search_page`.* FROM `search_page` '
                                    + 'INNER JOIN ('
                                    + keyword_query
                                    + sort_query
                                    + ') AS `words` ON `search_page`.`id` = `words`.`page_id` '
                                    + 'LIMIT %s, %s',
                                    words + [len(words), RESULT_PER_PAGE * (p - 1), RESULT_PER_PAGE]))
    query_time = time.time() - time_start
    print('query time {0}s'.format(query_time))
    highlight_re_str = reduce(lambda x, y: x + '|' + y, map(re.escape, words))
    highlight_re = re.compile(u'({0})'.format(highlight_re_str))
    rx1 = re.compile(r'(\</span\>)([\s\S]+?)(\<span)', re.UNICODE)
    def repl1(m):
        return m.group(1) + short(m.group(2)) + m.group(3)
    rx2 = re.compile(r'([\s\S]+?)(\<span)', re.UNICODE)
    def repl2(m):
        return short(m.group(1)) + m.group(2)
    rx3 = re.compile(r'(\</span\>)([\s\S]+?)', re.UNICODE)
    def repl3(m):
        return m.group(1) + short(m.group(2))
    def short(s, length=10):
        if len(s) > length:
            return s[:length / 2] + '...' + s[-length / 2:]
        else:
            return s
    def highlight(s):
        return u'<span class="keyword">{0}</span>'.format(s)
    def repl(m):
        return highlight(m.group(0))
    time_start = time.time()

    # post process
    for result in results:
        # highlight title
        result.title_highlighted = highlight_re.sub(repl, html.escape(result.title))
        # highlight content (partially)
        word_records = result.word_set.filter(word__in=words).order_by('start').all()
        length = len(result.content)
        result.content_highlighted = ''
        for word in [word_records[0]]:
            start = max(0, word.start - 100)
            end = min(word.end + 100, length)
            result.content_highlighted += '...'
            result.content_highlighted += html.escape(result.content[start:end])
            result.content_highlighted += '...'
        result.content_highlighted = highlight_re.sub(repl, result.content_highlighted)
        # shorten url
        result.url_short = short(result.url, 100)
    print('post process {0}s'.format(time.time() - time_start))
    page_count = int(math.ceil(count / float(RESULT_PER_PAGE)))
    return render(request, 'search.html',
                  {'title': q, 'q': q, 'p': p, 'sort': sort, 'word_count': len(words),
                   'pages': list(range(max(1, p - 5), min(p + 5, page_count) + 1)),
                   'count': count, 'page_count': page_count,
                   'count_current_page': len(results), 'results': results,
                   'query_time': round(query_time, 4), 'highlight_re': json.dumps(highlight_re_str)})


class PageView(generic.DetailView):
    model = Page
    template_name = 'page.html'


def page_json(request, pk):
    page = Page.objects.get(pk=pk)
    response = HttpResponse(json.dumps({'title': page.title, 'content': page.content,
                                        'url': page.url}))
    response['Content-Type'] = 'application/json'
    return response
