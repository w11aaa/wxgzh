from datetime import date
import json

from sqlalchemy.orm import Session

from app.models.push_log import PushLog
from app.models.push_task import PushTask
from app.models.wx_user import WxUser
from app.services.wechat_service import send_text_message


MAX_RETRIES = 3


def create_daily_push_tasks(db: Session, digest_date: date, digest_link: str) -> int:
    users = db.query(WxUser).filter(WxUser.subscribed.is_(True)).all()
    count = 0
    for user in users:
        payload = {
            'title': f'每日简报 {digest_date.isoformat()}',
            'link': digest_link,
            'content': f'【每日更新】{digest_date.isoformat()}\n{digest_link}'.strip(),
        }
        task = PushTask(
            wx_openid=user.openid,
            digest_date=digest_date.isoformat(),
            payload=json.dumps(payload, ensure_ascii=False),
        )
        db.add(task)
        count += 1
    db.commit()
    return count


def execute_pending_push_tasks(db: Session) -> int:
    tasks = db.query(PushTask).filter(PushTask.status.in_(['pending', 'retry'])).limit(100).all()
    success = 0

    for task in tasks:
        payload = json.loads(task.payload)
        content = payload.get('content', payload.get('title', '每日更新'))
        try:
            send_text_message(openid=task.wx_openid, content=content)
            task.status = 'success'
            task.last_error = None
            db.add(
                PushLog(
                    wx_openid=task.wx_openid,
                    digest_date=task.digest_date,
                    status='success',
                    message='wechat push success',
                )
            )
            success += 1
        except Exception as exc:
            task.retries += 1
            task.last_error = str(exc)
            task.status = 'retry' if task.retries < MAX_RETRIES else 'failed'
            db.add(
                PushLog(
                    wx_openid=task.wx_openid,
                    digest_date=task.digest_date,
                    status=task.status,
                    message=str(exc),
                )
            )

    db.commit()
    return success
