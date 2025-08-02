from sqlalchemy import Column, Integer, String, Boolean
from app.database.db import Base

class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    is_attending = Column(Boolean, default=False)
    message = Column(String(500), nullable=True)