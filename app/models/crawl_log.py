from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class CrawlLog(Base):
    __tablename__ = 'crawl_logs'

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=True, index=True)
    source_url = Column(String(1024), nullable=False)
    status = Column(String(32), nullable=False)
    message = Column(Text, nullable=True)
    created_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
