from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class PushLog(Base):
    __tablename__ = 'push_logs'

    id = Column(Integer, primary_key=True, index=True)
    wx_openid = Column(String(128), nullable=False, index=True)
    digest_date = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
