from aws_helper.helper import AwsHelper

helper = AwsHelper()

file = helper.get_file_from_s3({'bucket_name': 'dataiku-dss-config', 'key': ''})


print(file)

