# encoding=utf-8
import os
import urllib
import urllib2
import jieba
import json
import Queue
import urlparse
from HTMLParser import HTMLParser
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchengine.settings")
import django
django.setup()
from search.models import *


class SpiderParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_content = False
        self.is_title = False
        self.title = ''
        self.content = ''
        self.links = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.is_title = tag == 'title'
        self.is_content = tag not in ['script', 'title']
        if tag in ['a']:
            for attr, value in attrs:
                if not value:
                    value = ''
                value = value.strip().split('#')[0]
                if attr.lower() in ['href', 'src'] and value \
                   and not value.startswith('javascript:') and not value.startswith('vbscript:'):
                    self.links.append(value)
                    #print attr, value

    def handle_data(self, data):
        if self.is_content:
            self.content += data
        if self.is_title:
            self.title += data

    def handle_endtag(self, tag):
        pass


def get_response(url, **kwargs):
    if kwargs:
        data = urllib.urlencode(kwargs)
        request = urllib2.Request(url, data)
    else:
        request = urllib2.Request(url)
    
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                                     + 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 '
                                     + 'Safari/537.36 WandaiSpider/0.1')

    response = urllib2.urlopen(request)
    return response


def get_news():
    links = []
    for y in range(2000, 2020):
        for m in range(1, 13):
            url = 'http://news.tsinghua.edu.cn/publish/thunews/newsCollections/d_{0}_{1}.json'.format(y, m)
            try:
                j = json.loads(get_response(url).read())['data']
                for k, v in j.items():
                    for item in v:
                        links.append('http://news.tsinghua.edu.cn/' + item['htmlurl'][:-5] + '_.html')
            except Exception as e:
                print 'Error({0}) {1}'.format(e, url)
    return list(set(links))


def load_news():
    with open('links.txt', 'r') as f:
        links = [l.strip() for l in f]
    return links


def get_initial_urls():
    links = []
    for page in Page.objects.order_by('-download_at').all():
        current_link = page.url
        parser = SpiderParser()
        try:
            response = get_response(current_link)
            info = response.info()
            if info.getheader('Content-Type') not in ['text/html']:
                print 'Ignore(type={0}) {1}'.format(info.getheader('Content-Type'), current_link)
                continue
            print 'Load {0}'.format(current_link)
            parser.feed(response.read())
            print 'Loaded {0}'.format(len(links))
            for link in parser.links:
                link = urlparse.urljoin(current_link, link)
                link = link.split('#')[0]
                if not Page.objects.filter(url=link).exists():
                    links.append(link)
        except (urllib2.URLError, urllib2.HTTPError, UnicodeDecodeError) as e:
            continue
        if len(links) > 1000:
            break
    return list(set(links))


if __name__ == '__main__':
    Q = Queue.Queue()
    try:
        domains = ['news.tsinghua.edu.cn', 'www.tsinghua.edu.cn']
        # initial url
        print 'Initializing'
        for link in get_initial_urls():
            Q.put(link)
        # for link in load_news():
        #     Q.put(link)
        while not Q.empty():
            try:
                current_link = Q.get()
                current_domain = urlparse.urlparse(current_link).netloc.split(':')[0]
                if not any(current_domain.endswith(domain) for domain in domains):
                    print 'Ignore(domain={0}) {1}'.format(current_domain, current_link)
                    continue
                if Page.objects.filter(url=current_link).exists():
                    print 'Ignore(exists) {0}'.format(current_link)
                    continue
                parser = SpiderParser()
                try:
                    response = get_response(current_link)
                    info = response.info()
                    if info.getheader('Content-Type') not in ['text/html']:
                        print 'Ignore(type={0}) {1}'.format(info.getheader('Content-Type'), current_link)
                        continue
                    print 'Fetch {0}'.format(current_link)
                    parser.feed(response.read())
                    print 'Fetched'
                except Exception as e:
                    print 'Error({0}) {1}'.format(e, current_link)
                    continue
                # TODO(twd2): update_at, hash
                parser.title = parser.title.strip()
                parser.content = parser.content.strip()
                page = Page(title=parser.title, content=parser.content,
                            download_at=timezone.now(), update_at=timezone.now(),
                            url=current_link, hash='')
                try:
                    page.save()
                    print 'Enqueuing {0} links'.format(len(parser.links))
                    for link in parser.links:
                        link = urlparse.urljoin(current_link, link)
                        link = link.split('#')[0]
                        if not Page.objects.filter(url=link).exists():
                            Q.put(link)
                except Exception as e:
                    print 'Error({0}) {1}'.format(e, current_link)
            except Exception as e:
                print 'Error({0})'.format(e)
    except KeyboardInterrupt as e:
        pass
        # print list(downloaded)
        # while not Q.empty():
        #     print Q.get()