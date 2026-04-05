from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.core.database import Base


class UserTopic(Base):
    __tablename__ = 'user_topics'
    __table_args__ = (UniqueConstraint('wx_user_id', 'topic', name='uq_user_topics_user_topic'),)

    id = Column(Integer, primary_key=True, index=True)
    wx_user_id = Column(Integer, ForeignKey('wx_users.id', ondelete='CASCADE'), nullable=False)
    topic = Column(String(64), nullable=False)
