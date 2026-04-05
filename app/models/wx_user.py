from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.core.database import Base


class WxUser(Base):
    __tablename__ = 'wx_users'

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(128), nullable=False, unique=True, index=True)
    nickname = Column(String(128), nullable=True)
    subscribed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
