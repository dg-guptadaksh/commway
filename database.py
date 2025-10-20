# database.py

from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from message_schema import CanonicalMessage  # Import the core data structure

# 1. Database Configuration (Using SQLite for MVP simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./messages.db"

# 2. Setup SQLAlchemy Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite with FastAPI
)

# 3. Base Class for Declarative Models
Base = declarative_base()

# 4. Define the SQLAlchemy Table Model
class MessageDB(Base):
    __tablename__ = "messages"

    # Map directly from CanonicalMessage fields
    message_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    sender_email = Column(String, index=True)
    recipient_email = Column(String)
    intent_tag = Column(String)
    subject = Column(String)
    body_content = Column(String)
    internal_tag = Column(String, nullable=True)
    status = Column(String, default="PENDING")

# 5. Session Setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Initialization Function
def init_db():
    """Creates the database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

# 7. Helper function to create a new record from the CMS
def create_message(db_session, message: CanonicalMessage):
    """Logs a CanonicalMessage object to the database."""
    db_message = MessageDB(
        message_id=message.message_id,
        timestamp=message.timestamp,
        sender_email=message.sender_email,
        recipient_email=message.recipient_email,
        intent_tag=message.intent_tag,
        subject=message.subject,
        body_content=message.body_content,
        internal_tag=message.internal_tag,
        status=message.status
    )
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)
    return db_message

# 8. Helper function to update the status
def update_message_status(db_session, message_id: str, new_status: str):
    """Updates the status of a message after successful action (e.g., SENT)."""
    db_message = db_session.query(MessageDB).filter(MessageDB.message_id == message_id).first()
    if db_message:
        db_message.status = new_status
        db_session.commit()
        return True
    return False

# Execute initialization
if __name__ == "__main__":
    init_db()
    print("Database 'messages.db' initialized and tables created.")