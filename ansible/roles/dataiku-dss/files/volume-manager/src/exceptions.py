import logging


class VolumeException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        logging.critical(f"{message}, {errors}")


class HandlerException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        print('Handler Errors:')
        print(errors)