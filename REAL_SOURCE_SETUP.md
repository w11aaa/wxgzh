# 真实公众号信息采集配置指南（合规版）

> 更新时间：2026-04-06

你现在这个系统已经能跑通抓取链路，但要“采集到真实公众号信息”，建议先按 **合规 + 稳定来源** 路线配置，避免直接做高风险爬虫。

---

## 1. 先明确：当前系统最稳定的是 RSS 来源

目前代码里 `source_type` 只支持 `rss`（`/sources/{id}/crawl` 也会检查）。

所以要拿到真实内容，第一步是把公众号相关内容转换为可稳定订阅的 RSS 源，或者使用本身提供 RSS 的媒体源。

---

## 2. 必备环境配置

在 `.env` 中确认以下配置：

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/wxgzh
REDIS_URL=redis://redis:6379/0
ADMIN_API_KEY=你的管理密钥

WECHAT_TOKEN=你的公众号开发者Token
WECHAT_APP_ID=你的公众号AppID
WECHAT_APP_SECRET=你的公众号AppSecret
```

> 说明：
> - `WECHAT_*` 主要用于“推送与回调”。
> - “内容采集”是否成功，关键还是你配置的 source URL 是否真实可访问。

---

## 3. 添加真实可用来源（推荐顺序）

## 方案A（推荐）：行业站点/媒体官方 RSS

优点：稳定、低风险、维护成本低。

1. 收集你目标领域的官方 RSS 地址。
2. 用管理接口写入：

```bash
curl -X POST 'http://localhost:8000/api/v1/sources' \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: 你的ADMIN_API_KEY' \
  -d '{
    "name": "示例科技RSS",
    "source_type": "rss",
    "url": "https://example.com/rss.xml",
    "enabled": true
  }'
```

3. 手动触发抓取：

```bash
curl -X POST 'http://localhost:8000/api/v1/sources/1/crawl' \
  -H 'X-API-Key: 你的ADMIN_API_KEY'
```

4. 检查结果：

- `GET /api/v1/articles`
- `GET /api/v1/crawl-logs`

---

## 方案B：公众号内容的“RSS化中间层”

如果你要覆盖公众号内容，可通过合法可用的 RSS 聚合方式（例如你自建/维护的中间层）统一产出 RSS，再接入本系统。

建议原则：

1. 只接入公开可访问且允许引用的内容。
2. 仅保存摘要与原文链接，避免整文搬运。
3. 为每个来源保留 `name/url` 和失败日志。

---

## 4. 公众号能力配置（用于推送，不是采集）

在微信公众平台完成：

1. 开启开发者模式
2. 配置服务器地址（你的回调地址）
3. Token 与 `.env` 的 `WECHAT_TOKEN` 保持一致
4. 验证回调：
   - `GET /api/v1/wechat/callback`

推送链路检查：

1. `POST /api/v1/push/generate`
2. `POST /api/v1/push/execute`
3. 查看 `GET /api/v1/push/logs`

---

## 5. 如何判断“已经在采真实数据”

满足以下 4 条即可：

1. `crawl_logs` 中状态持续出现 `success`
2. `articles` 每天有新增记录
3. `digests` 可每日生成
4. 推送日志出现 `success` 且用户可收到消息

---

## 6. 常见失败原因

1. RSS URL 无法访问或格式错误。
2. 来源虽然可访问，但没有新文章（URL 去重后不新增）。
3. `X-API-Key` 错误导致管理接口 401。
4. 微信凭据错误导致推送失败。

---

## 7. 你现在最推荐的落地路径

1. 先接 10~20 个稳定 RSS（含你关心的公众号资讯镜像源）。
2. 连续跑 3~7 天，观察抓取成功率和新增量。
3. 稳定后再扩展到更复杂来源（自定义解析规则、相似度去重、质量评分）。

