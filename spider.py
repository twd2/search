# encoding=utf-8
import os
import urllib
import urllib2
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
        self.is_content = tag not in ['script', 'style', 'title']
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
                                     + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     + 'Chrome/52.0.2743.116 Safari/537.36 '
                                     + 'WandaiSpider/0.1')

    response = urllib2.urlopen(request)
    return response


def get_initial_urls():
    links = []
    for page in Page.objects.order_by('-download_at').all():
        current_link = page.url
        parser = SpiderParser()
        try:
            response = get_response(current_link)
            info = response.info()
            if not any(info.getheader('Content-Type').find(t) >= 0 for t in ['text/html']):
                print 'Ignore(type={0}) {1}'.format(info.getheader('Content-Type'), current_link)
                continue
            print 'Load {0}'.format(current_link)
            parser.feed(decode_chinese(response.read()))
            print 'Loaded {0} links'.format(len(links))
            for link in parser.links:
                link = urlparse.urljoin(current_link, link)
                link = link.split('#')[0]
                if not Page.objects.filter(url=link).exists():
                    links.append(link)
        except Exception as e:
            continue
        # 1000 is enough?
        if len(links) > 1000:
            break
    return list(set(links))


def decode_chinese(s):
    try:
        return s.decode('utf-8')
    except:
        return s.decode('gb18030', 'ignore')


def load_links_from_file(file):
    try:
        with open(file, 'r') as f:
            return [l.strip() for l in f]
    except Exception as e:
        print('Error no link in file {0}'.format(file))
        return []


if __name__ == '__main__':
    Q = Queue.Queue()
    try:
        domains = ['twd2.me', 'twd2.net', 'vijos.org', 'news.tsinghua.edu.cn', 'www.tsinghua.edu.cn']
        # initial url
        print 'Initializing'
        for link in load_links_from_file('links/left_links.txt'):
            Q.put(link)
        for link in get_initial_urls():
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
                parser = SpiderParser()
                try:
                    response = get_response(current_link)
                    info = response.info()
                    if not any(info.getheader('Content-Type').find(t) >= 0 for t in ['text/html']):
                        print 'Ignore(type={0}) {1}'.format(info.getheader('Content-Type'),
                                                            current_link)
                        continue
                    print 'Fetch {0}'.format(current_link)
                    parser.feed(decode_chinese(response.read()))
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
        with open('links/left_links.txt', 'w') as f:
            while not Q.empty():
                f.write(Q.get() + u'\n')
        print('Exiting')
