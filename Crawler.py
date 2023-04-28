import requests
from bs4 import BeautifulSoup
import re
from url_normalize import url_normalize
import threading
import time

class Crawler:
    def __init__(self, start_url):
        self.queue_dict = dict()
        self.queue_list = list()
        self.queue_list.append(start_url)
        self.crawled_page = 0

    def link_extractor(self, soup_object, base_url):
        links = soup_object.find_all('a')
        for link in links:
            url = link.get('href')
            
            check = url not in self.queue_dict
            
            if check and url is not None:
                if 'http' not in url and 'yazd.ac.ir' in url:
                    url = base_url + url

                if 'yazd.ac.ir' in url:
                    self.queue_list.append(url_normalize(url))

    def worker(self):
        json_file = open(f'output.txt', 'w')
        while True:
            if self.crawled_page >= 50:
                break
            
            url = None
            if len(self.queue_list) > 0:
                url = self.queue_list.pop()
            if url is not None:
                check_unique = self.queue_dict.get(url)
                if check_unique is None:
                    try:
                        page = requests.get(url, timeout=60)
                    except:
                        continue
                    soup = BeautifulSoup(page.content, "html.parser")
                    self.link_extractor(soup, url)
                    try:
                        title = soup.find('title')
                        title = title.text.replace('\n', '').replace('\t', '').replace('\r', '')
                        title = re.sub('\s+', ' ', title)

                        body = soup.find('body')
                        body = body.text.replace('\n', '').replace('\t', '').replace('\r', '')
                        body = re.sub('\s+', ' ', body)

                        html = soup.find('html')

                        page_data = {
                            'URL': url,
                            "Title": title,
                            "Body": body,
                            "Html": html
                        }

                        json_file.write(str(page_data))
                        self.queue_dict[url] = 1
                        self.crawled_page += 1
                        print(f'thread crawled {self.crawled_page} : {url}')
                    except:
                        pass
        json_file.close()


    def start(self):
        start_time = time.time()
        # threads = []
        # for i in range(8):
        #     t = threading.Thread(target=self.worker, name=str(i))
        #     threads.append(t)

        # # Start the threads
        # for thread in threads:
        #     thread.start()

        # # Wait for all threads to finish
        # for thread in threads:
        #     thread.join()
        self.worker()
        end_time = time.time()
        
        print(f"Time taken: {end_time - start_time} seconds")

