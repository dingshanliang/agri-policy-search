from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import re
import datetime
import time
import html2text


html2text = html2text.HTML2Text()
html2text.ignore_links = True
html2text.ignore_images = True
html2text.ignore_emphasis = True
html2text.ignore_tables = True

crawl_target = [
    "http://www.moa.gov.cn/xw/bmdt/",  # 部门新闻
    "http://www.moa.gov.cn/xw/zwdt/",    # 农业农村部动态
    "http://www.moa.gov.cn/xw/qg/"      # 全国信息联播
]
class_xw = "TRS_Editor"
class_public = "ggnr"


class MoaNewsListCrawler():
    def __init__(self, url):
        self.url = url
        self.news_list = []
    
    def get_news_list(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('li.ztlb'):
            title = item.select_one('a').text.strip()
            title = re.sub(r'\s+', '', title)
            link = item.select_one('a')['href']

            # 链接拼接处理，如果以.开头则将.替换为 url
            if link.startswith('.'):
                link = self.url + link[2:]  # 链接拼接处理，如果以.开头则将第一个.替换为 url

            date = item.select_one('span').text.strip()
            self.news_list.append({'title': title, 'date': date,'link': link})
        return self.news_list


class MoaArticleCrawler():

    def __init__(self, url, class_=class_xw):
        self.url = url  
        self.article = None
        self.html2text = html2text.handle
        self.soup = None
        self.class_ = class_

    def get_article(self):
        self.soup = self.get_soup()
        article = self.soup.find('div', class_=self.class_)
        self.article = self.html2text(str(article))
        self.article = re.sub(r'\n\n', '\n', self.article)
        self.article = re.sub(r',\n', '', self.article)
        self.article = self.article.strip().lstrip(
            "[").lstrip("\n").rstrip("\n").rstrip("]")
        return self.article

    def get_soup(self):
        response = requests.get(self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def __call__(self, *args, **kwds):
        self.article = self.get_article()
        return self.article


def get_moa_news(max=5):
    temp_news_list = []
    for url in crawl_target:
        moa_news_list_crawler = MoaNewsListCrawler(url)
        news_list = moa_news_list_crawler.get_news_list()
        for news in news_list:
            moa_article_crawler = MoaArticleCrawler(news['link'])
            article = moa_article_crawler.get_article()
            temp_news_list.append({'title': news['title'], 'link': news['link'], 'date': news['date'], 'article': article})
            if len(temp_news_list) == max:
                return temp_news_list
            time.sleep(1)
    return temp_news_list

if __name__ == '__main__':
    moa = MoaNewsListCrawler("http://www.moa.gov.cn/xw/zwdt/")
    news = moa.get_news_list()
    print(news)
