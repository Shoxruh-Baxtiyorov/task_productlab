from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError

import loader


class S3Services:
    def __init__(self):
        self.config = {
            "aws_access_key_id": loader.S3_KEY_ID,
            "aws_secret_access_key": loader.S3_SECRET_KEY,
            "endpoint_url": loader.S3_ENDPOINT_URL,
        }
        self.bucket_name = loader.S3_BUCKET_NAME
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        try:
            async with self.session.create_client("s3", **self.config) as client:
                try:
                    await client.head_bucket(Bucket=self.bucket_name)
                except:
                    await client.create_bucket(Bucket=self.bucket_name)
                yield client
        except Exception as e:
            print(f'Create S3 client error: {e}')

    async def upload_file(self, object_name: str, file: any, user_id: int):
        try:
            key = f"users/{user_id}/{object_name}"
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file,
                    ACL='public-read')
                file_url = f"{client.meta.endpoint_url}/{self.bucket_name}/{key}"
            return file_url
        except Exception as e:
            print(f'Upload file error: {e}')

    async def get_file(self, object_name: str) -> str | bytes:
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                async with response['Body'] as stream:
                    data = await stream.read()
                return data
        except ClientError as e:
            print(f'Get file error: {e}')

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            print(f'Delete file error: {e}')
