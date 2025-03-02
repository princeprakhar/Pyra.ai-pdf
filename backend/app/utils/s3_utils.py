import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException, status
import os

s3_client = boto3.client('s3')

async def upload_to_s3(contents,username, filename, content_type):
    try:
        s3_key = f"uploads/{username}/{filename}"
        s3_client.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=s3_key,
            Body=contents,
            ContentType=content_type
        )
        return s3_key
    except NoCredentialsError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3 credentials not available")
