import re
from abc import ABC, abstractmethod
from queue import Queue
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from utils.io_handler import IOHandler
from utils.logger import Logger
import ssl


class BaseCrawler(ABC):
    def __init__(self, seed_url, number_of_link_to_extract, filename) -> None:
        """
        initial method for base crawler
        :param seed_url: start url
        :param number_of_link_to_extract:
        """

        # define attribute
        self.seed_url = seed_url
        self.hostname = urlparse(seed_url).netloc  # get hostname
        self.number_of_link_to_extract = number_of_link_to_extract
        self.current_scraping_url = seed_url
        self.number_of_scraped_page = 0
        self.number_of_failed_page = 0

        self.visited_url = set([])
        self.url_queue = Queue()
        self.url_queue.put(seed_url)

        self.url_repeated = dict()
        self.output_file = IOHandler(filename)
        self.logger = Logger(__name__)

        my_ssl = ssl.create_default_context()
        my_ssl.check_hostname = False
        my_ssl.verify_mode = ssl.CERT_NONE

    def __is_url_same(self, url_1, url_2):
        try:
            return self.__normalize_url(url_1) == self.__normalize_url(url_2)
        except Exception as e:
            self.logger.log_error(str(e), 'err1001')
            return False

    def __is_url_visited(self, url):
        try:
            for u in self.visited_url:
                if self.__is_url_same(url, u):
                    self.url_repeated[self.__normalize_url(url)] += 1
                    return True
            self.url_repeated[self.__normalize_url(url)] = 1
            return False
        except Exception as e:
            self.logger.log_error(str(e), 'err1002')
            return False

    def __is_url_valid(self, url):
        try:
            url_parser = urlparse(url)

            head = requests.head(url)
            if url_parser.netloc == self.hostname and 'text/html' in head.headers['Content-Type']:
                return True
            return False
        except Exception as e:
            self.logger.log_error(str(e), 'err1003')
            return False

    def __normalize_data(self, soup):
        try:
            title = soup.find('title')
            body = soup.find('body')

            if title is not None:
                title = title.text.replace('\n', '').replace('\t', '').replace('\r', '')
                title = re.sub('\s+', ' ', title)

            if body is not None:
                body = body.text.replace('\n', '').replace('\t', '').replace('\r', '')
                body = re.sub('\s+', ' ', body)

            html = soup.find('html')

            return title, body, html
        except Exception as e:
            self.logger.log_error(str(e), 'err1004')

    def __build_data_from_response(self, response):
        try:
            soup = BeautifulSoup(response, "html.parser")
            title, body, html = self.__normalize_data(soup)
            page_data = {
                "URL": self.current_scraping_url,
                "Title": title,
                "Body": body,
                "Html": html
            }

            return page_data
        except Exception as e:
            self.logger.log_error(str(e), 'err1005')

    def __normalize_url(self, url):
        try:
            url_parser = urlparse(url)
            return url_parser.netloc + url_parser.path
        except Exception as e:
            self.logger.log_error(str(e), 'err1006')

    def __link_extractor(self, response):
        try:
            soup = BeautifulSoup(response, 'html.parser')
            anchor_tags = soup.find_all('a', href=True)
            for link in anchor_tags:
                url = link['href']
                url_parser = urlparse(url)

                if url_parser.scheme == '':
                    url = self.current_scraping_url + url
                if url_parser.netloc == self.hostname:
                    if url not in self.visited_url:
                        self.url_queue.put(url)
                        self.url_repeated[self.__normalize_url(url)] = 1
                    else:
                        self.url_repeated[self.__normalize_url(url)] += 1

        except Exception as e:
            self.logger.log_error(str(e), 'err1007')

    def __write_to_output_file(self, response):
        try:
            page_data = self.__build_data_from_response(response)
            self.output_file.write_data(data=page_data)
        except Exception as e:
            self.logger.log_error(str(e), 'err1008')

    def post_scrape_callback(self, response):
        response = response.text
        self.__link_extractor(response)
        self.__write_to_output_file(response)
        self.number_of_scraped_page += 1
