import boto3
from botocore.exceptions import NoCredentialsError
import os
from fastapi import UploadFile
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# S3 클라이언트 설정 
s3_client = boto3.client('s3', 
                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), 
                         region_name=os.getenv('AWS_REGION'))

def upload_to_s3(photo: UploadFile, bucket_name: str, folder_name: str, expiration: int = 3600) -> str:
    try:
        # 파일을 메모리에서 읽어옵니다.
        file_content = photo.file.read()
        
        # S3에 업로드할 때 사용할 파일명 (예시로 folder_name과 original filename을 사용)
        file_name = f"{folder_name}/{photo.filename}"
        
        # S3로 파일 업로드
        s3_client.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
        
        # 업로드된 파일의 URL 생성
        photo_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        
        return photo_url
    except NoCredentialsError:
        raise Exception("자격 증명이 필요합니다.")
    except Exception as e:
        raise Exception(f"파일 업로드 중 오류 발생: {str(e)}")
