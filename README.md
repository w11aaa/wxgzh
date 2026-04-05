# 微信公众号领域内容采集与每日推送助手（MVP）

基于 FastAPI + PostgreSQL + Redis + Celery 的最小可运行实现，覆盖：

- 来源管理（CRUD）
- RSS 采集与文章入库
- 简单去重（URL）与关键词分类
- 每日日报生成
- 公众号回调验签（基础）
- 用户订阅主题管理（基础）
- 推送任务生成与执行日志（stub）

## 快速启动

1. 复制环境变量：

```bash
cp .env.example .env
```

2. 启动服务：

```bash
docker compose up --build
```

3. 打开 API 文档：

- http://localhost:8000/docs

## 主要接口（前缀 `/api/v1`）

- `GET /health`
- `POST /sources`
- `GET /sources`
- `PATCH /sources/{source_id}`
- `POST /sources/{source_id}/crawl`
- `GET /articles`
- `POST /digests/generate`
- `GET /digests/latest`
- `GET /wechat/callback`（签名校验）
- `POST /wechat/users/{openid}/subscribe`
- `POST /wechat/users/{openid}/topics`
- `POST /push/generate`
- `POST /push/execute`

## 说明

- 当前微信推送执行为 stub（记录成功日志），后续可替换为真实 API 调用。
- 数据库初始化采用应用启动时 `create_all`，后续建议切换至 Alembic 迁移。
