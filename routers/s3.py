from fastapi import FastAPI
import boto3
from botocore.exceptions import NoCredentialsError
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

# S3 클라이언트 설정
s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))

class FolderRequest(BaseModel):
    bucket_name: str
    folder_name: str

@app.post("/create_folder/")
async def create_folder(request: FolderRequest):
    if not request.bucket_name or not request.folder_name:
        return {"error": "버킷 이름과 폴더 이름을 모두 입력해야 합니다."}
    
    try:
        # 폴더처럼 보이게 하려면 빈 객체를 생성합니다.
        s3_client.put_object(Bucket=request.bucket_name, Key=request.folder_name + '/')
        return {"message": f"폴더 '{request.folder_name}'가 버킷 '{request.bucket_name}'에 생성되었습니다."}
    
    except NoCredentialsError:
        return {"error": "자격 증명이 필요합니다."}
    except PermissionError:
        return {"error": "해당 버킷에 대한 권한이 없습니다."}
    except Exception as e:
        return {"error": f"예기치 못한 오류: {str(e)}"}
