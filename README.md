# 微信公众号领域内容采集与每日推送助手（使用说明书）

> 版本：MVP 迭代版（更新于 2026-04-06）

本项目是一个基于 **FastAPI + PostgreSQL + Redis + Celery** 的内容采集与日报推送后端，目标是完成：

1. 内容源管理
2. RSS 抓取与文章入库
3. 分类与摘要（基础规则）
4. 每日日报生成
5. 微信公众号回调与推送任务执行

---

## 一、技术栈

- API：FastAPI
- 数据库：PostgreSQL（开发可用 SQLite 冒烟）
- 缓存/队列：Redis
- 调度与异步任务：Celery Worker + Celery Beat
- 容器化：Docker + Docker Compose

---

## 二、目录结构

```text
app/
  api/            # HTTP 路由
  core/           # 配置、数据库、Redis、安全
  models/         # SQLAlchemy 模型
  schemas/        # Pydantic 请求/响应模型
  services/       # 业务服务（crawl/digest/push/wechat）
  tasks/          # Celery 任务和调度
tests/            # pytest 测试
README.md         # 使用说明书
TEST_REPORT.md    # 当前进度与测试报告
```

---

## 三、快速启动

### 1) 环境准备

- Docker & Docker Compose（推荐）
- 或 Python 3.10+ 本地运行

### 2) 配置环境变量

```bash
cp .env.example .env
```

关键配置项：

- `DATABASE_URL`
- `REDIS_URL`
- `ADMIN_API_KEY`
- `WECHAT_TOKEN`
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`

### 3) Docker 启动

```bash
docker compose up --build
```

服务说明：

- `api`：FastAPI 服务（默认 `:8000`）
- `worker`：Celery Worker
- `beat`：Celery Beat 调度器
- `postgres`：数据库
- `redis`：缓存/消息中间件

### 4) 打开接口文档

- Swagger UI: http://localhost:8000/docs

---

## 四、运行测试

```bash
pytest -q
```

已包含的自动化测试：

- `tests/test_digest_service.py`：日报生成幂等性
- `tests/test_wechat_signature.py`：微信签名校验成功/失败路径

---

## 五、鉴权说明

系统将高风险写操作设为管理接口，必须携带请求头：

```text
X-API-Key: <ADMIN_API_KEY>
```

未携带或错误时返回 `401`。

---

## 六、接口使用说明（`/api/v1`）

## 1. 公共接口

- `GET /health`：健康检查
- `GET /sources`：来源列表
- `GET /articles`：文章列表（支持 `category` 过滤）
- `GET /digests/latest`：最新日报
- `GET /crawl-logs`：抓取日志
- `GET /wechat/callback`：微信验签
- `POST /wechat/callback`：微信事件回调入口
- `POST /wechat/users/{openid}/subscribe`：用户订阅建档
- `POST /wechat/users/{openid}/topics`：设置订阅主题

### 2. 管理接口（需 `X-API-Key`）

- `POST /sources`：新增来源
- `PATCH /sources/{source_id}`：更新来源
- `POST /sources/{source_id}/crawl`：手动触发抓取
- `POST /digests/generate`：生成日报
- `POST /push/generate`：生成推送任务
- `POST /push/execute`：执行推送任务
- `GET /push/tasks`：推送任务列表
- `GET /push/logs`：推送日志列表

---

## 七、典型流程（建议）

1. 添加来源 `POST /sources`
2. 手动抓取 `POST /sources/{id}/crawl`
3. 查看文章 `GET /articles`
4. 生成日报 `POST /digests/generate`
5. 用户关注并设置主题
6. 生成推送任务 `POST /push/generate`
7. 执行推送 `POST /push/execute`

---

## 八、当前已实现能力与限制

### 已实现

- RSS 抓取 + URL 去重
- 关键词分类与摘要字段
- 抓取日志记录
- 推送重试（最多 3 次）
- 微信 access_token 缓存（Redis）

### 当前限制

- 数据库迁移仍是 `create_all`（未切 Alembic 流程）
- 微信真实环境联调依赖公众号资质与密钥
- 鉴权为静态 API Key（未上 RBAC/JWT）
- 监控告警尚未接入

---

## 九、常见问题

### 1) 401 invalid api key

请确认请求头中包含：`X-API-Key`，且与 `.env` 中 `ADMIN_API_KEY` 一致。

### 2) 推送失败

检查：

- `WECHAT_APP_ID` / `WECHAT_APP_SECRET` 是否正确
- Redis 是否可用（token 缓存）
- `GET /push/logs` 中错误信息

### 3) 为什么抓取没有新增文章？

常见原因：

- 来源 RSS 无更新
- 文章 URL 已存在（去重跳过）
- 来源不可访问（查看 `GET /crawl-logs`）

---

## 十、下一步迭代建议

1. 接入 Alembic 迁移
2. 完善 API 集成测试
3. 增加微信菜单与事件细化处理
4. 增加监控告警
5. 增加后台权限体系（JWT/RBAC）
