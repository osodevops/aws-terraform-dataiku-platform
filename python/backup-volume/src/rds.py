from aws import Aws


class Rds:
    aws_handler: Aws

    def __init__(self, aws_handler: Aws):
        self.aws_handler = aws_handler

    def create_snapshot(self, additional_tags):
        self.aws_handler.create_rds_snapshot(additional_tags=additional_tags)
