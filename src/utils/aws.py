import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()

def upload_blob(bucket_name, source, destination_blob_name):
    """Uploads a file to the bucket."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        if isinstance(source, dict):
            s3_client.put_object(Bucket=bucket_name, Key=destination_blob_name, Body=json.dumps(source), ContentType='application/json')
            print(f"Dictionary uploaded to {destination_blob_name}.")
        elif isinstance(source, str):
            s3_client.upload_file(source, bucket_name, destination_blob_name)
            print(f"File {source} uploaded to {destination_blob_name}.")
        else:
            print("Source must be a file path or a dictionary")
    except NoCredentialsError:
        print("Credentials not available")

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=blob_name)
        print(f"Blob {blob_name} deleted.")
    except NoCredentialsError:
        print("Credentials not available")

def list_buckets():
    """Lists all buckets."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        response = s3_client.list_buckets()
        names = [bucket['Name'] for bucket in response['Buckets']]
        return names
    except NoCredentialsError:
        print("Credentials not available")

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        names = [obj['Key'] for obj in response.get('Contents', [])]
        return names
    except NoCredentialsError:
        print("Credentials not available")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        s3_client.download_file(bucket_name, source_blob_name, destination_file_name)
        print(f"Downloaded {source_blob_name} to {destination_file_name}.")
    except NoCredentialsError:
        print("Credentials not available")

def read_jsonl(bucket_name, blob_name):
    """Read a JSONL blob from S3"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=blob_name)
        json_list = [json.loads(line) for line in obj['Body'].read().decode('utf-8').splitlines()]
        return json_list
    except NoCredentialsError:
        print("Credentials not available")

def check_file_exists(bucket_name, blob_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=getenv("AWS_REGION")
    )

    try:
        s3_client.head_object(Bucket=bucket_name, Key=blob_name)
        return True
    except s3_client.exceptions.ClientError:
        return False
