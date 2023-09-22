from google.cloud import storage
from dotenv import load_dotenv
from os import getenv

import json

load_dotenv()

def upload_blob(bucket_name, source, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"
    storage_client = storage.Client.from_service_account_json(getenv("GOOGLE_APPLICATION_CREDENTIALS"))   

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if isinstance(source, dict):
        blob.upload_from_string(data=json.dumps(source),content_type='application/json') 
        print(
            f"Dictionary uploaded to {destination_blob_name}."
        )
    elif isinstance(source, str):
        blob.upload_from_filename(source)
        print(
            f"File {source} uploaded to {destination_blob_name}."
        )
    else:
        print(
            "Please source must be a file path or a dictionary"
        )

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client.from_service_account_json(getenv("GOOGLE_APPLICATION_CREDENTIALS")) 

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f"Blob {blob_name} deleted.")

def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client.from_service_account_json(getenv("GOOGLE_APPLICATION_CREDENTIALS")) 
    buckets = storage_client.list_buckets()

    names = []
    for bucket in buckets:
        # printæ(bucket.name)
        names.append(bucket.name)
    
    return names

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client.from_service_account_json(getenv("GOOGLE_APPLICATION_CREDENTIALS")) 

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    names = []
    for blob in blobs:
        # print(blob.name)
        names.append(blob.name)
    return names

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

def read_jsonl(bucket_name, blob_name):
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client(getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html
    # with blob.open("w") as f:
    #     f.write("Hello world")
    with blob.open('r') as json_file:
        json_list = list(json_file)
    json_list = [json.loads(x) for x in json_list]
    return json_list

def check_file_exists(bucket_name, blob_name):
    # Initialize a storage client
    storage_client = storage.Client(getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(blob_name)

    # Check if the file exists
    return blob.exists()

