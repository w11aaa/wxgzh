# 微信公众号领域内容采集与每日推送助手（MVP+）

基于 FastAPI + PostgreSQL + Redis + Celery 的可运行后端实现，当前覆盖：

- 来源管理（CRUD）
- RSS 采集与文章入库
- URL 去重 + 标题 hash + 关键词分类
- 每日日报生成
- 公众号回调验签
- 用户订阅主题管理
- 推送任务生成/执行、失败重试与日志
- 抓取日志查询

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

## 管理接口鉴权

部分写接口需要管理员 API Key，请带请求头：

```text
X-API-Key: <ADMIN_API_KEY>
```

默认值来自 `.env` 的 `ADMIN_API_KEY`。

## 主要接口（前缀 `/api/v1`）

### 公共接口

- `GET /health`
- `GET /sources`
- `GET /articles`
- `GET /digests/latest`
- `GET /crawl-logs`
- `GET /wechat/callback`（签名校验）
- `POST /wechat/callback`
- `POST /wechat/users/{openid}/subscribe`
- `POST /wechat/users/{openid}/topics`

### 管理接口（需要 `X-API-Key`）

- `POST /sources`
- `PATCH /sources/{source_id}`
- `POST /sources/{source_id}/crawl`
- `POST /digests/generate`
- `POST /push/generate`
- `POST /push/execute`
- `GET /push/tasks`
- `GET /push/logs`

## 运行测试

```bash
pytest -q
```

## 说明

- 微信推送已接入真实发送流程（调用微信客服消息接口），需正确配置 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`。
- `push_tasks` 支持失败重试（最多 3 次）并记录 `push_logs`。
- 当前数据库初始化仍使用 `create_all`，下一步建议切到 Alembic 迁移。
