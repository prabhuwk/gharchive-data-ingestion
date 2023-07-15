import os
import requests
import logging
from requests.models import Response

# configure info level logging
logging.basicConfig(level=logging.INFO)


def download_file(file_name: str) -> Response:
    base_url = "https://data.gharchive.org"
    file_path = f"{base_url}/{file_name}"
    logging.info(f"Downloading file: {file_path}")
    return requests.get(file_path)


# main entry point for lambda function
def lambda_handler(event, context):
    file_name = os.environ.get("BASE_FILE_NAME")
    response = download_file(file_name)
    if response.status_code != 200:
        logging.error(f"Unable to download {file_name} file.")
    logging.info(f"Successfully downloaded {file_name} file !")
