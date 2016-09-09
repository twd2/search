# encoding=utf-8
import urllib
import urllib2
import json


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


if __name__ == '__main__':
    for link in get_news():
        print(link)