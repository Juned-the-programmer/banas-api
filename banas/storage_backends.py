from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError

class CustomS3Boto3Storage(S3Boto3Storage):
    def exists(self, name):
        try:
            return super().exists(name)
        except ClientError as e:
            # If the error is 410 Gone, treat it as "file does not exist"
            if e.response.get('Error', {}).get('Code') == '410':
                return False
            raise e
