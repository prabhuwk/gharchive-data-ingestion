import os
import boto3
import requests
import logging
from requests.models import Response
from datetime import datetime, timedelta
from botocore.errorfactory import ClientError

# configure info level logging
logging.getLogger().setLevel(level=logging.INFO)


def download_file(file_name: str) -> Response:
    """download file using requests"""
    base_url = "https://data.gharchive.org"
    file_path = f"{base_url}/{file_name}"
    logging.info(f"Downloading file: {file_path}")
    return requests.get(file_path)


def previous_file_name(
    bucket_name: str, base_file_name: str, bookmark_file_path: str
) -> str:
    """get previous file name"""
    s3_client = get_s3_client()
    try:
        bookmark_file = s3_client.get_object(Bucket=bucket_name, Key=bookmark_file_path)
        return bookmark_file.get("Body", {}).read().decode("utf-8")
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "NoSuchKey":
            return base_file_name
    return base_file_name


def next_file_name(previous_file: str) -> str:
    """get next file name"""
    datetime_part = previous_file.split(".")[0]
    return f"{datetime.strftime(datetime.strptime(datetime_part, '%Y-%M-%d-%H') + timedelta(hours=1), '%Y-%M-%d-%-H')}.json.gz"


def get_s3_client():
    """get s3 client object"""
    return boto3.client("s3")


def upload_file(bucket_name: str, file_path: str, content: str) -> dict:
    """upload file to given s3 bucket"""
    s3_client = get_s3_client()
    logging.info(f"Uploading file: {file_path}")
    return s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=content)


def upload_bookmark(bucket_name: str, bookmark_path: str, content: str) -> dict:
    """upload bookmark file"""
    s3_client = get_s3_client()
    logging.info(f"Uploading bookmark file: {bookmark_path}")
    return s3_client.put_object(Bucket=bucket_name, Key=bookmark_path, Body=content)


# main entry point for lambda function
def lambda_handler(event, context):
    upload_file_response = dict()
    base_file_name = os.environ.get("BASE_FILE_NAME")
    bucket_name = os.environ.get("BUCKET_NAME")
    path_prefix = os.environ.get("PATH_PREFIX")
    bookmark_file = os.environ.get("BOOKMARK_FILE")
    bookmark_path = f"{path_prefix}/{bookmark_file}"
    while True:
        previous_file = previous_file_name(bucket_name, base_file_name, bookmark_path)
        file_name = next_file_name(previous_file)
        response = download_file(file_name)
        if response.status_code == 404:
            logging.error(
                f"Invalid file name or downloads caught up till {previous_file}."
            )
            break
        logging.info(f"Successfully downloaded {file_name} file !")
        file_path = f"{path_prefix}/{file_name}"
        upload_file_response = upload_file(bucket_name, file_path, response.content)
        if (
            not upload_file_response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            == 200
        ):
            logging.error(f"Unable to upload {file_path} file")
        upload_bookmark(bucket_name, bookmark_path, file_name)
    return upload_file_response
