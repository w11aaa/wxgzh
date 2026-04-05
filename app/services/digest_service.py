from datetime import date

from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.digest import Digest
from app.models.digest_item import DigestItem


def generate_daily_digest(db: Session, target_date: date | None = None) -> Digest:
    target_date = target_date or date.today()

    existing = db.query(Digest).filter(Digest.digest_date == target_date).first()
    if existing:
        return existing

    articles = (
        db.query(Article)
        .filter(Article.category.isnot(None))
        .order_by(Article.created_at.desc())
        .limit(50)
        .all()
    )

    lines = [f'# 每日简报 {target_date.isoformat()}', '']
    for idx, article in enumerate(articles, start=1):
        lines.append(f"{idx}. [{article.title}]({article.url}) - {article.summary_short or ''}")

    digest = Digest(
        digest_date=target_date,
        title=f'每日简报-{target_date.isoformat()}',
        content_markdown='\n'.join(lines),
        content_html=None,
    )
    db.add(digest)
    db.flush()

    for idx, article in enumerate(articles, start=1):
        item = DigestItem(digest_id=digest.id, article_id=article.id, rank=idx, category=article.category)
        db.add(item)

    db.commit()
    db.refresh(digest)
    return digest
