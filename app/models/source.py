from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    source_type = Column(String(32), nullable=False, default='rss')
    url = Column(String(512), nullable=False, unique=True)
    parser_rule = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
