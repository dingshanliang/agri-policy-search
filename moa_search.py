import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re

# 创建 Chrome 选项
options = Options()
options.add_argument("--headless")  # 设置为无头模式，即不显示浏览器界面
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 使用 Chrome 选项创建 Chrome 服务
service = Service("/usr/local/bin/chromedriver")

# 启动 Chrome 浏览器
driver = webdriver.Chrome(service=service, options=options)

def parse_page(driver):
# 获取页面源代码
    html_content = driver.page_source

# 使用 BeautifulSoup 解析页面源代码
    soup = BeautifulSoup(html_content, 'html.parser')

# 找到所有的新闻元素
    news = soup.select('#results > div')
    results = []
    for new in news:
        title = new.select_one('div.title > a').text
    # #results > div:nth-child(20) > div > div.content > div
        date = new.select_one('div.content > div').text
    # 从 农业农村部-2021-09-01 格式中提取日期
        match = re.search(r'\d{4}-\d{2}-\d{2}', date)
        if match:
            date = match.group()
        link = new.select_one('div.title > a')['href']
        results.append({'title': title, 'date': date, 'link': link})

    return results


def click_next_page(driver):
    try:
        print("正在点击下一页...")
        print(driver)
        next_page = driver.find_element("xpath", '//a[@class="next"]')
        next_page.click()
    except Exception as e:
        print("Error: ", e)
    

def moa_query(query, max_pages=2):

    results_news = []
    pages = 1
    # 访问首页
    driver.get("http://www.moa.gov.cn/so/s?qt={query}&tab=gk".format(query=query))
    results_news.extend(parse_page(driver))
    print("第{pages}页：{results}".format(pages=pages, results=results_news))
    time.sleep(5)

    # 点击下一页
    while True:
        if pages >= max_pages:
            break
        try:
            click_next_page(driver)
            #生成随机等待时间，防止被网站识别为爬虫
            wait_time = random.randint(5, 8)
            time.sleep(wait_time)
            # parse_page(driver, query=query)
            results_news.extend(parse_page(driver))
            pages += 1
            print("-"*100)
            print("第{pages}页：{results}".format(
                pages=pages, results=results_news))
        except Exception as e:
            print("Error: ", e)
            break
    
    # 关闭浏览器
    # driver.quit()
    return results_news


temp_list = moa_query("数字乡村", max_pages=3)
print(temp_list)