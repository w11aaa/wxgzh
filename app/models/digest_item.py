from sqlalchemy import Column, ForeignKey, Integer, String

from app.core.database import Base


class DigestItem(Base):
    __tablename__ = 'digest_items'

    id = Column(Integer, primary_key=True, index=True)
    digest_id = Column(Integer, ForeignKey('digests.id', ondelete='CASCADE'), nullable=False)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    rank = Column(Integer, default=0, nullable=False)
    category = Column(String(64), nullable=True)
