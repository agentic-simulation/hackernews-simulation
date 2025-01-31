import json
import os
from typing import List

import boto3
from botocore.client import Config


class R2Storage:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("R2_API_KEY")
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
        filename: str,
    ):
        try:
            response = self.client.get_object(
                Bucket=bucket,
                Key=key,
            )
            stream = response["Body"]
            if not filename.endswith(".jsonl"):
                filename += ".jsonl"

            # Write stream to JSONL file
            with open(filename, "wb") as f:
                for chunk in stream.iter_chunks():
                    f.write(chunk)
        except Exception as e:
            raise Exception(f"Failed to get object from R2: {str(e)}")
