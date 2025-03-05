import boto3
import os
from dotenv import load_dotenv
from uuid import uuid4

# 환경 변수 로드
load_dotenv()

# AWS S3 설정
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def upload_to_s3(file):
    """S3에 파일 업로드 후 URL 반환"""
    file_extension = file.filename.split(".")[-1]  # 확장자 추출
    s3_key = f"diary/{uuid4()}.{file_extension}"  # 고유 파일 이름 생성
    
    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"S3 업로드 실패: {e}")
        return None
