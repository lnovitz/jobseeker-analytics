import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import base64

# Sample SNS subscription confirmation message
sns_subscription_message = {
    "Type": "SubscriptionConfirmation",
    "MessageId": "test-message-id",
    "Token": "test-token",
    "TopicArn": "arn:aws:sns:us-east-1:615299727956:jobba-help-email-notifications",
    "Message": "You have chosen to subscribe to the topic...",
    "SubscribeURL": "https://example.com/confirm",  # This will be mocked
    "Timestamp": datetime.utcnow().isoformat(),
    "SignatureVersion": "1",
    "Signature": "test-signature",
    "SigningCertURL": "https://example.com/cert"
}

# Sample SES email notification via SNS
sample_email = """From: sender@example.com
To: track@jobba.help
Subject: Software Engineer Position
Date: Thu, 21 Mar 2024 12:00:00 -0700

Thank you for applying to the Software Engineer position at Example Corp.
We have received your application and will review it shortly.

Best regards,
HR Team"""

sns_email_notification = {
    "Type": "Notification",
    "MessageId": "test-message-id",
    "TopicArn": "arn:aws:sns:us-east-1:615299727956:jobba-help-email-notifications",
    "Message": json.dumps({
        "mail": {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "sender@example.com",
            "destination": ["track@jobba.help"],
            "messageId": "test-email-id",
            "commonHeaders": {
                "from": ["sender@example.com"],
                "to": ["track@jobba.help"],
                "subject": "Software Engineer Position"
            }
        },
        "content": base64.b64encode(sample_email.encode()).decode()
    }),
    "Timestamp": datetime.utcnow().isoformat(),
    "SignatureVersion": "1",
    "Signature": "test-signature",
    "SigningCertURL": "https://example.com/cert"
}

def test_subscription_confirmation(test_client: TestClient, mocker):
    """Test handling of SNS subscription confirmation."""
    # Mock the requests.get call to return success
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200))
    
    response = test_client.post(
        "/webhook/email",
        json=sns_subscription_message
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "SNS subscription confirmed"

def test_email_notification(test_client: TestClient, mocker):
    """Test handling of email notification via SNS."""
    response = test_client.post(
        "/webhook/email",
        json=sns_email_notification
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Email processed successfully"

# Helper function to run webhook locally for manual testing
def run_local_tests():
    """
    Helper function to manually test the webhook locally.
    Usage:
    1. Start your FastAPI server
    2. Run this script
    3. It will send test messages to your local endpoint
    """
    import requests
    import time
    
    BASE_URL = "http://localhost:8000"
    
    print("Testing subscription confirmation...")
    response = requests.post(
        f"{BASE_URL}/webhook/email",
        json=sns_subscription_message
    )
    print(f"Response: {response.status_code}")
    print(response.json())
    
    time.sleep(1)  # Wait a bit between requests
    
    print("\nTesting email notification...")
    response = requests.post(
        f"{BASE_URL}/webhook/email",
        json=sns_email_notification
    )
    print(f"Response: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    run_local_tests() 