from app.core.database import SessionLocal
from app.models.source import Source
from app.services.crawler import crawl_rss_source
from app.services.digest_service import generate_daily_digest
from app.services.push_service import execute_pending_push_tasks
from app.tasks.celery_app import celery_app


@celery_app.task(name='tasks.crawl_all_sources')
def crawl_all_sources() -> int:
    db = SessionLocal()
    try:
        count = 0
        sources = db.query(Source).filter(Source.enabled.is_(True), Source.source_type == 'rss').all()
        for source in sources:
            count += crawl_rss_source(db, source)
        return count
    finally:
        db.close()


@celery_app.task(name='tasks.generate_daily_digest')
def scheduled_generate_daily_digest() -> int:
    db = SessionLocal()
    try:
        digest = generate_daily_digest(db)
        return digest.id
    finally:
        db.close()


@celery_app.task(name='tasks.execute_push_tasks')
def execute_push_tasks() -> int:
    db = SessionLocal()
    try:
        return execute_pending_push_tasks(db)
    finally:
        db.close()
