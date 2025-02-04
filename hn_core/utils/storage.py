from dotenv import load_dotenv
import json
import os
from typing import List

import boto3
from botocore.client import Config


class R2Storage:
    def __init__(self, token: str = None):
        # Load environment variables from .env file
        load_dotenv()
        
        self.token = token or os.getenv("R2_API_KEY")
        
        # Verify that required environment variables are present
        required_vars = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        try:
            self.client = boto3.client(
                "s3",
                endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
                config=Config(signature_version="s3v4"),
            )
        except Exception as e:
            raise Exception(f"Failed to initialize boto3 client: {str(e)}")

    def _serialize_data(self, data: List):
        if not isinstance(data, List):
            raise TypeError("Data must be a list to serialize to jsonl.")

        # Convert each item in the list to a JSON line
        jsonl_data = "\n".join(json.dumps(item, default=str) for item in data)
        return jsonl_data.encode(), "application/x-ndjson"

    def upload_file(
        self,
        filename: str,
        bucket: str,
        key: str,
    ):
        try:
            self.client.upload_file(
                Filename=filename,
                Bucket=bucket,
                Key=key,
            )
        except Exception as e:
            raise Exception(f"Failed to upload file to R2: {str(e)}")

    def put_object(
        self,
        data,
        bucket: str,
        key: str,
    ):
        serialized_data, content_type = self._serialize_data(data)
        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=serialized_data,
            ContentType=content_type,
        )

    def get_object(
        self,
        bucket: str,
        key: str,
        filename: str = None,
    ):
        try:
            response = self.client.get_object(
                Bucket=bucket,
                Key=key,
            )
            stream = response["Body"]
            
            # If filename is provided, save to file
            if filename:
                if not filename.endswith(".jsonl"):
                    filename += ".jsonl"
                with open(filename, "wb") as f:
                    for chunk in stream.iter_chunks():
                        f.write(chunk)
            
            # Read and parse the data
            data = stream.read().decode('utf-8')
            if key.endswith('.json'):
                return json.loads(data)
            elif key.endswith('.jsonl'):
                return [json.loads(line) for line in data.splitlines() if line.strip()]
            else:
                return data
            
        except Exception as e:
            raise Exception(f"Failed to get object from R2: {str(e)}")

    def download_file(
        self,
        bucket: str,
        key: str,
        filename: str,
    ):
        try:
            self.client.download_file(
                Bucket=bucket,
                Key=key,
                Filename=filename,
            )
        except Exception as e:
            raise Exception(f"Failed to download file from R2: {str(e)}")
