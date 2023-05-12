import logging


class Logger:
    def __init__(self, module_name):
        # set up logger
        logging.basicConfig(
            filename='crawler.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='w'
        )
        self.logger = logging.getLogger(module_name)

    def log_debug(self, message, identifier):
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f'{identifier} -> {message}')

    def log_info(self, message, identifier):
        self.logger.setLevel(logging.INFO)
        self.logger.info(f'{identifier} -> {message}')

    def log_warning(self, message, identifier):
        self.logger.setLevel(logging.WARNING)
        self.logger.warning(f'{identifier} -> {message}')

    def log_error(self, message, identifier):
        self.logger.setLevel(logging.ERROR)
        self.logger.error(f'{identifier} -> {message}')

    def log_critical(self, message, identifier):
        self.logger.setLevel(logging.CRITICAL)
        self.logger.critical(f'{identifier} -> {message}')

# test
# log = Logger(__name__)
# log.log_debug('Hi', 'debug254125')
# log = Logger('ALI')
# log.log_debug('HIHIHIH', 'debug124512')
