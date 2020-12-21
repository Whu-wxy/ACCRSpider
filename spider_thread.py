import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
import re
import multiprocessing as mp
import os
from urllib.parse import urljoin
import random
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
from queue import Queue
from Download_thread import ThreadWrite
import json
import config

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}



# proxies = {'http':'http://117.88.5.202',
#            'https':'https://117.88.177.33',
#             'https':'https://119.254.94.93',
#             'https':'https://117.88.5.27',
#             'https':'https://125.73.220.18',
#             'https':'https://117.88.176.110',
#            }


#解析网页数据
def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    with open('./save2.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 找出所有图片url
    url_feature = '^[\s\S]*(' + 'shufa' + ')[\s\S].*gif$'
    imgs = soup.find_all("img", {"src": re.compile(url_feature)}, recursive=True)

    img_links = []
    img_names = []
    for link in imgs:
        alt = link.attrs['alt']
        link = link['src']

        if len(link) < 2:
            continue
        link = link.replace("\n", "")
        link = link.replace("\r", "")
        img_links.append(link.strip())
        img_names.append(alt.strip())

    return img_names, img_links

#下载网页
async def crawl(url, session):
    print('正在爬取: ', url)
    try:
        r = await session.get(url, headers=headers)   #, proxy = 'http://117.88.5.202'
        html = await r.text("gb18030","ignore")    #utf-8改为gb18030
        await asyncio.sleep(random.uniform(2, 5))       # slightly delay for downloading
        return (html)
    except Exception as e:
        print(repr(e))
        return ('')


async def main(loop):
    pool = mp.Pool(2)               # slightly affected


    #读json文件，存到word_list
    # f = open("catestest.json", encoding='utf-8')
    # settings = json.load(f)
    # word_list = []
    # for setting in settings:
    #     a_gb2312 = setting['text'].encode('gb2312')
    #
    #     a_gb2312 = str(a_gb2312)
    #     a_gb2312 = a_gb2312.replace("\\x", "")
    #     a_gb2312 = a_gb2312[2:-1]
    #
    #     a_gb2312 = '%' + a_gb2312[:2] + '%' + a_gb2312[-2:]
    #     word_list.append(a_gb2312)

    word_list = []
    with open('GB1_3.txt', encoding='utf-8') as f:
        words = f.read().strip().strip('\ufeff')
        for word in words:
            word = word.encode('gb2312')
            word = str(word)
            word = word.replace("\\x", "")
            word = word[2:-1]
            word = '%' + word[:2] + '%' + word[-2:]
            word_list.append(word)

    async with aiohttp.ClientSession() as session:
        while len(word_list) != 0:
            # 队列中还有config.thread_num*10个以上的图未下载时，不下载解析网页
            if img_queue.qsize() > config.thread_num*10:
                time.sleep(1)
                continue

            tasks = [loop.create_task(crawl(config.base_url+word, session)) for word in word_list[:5]]
            for i in range(5):
                if len(word_list)==0:
                    break
                word_list.pop(0)


            finished, unfinished = await asyncio.wait(tasks)
            htmls = [f.result() for f in finished]

            parse_jobs = [pool.apply_async(parse, args=(html,)) for (html) in htmls]
            results = [j.get() for j in parse_jobs]

            for img_names, img_links in results:
                for name, link in zip(img_names, img_links):
                    img_queue.put((name, link))



if __name__ == "__main__":
    img_queue = Queue()

    URLValid = True
    if len(config.base_url) < 4:
        URLValid = False
        print('请输入要爬取的网站地址！')
    elif not config.base_url.startswith('http'):
        URLValid = False
        print('请输入格式正确的网站地址！')
    elif URLValid:
        print('将爬取所有网页图片！手动停止(Ctrl+C)或爬取完所有网页！')

        print('开始从%s爬取图片...' % config.base_url)

        thread_list = []
        loadList = []
        for i in range(config.thread_num):
            loadList.append('线程'+str(i))
        for threadName in loadList:
            Ithraad = ThreadWrite(threadName, img_queue)
            Ithraad.start()
            thread_list.append(Ithraad)

        t1 = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
        loop.close()
        print("Total time: ", time.time() - t1)

        print('等待图片下载...')

        for thread in thread_list:
            thread.THREAD_EXIT = True
            thread.join()

    print('结束！')

