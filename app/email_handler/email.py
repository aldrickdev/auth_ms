# std
# 3p
import boto3

# user
import env_vars


SESClient = boto3.client(
    "sesv2",
    region_name=env_vars.AWS_REGION,
    aws_access_key_id=env_vars.AWS_SEND_EMAIL_ACCESS_KEY,
    aws_secret_access_key=env_vars.AWS_SEND_EMAIL_SECRET_KEY,
)
