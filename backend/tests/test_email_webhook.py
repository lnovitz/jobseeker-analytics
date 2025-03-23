from datetime import datetime
import json
import base64
from db.utils import user_email_utils

# Sample SNS subscription confirmation message
sns_subscription_message = {
    "Type": "SubscriptionConfirmation",
    "MessageId": "test-message-id",
    "Token": "test-token",
    "TopicArn": "123",
    "Message": "You have chosen to subscribe to the topic...",
    "SubscribeURL": "https://example.com/confirm",  # This will be mocked
    "Timestamp": datetime.utcnow().isoformat(),
    "SignatureVersion": "1",
    "Signature": "test-signature",
    "SigningCertURL": "https://example.com/cert"
}

# Sample SES email notification via SNS
sample_email = """From: sender@example.com
To: test@test.jobba.help
Subject: Software Engineer Position
Date: Thu, 21 Mar 2024 12:00:00 -0700

Thank you for applying to the Software Engineer position at Example Corp.
We have received your application and will review it shortly.

Best regards,
HR Team"""

sns_email_notification = {
    "Type": "Notification",
    "MessageId": "test-message-id",
    "TopicArn": "123",
    "Message": json.dumps({
        "mail": {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "sender@example.com",
            "destination": ["test@test.jobba.help"],
            "messageId": "test-email-id",
            "commonHeaders": {
                "from": ["sender@example.com"],
                "to": ["test@test.jobba.help"],
                "subject": "Software Engineer Position",
            }
        },
        "content": base64.b64encode(sample_email.encode()).decode()
    }),
    "Timestamp": datetime.utcnow().isoformat(),
    "SignatureVersion": "1",
    "Signature": "test-signature",
    "SigningCertURL": "https://example.com/cert"
}

def test_subscription_confirmation(test_client, mocker):
    """Test handling of SNS subscription confirmation."""
    # Mock the requests.get call to return success
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200))
    
    response = test_client.post(
        "api/v1/webhook/email",
        json=sns_subscription_message
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "SNS subscription confirmed"

def test_email_notification(test_client, mocker):
    """Test handling of email notification via SNS."""
    # Mock user email creation
    mock_user_email = mocker.Mock()
    mock_user_email.id = "mock-id"
    mock_user_email.user_id = "mock-user-id"
    mocker.patch('db.utils.user_email_utils.create_user_email', return_value=mock_user_email)

    response = test_client.post(
        "api/v1/webhook/email",
        json=sns_email_notification
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Email processed successfully"

