# encoding=utf-8
import os
import Queue
import urlparse
import re
import pytz
import datetime
import spider
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchengine.settings")
import django
django.setup()
from search.models import *


def load_news():
    return spider.load_links_from_file('new_links.txt')


TITLE_RE = re.compile(r'\<title\>(.+?)\</title\>')
CONTENT_RE = re.compile(r'\<article (.+?)\>([\s\S]+?)\</article\>')
UPDATE_AT_RE = re.compile(ur'\</i\>(\d{4})年(\d{1,2})月(\d{1,2})日\s+?(\d{1,2}):(\d{1,2}):(\d{1,2})'
                          + ur'[\s　]+?清华新闻网\</div\>')


def get_news_detail(text):
    title = TITLE_RE.search(text).group(1)
    parser = spider.SpiderParser()
    parser.feed(CONTENT_RE.search(text).group(2))
    content = parser.content.strip()
    update_at_match = UPDATE_AT_RE.search(text)
    y, mo, d, h, mi, s = [int(str(g)) for g in update_at_match.groups()]
    tz = pytz.timezone('Asia/Shanghai')
    update_at = tz.localize(datetime.datetime(y, mo, d, h, mi, s)).astimezone(pytz.utc)
    return title, content, update_at


if __name__ == '__main__':
    Q = Queue.Queue()
    try:
        domains = ['news.tsinghua.edu.cn', 'www.tsinghua.edu.cn']
        # initial url
        print 'Initializing'
        for link in load_news():
            Q.put(link)
        while not Q.empty():
            try:
                current_link = Q.get()
                # TODO(twd2): IPv6
                current_domain = urlparse.urlparse(current_link).netloc.split(':')[0]
                if not any(current_domain.endswith(domain) for domain in domains):
                    print 'Ignore(domain={0}) {1}'.format(current_domain, current_link)
                    continue
                if Page.objects.filter(url=current_link).exists():
                    print 'Ignore(exists) {0}'.format(current_link)
                    continue
                try:
                    response = spider.get_response(current_link)
                    info = response.info()
                    if not any(info.getheader('Content-Type').find(t) >= 0 for t in ['text/html']):
                        print 'Ignore(type={0}) {1}'.format(info.getheader('Content-Type'),
                                                            current_link)
                        continue
                    print 'Fetch {0}'.format(current_link)
                    html = response.read().decode('utf-8')
                    print 'Fetched'
                except Exception as e:
                    print 'Error({0}) {1}'.format(e, current_link)
                    continue
                # TODO(twd2): hash
                title, content, update_at = get_news_detail(html)
                print(title + ' ' + str(update_at))
                page = Page(title=title, content=content,
                            download_at=timezone.now(), update_at=update_at,
                            url=current_link, hash='')
                try:
                    page.save()
                    # doesn't follow links
                except Exception as e:
                    print 'Error({0}) {1}'.format(e, current_link)
            except Exception as e:
                print 'Error({0})'.format(e)
    except KeyboardInterrupt as e:
        print('Exiting')
