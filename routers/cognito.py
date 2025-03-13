import boto3
import os
from dotenv import load_dotenv

load_dotenv()

cognito_client = boto3.client('cognito-idp',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

def verify_cognito_token(token):
    try:
        response = cognito_client.get_user(
            AccessToken=token
        )
        return {
            "sub": next(attr['Value'] for attr in response['UserAttributes'] if attr['Name'] == 'sub'),
            "username": response['Username']
        }
    except Exception as e:
        return None 