from utils.logger import Logger


class IOHandler:
    def __init__(self, file_path):
        self.file = open(file_path, 'w')
        self.logger = Logger('__module__')

    def write_data(self, data):
        try:
            self.file.write(str(data))
        except Exception as e:
            self.logger.log_error(str(e), 'err2001')
