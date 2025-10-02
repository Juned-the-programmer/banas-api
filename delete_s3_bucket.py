import os

import boto3
import django
from django.conf import settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banas.settings")
django.setup()


def delete_all_files():
    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket.objects.all().delete()
    print("✅ All files deleted successfully!")


if __name__ == "__main__":
    delete_all_files()


# def delete_file_from_s3(file_key):
#     """
#     Deletes a file from S3 bucket.
#     :param file_key: str -> path or key of the file inside S3 bucket.
#     :return: bool -> True if deleted successfully, False otherwise.
#     """
#     s3_client = boto3.client(
#         "s3",
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         region_name=settings.AWS_S3_REGION_NAME,
#     )

#     try:
#         s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_key)
#         return True
#     except ClientError as e:
#         logging.error(f"Error deleting file {file_key}: {e}")
#         return False
