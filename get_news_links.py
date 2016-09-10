# encoding=utf-8
import json
import spider


def get_news():
    links = []
    for y in range(2000, 2020):
        for m in range(1, 13):
            url = 'http://news.tsinghua.edu.cn/publish/thunews/newsCollections/d_{0}_{1}.json'.format(y, m)
            try:
                j = json.loads(spider.get_response(url).read())['data']
                for k, v in j.items():
                    for item in v:
                        links.append('http://news.tsinghua.edu.cn/' + item['htmlurl'][:-5] + '_.html')
            except Exception as e:
                print('Error({0}) {1}'.format(e, url))
    return list(set(links))


if __name__ == '__main__':
    for link in get_news():
        print(link)