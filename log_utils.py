import os
import sys

from loguru import logger as logging

import settings


def mkdir(path: str) -> bool:
    path = path.rstrip("/")
    os.makedirs(path, exist_ok=True)
    return os.path.exists(path)


class Logger:
    def __init__(self, log_name: str = settings.log_name):
        log_file_path = log_name
        self._logger = logging
        self._logger.remove()
        self._add_stdout_logger()
        self._add_file_logger(log_file_path)

    def _add_stdout_logger(self):
        self._logger.add(
            sys.stdout,
            level=settings.stdout_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level:8}</level> | "
                   "<magenta>{module}.{function}:{line}</magenta> - "
                   "<level>{message}</level>",
            diagnose=False,
            enqueue=False,
        )

    def _add_file_logger(self, log_file_path):
        self._logger.add(
            log_file_path,
            level=settings.file_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | "
                   "{level:8} | "
                   "{module}.{function}:{line} - "
                   "{message} -- "
                   "{name}",
            diagnose=False,
        )

    @property
    def logger(self):
        return self._logger


logger = Logger().logger

if __name__ == "__main__":
    logger.debug("debug")
    logger.info("test")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
