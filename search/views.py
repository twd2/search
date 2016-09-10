# encoding=utf-8
from django.shortcuts import render
from django.db import connection
from django.utils import html
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
import urllib
import re
import jieba
import math
import time
import json
from search.models import *

jieba.initialize()


def short(s, length=10):
    if len(s) > length:
        return s[:length / 2] + '...' + s[-length / 2:]
    else:
        return s


def highlight(s):
    return u'<span class="keyword">{0}</span>'.format(s)


def highlight_repl(m):
    return highlight(m.group(0))


def main(request):
    return render(request, 'index.html', {'title': 'Main'})


RESULT_PER_PAGE = 10
_count_cache = {}
_result_cache = {}


def search(request):
    time_start = time.time()
    p = int(request.GET.get('p', 1))
    q = unicode(request.GET.get('q', ''))
    sort = bool(int(request.GET.get('sort', 1)))
    if len(q) > 100:
        return HttpResponseForbidden('query too long')
    # TODO(twd2): map(lower, ...)
    words = list(sorted(filter(lambda s: s.strip() != '', set(jieba.lcut(q))),
                        key=lambda s: -len(s)))
    if not words:
        return HttpResponseForbidden('no query')

    # advanced search
    try:
        year = int(request.GET.get('year', 0))
    except ValueError as e:
        year = 0
    month = bool(int(request.GET.get('month', 0)))
    week = bool(int(request.GET.get('week', 0)))
    print('preprocess time {0}s'.format(time.time() - time_start))

    count_cache_key = (' '.join(words), year, month, week)
    print(count_cache_key)
    query = '%s, ' * len(words)
    query = query[:-2]
    keyword_query = ('  SELECT `page_id` FROM `search_word` '
                     + '  WHERE `word` IN (' + query + ') '
                     + '  GROUP BY `page_id` HAVING count(`word`) >= %s')
    filter_query = ''
    filter_params = []
    if year:
        filter_query += 'strftime(\'%%Y\', `update_at`) = %s AND '
        filter_params.append(str(year))
    if month:
        filter_query += 'julianday(datetime(\'now\')) - julianday(`update_at`) <= 31 AND '
    if week:
        filter_query += 'julianday(datetime(\'now\')) - julianday(`update_at`) <= 7 AND '
    if filter_query:
        # remove ' AND '
        filter_query = filter_query[:-5]
        filter_query = 'WHERE ' + filter_query + ' '
    print(filter_query)
    time_start = time.time()
    if count_cache_key not in _count_cache:
        cursor = connection.cursor()
        # cursor.execute('SELECT count(*) FROM ('
        #                + keyword_query
        #                + ')', words + [len(words)])
        cursor.execute('SELECT count(*) FROM `search_page` '
                       + 'INNER JOIN ('
                       + keyword_query
                       + ') AS `words` ON `search_page`.`id` = `words`.`page_id` '
                       + filter_query,
                       words + [len(words)] + filter_params)
        _count_cache[count_cache_key] = count = cursor.fetchone()[0]
    else:
        count = _count_cache[count_cache_key]
    print('count time {0}s'.format(time.time() - time_start))
    time_start = time.time()
    cache_hit = False
    result_cache_key = (count_cache_key, p, sort)
    if count == 0:
        results = []
    elif result_cache_key not in _result_cache:
        order_by = 'sum(`rank`)'
        sort_query = '  ORDER BY ' + order_by + ' DESC'
        if not sort:
            sort_query = ''
        page_params = [RESULT_PER_PAGE * (p - 1), RESULT_PER_PAGE]
        results = list(Page.objects.raw('SELECT `search_page`.* FROM `search_page` '
                                        + 'INNER JOIN ('
                                        + keyword_query
                                        + sort_query
                                        + ') AS `words` ON `search_page`.`id` = `words`.`page_id` '
                                        + filter_query
                                        + 'LIMIT %s, %s',
                                        words + [len(words)] + filter_params + page_params))
        _result_cache[result_cache_key] = results
    else:
        cache_hit = True
        results = _result_cache[result_cache_key]
    query_time = time.time() - time_start
    print('query time {0}s'.format(query_time))
    highlight_re_str = reduce(lambda x, y: x + '|' + y, map(re.escape, map(html.escape, words)))
    highlight_re = re.compile(u'({0})'.format(highlight_re_str))
    time_start = time.time()

    # post process
    for result in results:
        # highlight title
        result.title_highlighted = highlight_re.sub(highlight_repl, html.escape(result.title))
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
        result.content_highlighted = highlight_re.sub(highlight_repl, result.content_highlighted)
        # shorten url
        result.url_short = short(result.url, 100)
    print('post process {0}s'.format(time.time() - time_start))
    page_count = int(math.ceil(count / float(RESULT_PER_PAGE)))
    query_string = 'q={0}'.format(urllib.quote_plus(q.encode('utf-8')))
    if sort:
        query_string += '&sort=1'
    if year:
        query_string += '&year={0}'.format(year)
    if month:
        query_string += '&month=1'
    if week:
        query_string += '&week=1'
    return render(request, 'search.html',
                  {'title': q, 'q': q, 'query_string': query_string,
                   'p': p, 'sort': sort, 'word_count': len(words),
                   'pages': list(range(max(1, p - 5), min(p + 5, page_count) + 1)),
                   'count': count, 'page_count': page_count,
                   'count_current_page': len(results), 'results': results,
                   'query_time': round(query_time, 4), 'cache_hit': cache_hit,
                   'highlight_re': json.dumps(highlight_re_str)})


class PageView(generic.DetailView):
    model = Page
    template_name = 'page.html'


def page_json(request, pk):
    page = Page.objects.get(pk=pk)
    response = HttpResponse(json.dumps({'title': html.escape(page.title),
                                        'content': html.escape(page.content),
                                        'url': page.url}, ensure_ascii=False))
    response['Content-Type'] = 'application/json'
    return response


def page_go(request, pk):
    page = Page.objects.get(pk=pk)
    # TODO(twd2): count++
    return HttpResponseRedirect(page.url)


def cache(request):
    return render(request, 'cache.html', {'title': 'Cache',
                                          'count_cache': _count_cache,
                                          'result_cache': _result_cache.keys()})


def cache_clear(request):
    global _count_cache, _result_cache
    _count_cache = {}
    _result_cache = {}
    return HttpResponseRedirect(reverse('cache'))


def advanced(request):
    q = request.GET.get('q', '')
    try:
        year = int(request.GET.get('year', 0))
    except ValueError as e:
        year = 0
    month = bool(int(request.GET.get('month', '0')))
    week = bool(int(request.GET.get('week', '0')))
    return render(request, 'advanced.html', {'title': 'Advanced Search', 'q': q,
                                             'year': year, 'month': month, 'week': week})


def page_tags(request, pk):
    import jieba.analyse
    page = Page.objects.get(pk=pk)
    tags = jieba.analyse.extract_tags(page.content)
    return render(request, 'tags.html', {'title': 'Tags',
                                         'page': page, 'tags': tags})