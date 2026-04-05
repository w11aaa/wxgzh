from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class PushTask(Base):
    __tablename__ = 'push_tasks'

    id = Column(Integer, primary_key=True, index=True)
    wx_openid = Column(String(128), nullable=False, index=True)
    digest_date = Column(String(16), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default='pending')
    retries = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
