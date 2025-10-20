# api.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Literal

from database import init_db, SessionLocal, create_message, update_message_status
from mail_generator import send_structured_email
from message_schema import CanonicalMessage

Intent = Literal["ACTION_REQUIRED", "FYI_READ_ONLY", "REQUEST_MEETING", "FEEDBACK_REQUEST", "GENERAL"]

# Initialize the database on startup
init_db()

app = FastAPI(title="CommWay Gateway API", version="0.1.0")

# --- Pydantic Request Schema (Defines the expected API input) ---
class MessageRequest(BaseModel):
    """The data structure expected from the web form submission."""
    sender_email: str
    recipient_email: str

    # Use a literal union for validation on intent_tag
    intent_tag: Intent = Field(
        description="The purpose of the message, must be one of the defined Intents."
    )

    subject: str
    body_content: str
    internal_tag: Optional[str] = None

    # Add a configuration for the schema example
    class Config:
        json_schema_extra = {
            "example": {
                "sender_email": "alice@sender.com",
                "recipient_email": "bob@recipient.com",
                "intent_tag": "ACTION_REQUIRED",  # Changed from Intent.ACTION_REQUIRED
                "subject": "Final review of Q3 numbers",
                "body_content": "Please check the attached report and confirm the totals are correct before sending to the CEO.",
                "internal_tag": "Finance_Q3"
            }
        }

# --- Dependency for Database Session ---
def get_db():
    """FastAPI Dependency to handle DB session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Main Send Message Endpoint ---
@app.post("/send-message/")
def send_message(message_data: MessageRequest, db: Session = Depends(get_db)):
    """
    Receives structured message data, logs it, and sends the corresponding email.
    """

    # 1. Input Validation (Pydantic handles basic validation, but we check business logic)
    valid_intents = ["ACTION_REQUIRED", "FYI_READ_ONLY", "REQUEST_MEETING", "FEEDBACK_REQUEST", "GENERAL"]
    if message_data.intent_tag not in valid_intents:
        raise HTTPException(status_code=400, detail=f"Invalid intent tag provided: {message_data.intent_tag}")

    # 2. Create the Canonical Message object
    canonical_msg = CanonicalMessage(**message_data.model_dump(), status="PENDING")

    # 3. Log the message to the database
    try:
        create_message(db, canonical_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database logging failed: {e}")

    # 4. Attempt to send the email
    sent_success = send_structured_email(canonical_msg)

    # 5. Update database status based on send result
    new_status = "SENT" if sent_success else "FAILED"
    update_message_status(db, canonical_msg.message_id, new_status)

    if not sent_success:
        # Although logged, the message failed to leave the system
        raise HTTPException(status_code=500, detail="Email failed to send. Status logged as FAILED.")

    return {
        "status": "success",
        "message_id": canonical_msg.message_id,
        "external_status": "Email sent successfully, status logged as SENT."
    }

# --- Simple Health Check Endpoint ---
@app.get("/health/")
def health_check():
    """Verifies the API is running."""
    return {"status": "ok", "service": "CommWay Gateway"}