from datetime import date
import json

from sqlalchemy.orm import Session

from app.models.push_log import PushLog
from app.models.push_task import PushTask
from app.models.wx_user import WxUser


def create_daily_push_tasks(db: Session, digest_date: date, digest_link: str) -> int:
    users = db.query(WxUser).filter(WxUser.subscribed.is_(True)).all()
    count = 0
    for user in users:
        payload = {'title': f'每日简报 {digest_date.isoformat()}', 'link': digest_link}
        task = PushTask(wx_openid=user.openid, digest_date=digest_date.isoformat(), payload=json.dumps(payload, ensure_ascii=False))
        db.add(task)
        count += 1
    db.commit()
    return count


def execute_pending_push_tasks(db: Session) -> int:
    tasks = db.query(PushTask).filter(PushTask.status == 'pending').limit(100).all()
    success = 0
    for task in tasks:
        task.status = 'success'
        log = PushLog(wx_openid=task.wx_openid, digest_date=task.digest_date, status='success', message='stub push success')
        db.add(log)
        success += 1
    db.commit()
    return success
