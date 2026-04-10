import sys
import os
import uuid
from typing import List, Dict, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Database.database import SessionLocal, engine, Base
from Database.models import UserSession, Message, UserProfile

Base.metadata.create_all(bind=engine)

class ChatMemoryManager:
    def __init__(self):
        pass

    def create_session(self, user_id: str) -> str:
        """Creates a new session for a given user and returns the session_id."""
        db = SessionLocal()
        try:
            session_id = str(uuid.uuid4())
            new_session = UserSession(user_id=user_id, session_id=session_id)
            db.add(new_session)
            db.commit()
            return session_id
        finally:
            db.close()

    def add_message(self, session_id: str, role: str, content: str):
        """Adds a general message to the specified session."""
        db = SessionLocal()
        try:
            message = Message(session_id=session_id, role=role, content=content)
            db.add(message)
            db.commit()
        finally:
            db.close()

    def get_messages(self, session_id: str) -> List[Dict]:
        """Retrieves all messages for a given session."""
        db = SessionLocal()
        try:
            messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
            return [{"role": msg.role, "content": msg.content, "created_at": msg.created_at} for msg in messages]
        finally:
            db.close()

    def register_user(self, user_id: str, name: str, email: str, phone: str):
        """Registers a new user CRM profile or updates an existing one."""
        db = SessionLocal()
        try:
            user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if user:
                user.name = name
                user.email = email
                user.phone = phone
            else:
                user = UserProfile(user_id=user_id, name=name, email=email, phone=phone)
                db.add(user)
            db.commit()
        finally:
            db.close()

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Retrieves user profile details."""
        db = SessionLocal()
        try:
            user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if user:
                return {"user_id": user.user_id, "name": user.name, "email": user.email, "phone": user.phone, "created_at": user.created_at}
            return None
        finally:
            db.close()

    def get_all_users(self) -> List[Dict]:
        """Retrieves all registered leads for marketing monitoring."""
        db = SessionLocal()
        try:
            users = db.query(UserProfile).all()
            return [{"user_id": u.user_id, "name": u.name, "email": u.email, "phone": u.phone, "created_at": u.created_at} for u in users]
        finally:
            db.close()

if __name__ == "__main__":
    manager = ChatMemoryManager()
    
    user_id = "user123"
    session_id = manager.create_session(user_id)
    print(f"Created new session with ID: {session_id} for user: {user_id}")
    
    manager.add_message(session_id, role="user", content="Hello, this is a test message!")
    manager.add_message(session_id, role="assistant", content="Hi there! I have saved your message.")
    
    print("\nRetrieving messages from database:")
    messages = manager.get_messages(session_id)
    for msg in messages:
        print(f"[{msg['created_at']}] {msg['role'].capitalize()}: {msg['content']}")
