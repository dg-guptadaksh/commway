# message_schema.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal
import uuid

# --- Core Enumeration ---
Intent = Literal[
    "ACTION_REQUIRED",
    "FYI_READ_ONLY", 
    "REQUEST_MEETING",
    "FEEDBACK_REQUEST",
    "GENERAL"
]

# --- The Canonical Message Schema (CMS) ---
@dataclass
class CanonicalMessage:
    """The unified data structure for any message sent via the gateway."""
    # Required fields first (no defaults)
    sender_email: str
    recipient_email: str
    intent_tag: str
    subject: str
    body_content: str
    
    # Optional fields with defaults
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    internal_tag: Optional[str] = None
    status: str = "PENDING"

    # Data validation helper
    def validate(self):
        valid_intents = ["ACTION_REQUIRED", "FYI_READ_ONLY", "REQUEST_MEETING", "FEEDBACK_REQUEST", "GENERAL"]
        if self.intent_tag not in valid_intents:
            raise ValueError(f"Invalid intent_tag: {self.intent_tag}")
        if not self.sender_email or not self.recipient_email:
            raise ValueError("Sender and recipient emails are mandatory.")