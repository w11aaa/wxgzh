from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SourceBase(BaseModel):
    name: str
    source_type: str = 'rss'
    url: HttpUrl
    parser_rule: str | None = None
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: str | None = None
    parser_rule: str | None = None
    enabled: bool | None = None


class SourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    url: str
    parser_rule: str | None
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True
