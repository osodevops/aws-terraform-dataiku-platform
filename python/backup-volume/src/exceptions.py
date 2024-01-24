import logging


class BackupException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        logging.warning(f"{message}, {errors}")
