import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from queue import Empty

import requests

from base.base_crawler import BaseCrawler
from utils.logger import Logger
import time


class MultiThreadedCrawler(BaseCrawler):
    def __init__(self, seed_url, number_of_thread, number_of_link_to_extract, filename) -> None:
        super().__init__(seed_url, number_of_link_to_extract, filename)
        self.logger = Logger(__name__)
        self.number_of_thread = number_of_thread
        self.pool = ThreadPoolExecutor(max_workers=number_of_thread)

    def scrape_page(self, url):
        try:
            res = requests.get(url, timeout=(3, 30), headers={'User-Agent': 'Mozilla/5.0'})
            self.logger.log_info(f'{url} ----->>>>>>> {res.status_code}', 'info2001')
            if res.status_code == 200 and "text/html" in res.headers["Content-Type"]:
                return res
            else:
                self.number_of_failed_page += 1
        except requests.RequestException as e:
            self.logger.log_error(str(e), 'err1001')

    def run_crawler(self):
        while True:
            try:
                if self.number_of_scraped_page >= self.number_of_link_to_extract:
                    return

                url_list = list()
                while len(url_list) < self.number_of_thread:
                    if len(url_list) > self.url_queue.qsize():
                        break
                    target_url = self.url_queue.get(timeout=60)
                    if target_url not in self.visited_url:
                        self.current_scraping_url = "{}".format(target_url)
                        print("Scraping URL: {}".format(target_url))
                        self.visited_url.add(target_url)
                        url_list.append(target_url)

                futures = self.pool.map(self.scrape_page, url_list)

                for future in futures:
                    self.post_scrape_callback(future)

            except Empty:
                return
            except Exception as e:
                print(e)
                continue

    def info(self):
        print('\n Seed URL is: ', self.seed_url, '\n')
        print('Number of crawled page: ', self.number_of_scraped_page, '\n')
        print('Number of crawled page failed ', self.number_of_failed_page, '\n')
        print(f'Size of queue after crawling : {self.url_queue.qsize()}\n')
        print(f'Number of same url found: {len(self.url_repeated)}\n')

    def start(self):
        start_time = time.time()
        self.run_crawler()
        self.info()
        end_time = time.time()

        print(f"Time taken: {end_time - start_time} seconds")
        self.pool.shutdown(wait=True)
