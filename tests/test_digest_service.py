import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

from app.core.database import Base, SessionLocal, engine
from app.models.article import Article
from app.models.source import Source
from app.services.digest_service import generate_daily_digest


def test_generate_daily_digest_creates_digest_once():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    source = Source(name='s1', source_type='rss', url='https://example.com/rss', enabled=True)
    db.add(source)
    db.commit()

    db.add(
        Article(
            source_id=source.id,
            title='hello fastapi',
            url='https://example.com/1',
            category='backend',
            summary_short='summary',
        )
    )
    db.commit()

    digest1 = generate_daily_digest(db)
    digest2 = generate_daily_digest(db)

    assert digest1.id == digest2.id
    assert '每日简报' in digest1.title

    db.close()
