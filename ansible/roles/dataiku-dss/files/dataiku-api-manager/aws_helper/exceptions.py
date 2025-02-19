import logging


class AwsHelperException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        print(f"{message}, {errors}")
