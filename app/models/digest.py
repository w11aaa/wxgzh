from sqlalchemy import Column, Date, DateTime, Integer, String, Text, UniqueConstraint, func

from app.core.database import Base


class Digest(Base):
    __tablename__ = 'digests'
    __table_args__ = (UniqueConstraint('digest_date', name='uq_digests_date'),)

    id = Column(Integer, primary_key=True, index=True)
    digest_date = Column(Date, nullable=False)
    title = Column(String(255), nullable=False)
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    public_link = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
