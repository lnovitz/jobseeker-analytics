from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import requests

from sqlmodel import Session
from database import get_session
from db.utils.user_email_utils import create_user_email
from db.users import Users
from utils.email_utils import get_email
from utils.llm_utils import process_email

router = APIRouter()

class EmailPayload(BaseModel):
    sender: str
    recipient: str
    subject: str
    raw_email: str
    timestamp: Optional[datetime]

@router.post("/webhook/email")
async def receive_email(
    request: Request,
    db: Session = Depends(get_session)
):
    """Process incoming SNS messages, including subscription confirmation and email notifications.
    
    Args:
        request (Request): The raw request to handle SNS messages
        db (Session): Database session
        
    Returns:
        dict: Status of the message processing
    """
    try:
        # Get the raw body as text
        body = await request.body()
        
        # Parse the SNS message
        sns_message = json.loads(body)
        
        # Handle SNS subscription confirmation
        if sns_message.get('Type') == 'SubscriptionConfirmation':
            # Get the subscription confirmation URL
            subscribe_url = sns_message.get('SubscribeURL')
            if subscribe_url:
                # Make a GET request to confirm the subscription
                response = requests.get(subscribe_url)
                if response.status_code == 200:
                    return {"status": "success", "message": "SNS subscription confirmed"}
                else:
                    raise HTTPException(status_code=400, detail="Failed to confirm SNS subscription")
        
        # Handle email notification
        elif sns_message.get('Type') == 'Notification':
            # Parse the message from SNS
            message = json.loads(sns_message.get('Message', '{}'))
            
            # Extract email content from the SES message
            ses_mail = message.get('mail', {})
            ses_content = message.get('content', '')
            
            # Create payload for processing
            payload = EmailPayload(
                sender=ses_mail.get('source', ''),
                recipient=ses_mail.get('destination', [''])[0],
                subject=ses_mail.get('commonHeaders', {}).get('subject', ''),
                raw_email=ses_content,
                timestamp=datetime.fromisoformat(ses_mail.get('timestamp', '')) if ses_mail.get('timestamp') else None
            )
            
            # Use refactored get_email function to parse the email
            email_data = get_email(raw_message={
                "raw": payload.raw_email,
                "message_id": ses_mail.get('messageId', f"FWD-{datetime.utcnow().timestamp()}")
            })
            
            if not email_data:
                raise HTTPException(status_code=400, detail="Could not parse email")
            
            # Process email using existing LLM utility
            result = process_email(email_data["text_content"])
            if not isinstance(result, str) and result:
                # Set default values for empty fields
                for key in result.keys():
                    if not result[key]:
                        result[key] = "unknown"
            else:
                result = {
                    "company_name": "unknown",
                    "application_status": "unknown",
                    "job_title": "unknown"
                }
            
            # Prepare message data for UserEmails creation
            message_data = {
                "id": email_data["id"],
                "company_name": result["company_name"],
                "application_status": result["application_status"],
                "received_at": email_data["date"],
                "subject": email_data["subject"],
                "job_title": result["job_title"],
                "from": email_data["from"]
            }
            
            # Create UserEmails record using existing utility
            tracked_user = Users(user_id=payload.recipient, user_email=payload.recipient, start_date=datetime.now())
            # TODO: fix this user object to extract id and check if user exists and matches against stored token
            email_record = create_user_email(tracked_user, message_data)
            
            if email_record:
                db.add(email_record)
                db.commit()
                return {"status": "success", "message": "Email processed successfully"}
            else:
                return {"status": "skipped", "message": "Email already exists or could not be processed"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported SNS message type: {sns_message.get('Type')}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))