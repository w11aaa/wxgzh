from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func

from app.core.database import Base


class Article(Base):
    __tablename__ = 'articles'
    __table_args__ = (UniqueConstraint('url', name='uq_articles_url'),)

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='SET NULL'), nullable=True)
    title = Column(String(512), nullable=False)
    author = Column(String(128), nullable=True)
    url = Column(String(1024), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    content = Column(Text, nullable=True)
    summary_short = Column(String(500), nullable=True)
    summary_long = Column(Text, nullable=True)
    category = Column(String(64), nullable=True)
    title_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
