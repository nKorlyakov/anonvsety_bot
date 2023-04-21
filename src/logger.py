# Logger file
from loguru import logger
import config


class CustomLogger:
    def __init__(self):
        self.levels_log = {'INFO': logger.info,
                           'WARNING': logger.warning,
                           'ERROR': logger.error
        }
        logger.add('../logs/info.log', level='INFO', rotation='1 day', compression='zip')
        logger.add('../logs/warning.log', level='WARNING', rotation='10 KB', compression='zip')
        logger.add('../logs/error.log', level='ERROR', rotation='10 KB', compression='zip')


    def send_to_file(self, message: str, level: str) -> None:
        '''
        Отправляет лог сообщение в файл и консоль
        '''
        self.levels_log[level](message)

