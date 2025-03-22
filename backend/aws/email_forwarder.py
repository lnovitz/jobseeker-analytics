import json
import boto3
import requests
import base64
from datetime import datetime
import os

def lambda_handler(event, context):
    """AWS Lambda function to forward emails from SES to webhook endpoint."""
    
    # Extract email data from SES event
    ses_notification = event['Records'][0]['ses']
    message_id = ses_notification['mail']['messageId']
    
    # Get the email content from S3 (SES stores it there)
    s3 = boto3.client('s3')
    bucket_name = os.environ['S3_BUCKET_NAME']
    
    try:
        # Get email content from S3
        response = s3.get_object(Bucket=bucket_name, Key=message_id)
        email_content = response['Body'].read()
        
        # Prepare payload for webhook
        payload = {
            'sender': ses_notification['mail']['source'],
            'recipient': ses_notification['mail']['destination'][0],
            'subject': ses_notification['mail']['commonHeaders']['subject'],
            'raw_email': base64.b64encode(email_content).decode('utf-8'),
            'timestamp': ses_notification['mail']['timestamp']
        }
        
        # Send to webhook
        webhook_url = os.environ['WEBHOOK_URL']
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Webhook returned status code {response.status_code}")
            
        return {
            'statusCode': 200,
            'body': json.dumps('Email forwarded successfully')
        }
        
    except Exception as e:
        print(f"Error processing email: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        } 