from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery('wx_assistant', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    imports=['app.tasks.jobs'],
    beat_schedule={
        'crawl-all-sources-every-30-min': {
            'task': 'tasks.crawl_all_sources',
            'schedule': 1800.0,
        },
        'generate-daily-digest-hourly-check': {
            'task': 'tasks.generate_daily_digest',
            'schedule': 3600.0,
        },
        'execute-push-tasks-every-10-min': {
            'task': 'tasks.execute_push_tasks',
            'schedule': 600.0,
        },
    },
)
