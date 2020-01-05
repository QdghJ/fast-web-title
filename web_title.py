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
import IPy

ssl._create_default_https_context = ssl._create_unverified_context

class WebTitle:

    def __init__(self, urls, coroutine_count=20):
        self.urls = list(set(urls))
        self.coroutine_count = coroutine_count
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

    async def get_title(self, queue):
        while True:
            url = await queue.get()
            print('get title for {}'.format(url))
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=3, ssl=ssl.SSLContext()) as resp:
                        html = await resp.text()
                title = self.get_title_from_html(html)
                print('{}:{}'.format(url,title))
                self.result[url] = title
            except Exception as e:
                print('{} has error: {} '.format(url,str(e)))                
            queue.task_done()

    async def start_task(self):
        queue = self.init_queue()
        tasks = []
        for i in range(self.coroutine_count):
            task = asyncio.create_task(self.get_title(queue))
            tasks.append(task)

        await queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)


    def start(self):
        asyncio.run(self.start_task())

    def write_result(self, outfile):
        urls = self.result.keys()
        with open(outfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['url','title'])
            for url in urls:
                title = self.result[url]
                writer.writerow([url, title])
        with open(outfile + '_alive.txt', 'w') as f:
            for url in urls:
                f.write(url + '\n')
        
        print('alive urls write to {}'.format(outfile + '_alive.txt'))
        print('title write to {}'.format(outfile))

def parse_args():
    parser = argparse.ArgumentParser(description='A tool that can get title for domains or urls')
    parser.add_argument('-d','--domain', metavar='domain.txt', dest='domain_file', type=str, help=u'domain to get title')
    parser.add_argument('-u','--url', metavar='url.txt', dest='url_file', type=str, help=u'urls to get title')
    parser.add_argument('-i','--ip', metavar='ip.txt', dest='ip_file', type=str, help=u'ips to get title')
    parser.add_argument('-t','--coroutine', metavar='20', dest='coroutine_count', type=int, default=20,help=u'coroutines to get title')
    parser.add_argument('-o','--outfile', metavar='result.txt', dest='outfile', type=str, default='result.csv',help=u'file to result')
    args = parser.parse_args()
    if args.url_file == None and args.domain_file == None and args.ip_file == None:
        parser.print_help()
        sys.exit()
    return args


def main():
    try:
        args = parse_args()
        urls = []

        if args.domain_file:
            with open(args.domain_file) as f:
                domains = f.readlines()
            for domain in domains:
                domain = domain.strip()
                if domain != '':
                    urls.append('http://' + domain)
                    urls.append('https://' + domain)

        if args.url_file:
            with open(args.url_file) as f:
                urls2 = f.readlines()
            for url in urls2:
                url = url.strip()
                if url != '':
                    urls.append(url)

        if args.ip_file:
            with open(args.ip_file) as f:
                ips = f.readlines()
            for ip in ips:
                ip = ip.strip()
                if ip != '':
                    # cidr_ip = IPy.IP(ip)
                    cidr_ip = IPy.IP(ip, make_net=1)
                    for i in cidr_ip:
                        urls.append('http://' + str(i))
                        urls.append('https://' + str(i))

        web_title = WebTitle(urls, args.coroutine_count)
        web_title.start()
        web_title.write_result(args.outfile)
    except Exception as e:
        print(e)

def banner():
    print('''                                             
  __           _                  _       _   _ _   _      
 / _| __ _ ___| |_  __      _____| |__   | |_(_) |_| | ___ 
| |_ / _` / __| __| \ \ /\ / / _ \ '_ \  | __| | __| |/ _ \ 
|  _| (_| \__ \ |_   \ V  V /  __/ |_) | | |_| | |_| |  __/
|_|  \__,_|___/\__|   \_/\_/ \___|_.__/   \__|_|\__|_|\___|
                                                           ''')


if __name__ == '__main__':
    banner()
    main()

