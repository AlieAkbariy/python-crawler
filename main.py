from crawler.multithreaded_crawler import MultiThreadedCrawler

multi_thread_crawler = MultiThreadedCrawler('https://yazd.ac.ir', 16, 12000, 'output.txt')
multi_thread_crawler.start()
