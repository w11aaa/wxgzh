from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import Base, engine, get_db
from app.models import Article, Digest, Source, UserTopic, WxUser
from app.schemas.article import ArticleOut
from app.schemas.source import SourceCreate, SourceOut, SourceUpdate
from app.services.crawler import crawl_rss_source
from app.services.digest_service import generate_daily_digest
from app.services.push_service import create_daily_push_tasks, execute_pending_push_tasks
from app.services.wechat_service import verify_signature

router = APIRouter()


@router.on_event('startup')
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@router.post('/sources', response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    exists = db.query(Source).filter(Source.url == str(payload.url)).first()
    if exists:
        raise HTTPException(status_code=409, detail='source exists')
    source = Source(
        name=payload.name,
        source_type=payload.source_type,
        url=str(payload.url),
        parser_rule=payload.parser_rule,
        enabled=payload.enabled,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get('/sources', response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.id.desc()).all()


@router.patch('/sources/{source_id}', response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail='source not found')

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


@router.post('/sources/{source_id}/crawl')
def crawl_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id, Source.enabled.is_(True)).first()
    if not source:
        raise HTTPException(status_code=404, detail='enabled source not found')

    if source.source_type != 'rss':
        raise HTTPException(status_code=400, detail='only rss source is supported now')

    count = crawl_rss_source(db, source)
    return {'created_articles': count}


@router.get('/articles', response_model=list[ArticleOut])
def list_articles(category: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Article)
    if category:
        query = query.filter(Article.category == category)
    return query.order_by(Article.id.desc()).limit(100).all()


@router.post('/digests/generate')
def generate_digest(db: Session = Depends(get_db)):
    digest = generate_daily_digest(db)
    return {'digest_id': digest.id, 'digest_date': digest.digest_date.isoformat()}


@router.get('/digests/latest')
def latest_digest(db: Session = Depends(get_db)):
    digest = db.query(Digest).order_by(Digest.digest_date.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail='digest not found')
    return {
        'id': digest.id,
        'date': digest.digest_date.isoformat(),
        'title': digest.title,
        'content_markdown': digest.content_markdown,
    }


@router.get('/wechat/callback')
def wechat_verify(signature: str, timestamp: str, nonce: str, echostr: str):
    if verify_signature(signature=signature, timestamp=timestamp, nonce=nonce):
        return echostr
    raise HTTPException(status_code=403, detail='invalid signature')


@router.post('/wechat/callback')
async def wechat_event(_: Request):
    return {'message': 'event received'}


@router.post('/wechat/users/{openid}/subscribe')
def subscribe_user(openid: str, db: Session = Depends(get_db)):
    user = db.query(WxUser).filter(WxUser.openid == openid).first()
    if not user:
        user = WxUser(openid=openid, subscribed=True)
        db.add(user)
    else:
        user.subscribed = True
    db.commit()
    return {'openid': openid, 'subscribed': True}


@router.post('/wechat/users/{openid}/topics')
def set_topics(openid: str, topics: list[str], db: Session = Depends(get_db)):
    user = db.query(WxUser).filter(WxUser.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')

    db.query(UserTopic).filter(UserTopic.wx_user_id == user.id).delete()
    for topic in topics:
        db.add(UserTopic(wx_user_id=user.id, topic=topic))
    db.commit()
    return {'openid': openid, 'topics': topics}


@router.post('/push/generate')
def generate_push_tasks(db: Session = Depends(get_db)):
    digest = db.query(Digest).order_by(Digest.digest_date.desc()).first()
    if not digest:
        raise HTTPException(status_code=404, detail='digest not found')
    count = create_daily_push_tasks(db, date.fromisoformat(digest.digest_date.isoformat()), digest.public_link or '')
    return {'created_tasks': count}


@router.post('/push/execute')
def execute_push_tasks(db: Session = Depends(get_db)):
    count = execute_pending_push_tasks(db)
    return {'success_tasks': count}
