#!/isr/bin/python3
#coding=utf-8

import sys
import argparse
import threading
import asyncio
import re
import chardet
import aiohttp
import ssl
import csv

ssl._create_default_https_context = ssl._create_unverified_context

class WebTitle:

    def __init__(self, urls, thread_count=20):
        self.urls = urls
        self.thread_count = thread_count
        self.result = {}

    def init_queue(self):
        queue = asyncio.Queue()
        for url in self.urls:
           queue.put_nowait(url)
        return queue

    def get_title_from_html(self, html):
        title = 'not content!'
        title_patten = r'<title>(\s*?.*?\s*?)</title>'
        result = re.findall(title_patten, html)
        if len(result) >= 1:
            title = result[0]
            title = title.strip()
        return title

    async def get_title(self):
        while True:
            url = await self.queue.get()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=3, ssl=ssl.SSLContext()) as resp:
                        html = await resp.text()
                title = self.get_title_from_html(html)
                print('{}:{}'.format(url,title))
                self.result[url] = title
            except Exception as e:
                pass                
            self.queue.task_done()

    async def start_task(self):
        self.queue = self.init_queue()
        tasks = []
        for i in range(self.thread_count):
            task = asyncio.create_task(self.get_title())
            tasks.append(task)

        await self.queue.join()
        
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        

    def start(self):
        asyncio.run(self.start_task())

    def write_result(self, outfile):
        with open(outfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['url','title'])
            urls = self.result.keys()
            for url in urls:
                title = self.result[url]
                writer.writerow([url, title])
        print('result write to {}'.format(outfile))

def parse_args():
    parser = argparse.ArgumentParser(description='A tool that can get title for domains or urls')
    parser.add_argument('-d','--domain', metavar='domain.txt', dest='domain_file', type=str, help=u'domain to get title')
    parser.add_argument('-u','--url', metavar='url.txt', dest='url_file', type=str, help=u'urls to get title')
    parser.add_argument('-t','--thread', metavar='20', dest='thread_count', type=int, default=20,help=u'threads to get title')
    parser.add_argument('-o','--outfile', metavar='result.txt', dest='outfile', type=str, default='result.csv',help=u'file to result')
    args = parser.parse_args()
    if args.url_file == None and args.domain_file == None:
        parser.print_help()
        sys.exit()
    return args


def main():
    args = parse_args()
    urls = []
    if args.domain_file:
        with open(args.domain_file) as f:
            domains = f.readlines()
        for domain in domains:
            urls.append('http://' + domain.strip())
            urls.append('https://' + domain.strip())

    if args.url_file:
        with open(args.url_file) as f:
            urls2 = f.readlines()
        for url in urls2:
            urls.append(url.strip())
    web_title = WebTitle(urls, args.thread_count)
    web_title.start()
    web_title.write_result(args.outfile)

if __name__ == '__main__':
    main()

