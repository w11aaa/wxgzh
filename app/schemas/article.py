from datetime import datetime

from pydantic import BaseModel


class ArticleOut(BaseModel):
    id: int
    source_id: int | None
    title: str
    url: str
    author: str | None
    category: str | None
    summary_short: str | None
    created_at: datetime

    class Config:
        from_attributes = True
