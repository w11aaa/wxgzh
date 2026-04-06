# `.env` 保姆级配置教程（从 0 到可运行）

> 更新时间：2026-04-06
> 适用项目：微信公众号领域内容采集与每日推送助手

这份教程专门解决你提到的问题：

- `DATABASE_URL` 从哪里来？
- `REDIS_URL` 怎么拿？
- `ADMIN_API_KEY` 怎么设置？
- `WECHAT_*` 去哪里申请？

我按“**先跑起来，再接真实微信**”分成两阶段，照抄即可。

---

## 一、先复制 `.env` 模板

在项目根目录执行：

```bash
cp .env.example .env
```

然后打开 `.env` 文件编辑。

---

## 二、第一阶段（本地先跑通，10 分钟）

> 这一阶段先不追求真实微信推送，只保证服务可启动、可抓取、可生成日报。

把 `.env` 先填成下面这样：

```env
# 1) 数据库（使用 docker-compose 里的 postgres 容器）
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/wxgzh

# 2) Redis（使用 docker-compose 里的 redis 容器）
REDIS_URL=redis://redis:6379/0

# 3) 管理接口密钥（你自己定义，越长越好）
ADMIN_API_KEY=dev-change-to-your-secret-key-2026

# 4) 微信参数（先填占位，第二阶段再替换真实值）
WECHAT_TOKEN=test-token-2026
WECHAT_APP_ID=replace-later
WECHAT_APP_SECRET=replace-later
WECHAT_AES_KEY=
```

### 解释（你只要知道这个就够了）

1. `postgres@postgres:5432` 和 `redis://redis:6379` 里的主机名 `postgres/redis`，是 docker-compose 的服务名，不是公网地址。
2. `ADMIN_API_KEY` 就像后台密码，你自己生成，不需要去第三方平台申请。
3. `WECHAT_*` 先占位是为了让你先把系统流程跑通。

---

## 三、如何生成一个安全的 `ADMIN_API_KEY`

任选一种方式：

### 方法 A：OpenSSL

```bash
openssl rand -hex 32
```

生成示例（不要照抄）：

```text
4a9f...（64位十六进制）
```

把它写进 `.env`：

```env
ADMIN_API_KEY=这里填你生成的值
```

### 方法 B：Python

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

---

## 四、第二阶段（接入真实微信公众号）

> 这一步才是获取 `WECHAT_TOKEN / WECHAT_APP_ID / WECHAT_APP_SECRET / WECHAT_AES_KEY` 的关键。

## 1) 先准备公众号

你需要一个已开通开发能力的公众号（服务号/订阅号，能力存在差异）。

## 2) 登录微信公众平台

打开微信公众平台官网并登录你自己的公众号后台。

## 3) 获取 `WECHAT_APP_ID` 与 `WECHAT_APP_SECRET`

通常在“开发设置/基本配置”相关页面可找到：

- `AppID`  -> 填到 `WECHAT_APP_ID`
- `AppSecret` -> 填到 `WECHAT_APP_SECRET`

> 注意：`AppSecret` 是高敏感信息，不要提交到 Git。

## 4) 配置 `WECHAT_TOKEN`

在公众号“开发者配置”中，你需要填写一个 Token（自定义字符串）。

- 你在平台填什么，`.env` 的 `WECHAT_TOKEN` 就必须填同样的值。
- 建议用 32+ 位随机字符串。

## 5) `WECHAT_AES_KEY` 怎么办？

- 如果你用明文模式，可先留空。
- 如果你启用安全模式，平台会要求 EncodingAESKey，把它填到 `WECHAT_AES_KEY`。

## 6) 配置服务器地址（URL）

你需要一个公网可访问的回调地址，例如：

```text
https://your-domain.com/api/v1/wechat/callback
```

然后在公众平台里提交 URL + Token（+ AESKey，如启用安全模式）。

系统会通过 `GET /api/v1/wechat/callback` 做验签。

---

## 五、如何验证 `.env` 配置是否正确

### 1) 启动服务

```bash
docker compose up --build
```

### 2) 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

期望：

```json
{"status":"ok"}
```

### 3) 测试管理密钥是否生效

#### 不带 key（应失败）

```bash
curl -X POST http://localhost:8000/api/v1/sources \
  -H 'Content-Type: application/json' \
  -d '{"name":"x","source_type":"rss","url":"https://example.com/rss.xml","enabled":true}'
```

期望：`401`

#### 带 key（应成功）

```bash
curl -X POST http://localhost:8000/api/v1/sources \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: 你的ADMIN_API_KEY' \
  -d '{"name":"x","source_type":"rss","url":"https://example.com/rss.xml","enabled":true}'
```

期望：返回 source JSON。

### 4) 微信验签回调验证

当你在公众平台配置 URL 后，平台会请求：

- `GET /api/v1/wechat/callback?signature=...&timestamp=...&nonce=...&echostr=...`

如果 Token 一致且 URL 可访问，会通过验证。

---

## 六、最常见的坑（你八成会遇到）

1. **把容器内地址和本机地址搞混**
   - 容器互联用 `postgres` / `redis`
   - 本机直连一般是 `localhost`

2. **`ADMIN_API_KEY` 没放到请求头**
   - 必须用：`X-API-Key: ...`

3. **公众号后台 Token 与 `.env` 不一致**
   - 一字不差才行。

4. **回调 URL 不是公网 HTTPS**
   - 本地 `localhost` 不能直接给微信服务器访问。

5. **把 `.env` 提交到 Git**
   - 绝对不要提交。

---

## 七、给你一份可直接改的最终模板

```env
APP_NAME=wx-content-assistant
APP_ENV=dev
APP_PORT=8000

DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/wxgzh
REDIS_URL=redis://redis:6379/0
ADMIN_API_KEY=替换成你生成的随机密钥

WECHAT_TOKEN=替换成你在公众号后台配置的Token
WECHAT_APP_ID=替换成公众号AppID
WECHAT_APP_SECRET=替换成公众号AppSecret
WECHAT_AES_KEY=明文模式可留空，安全模式填EncodingAESKey
WECHAT_API_BASE=https://api.weixin.qq.com
```

---

## 八、你下一步直接做什么

1. 先按“第二章”填占位值并启动服务。
2. 再按“第四章”去公众号后台拿真实 `WECHAT_*` 替换。
3. 最后按“第五章”做验证。

如果你愿意，我下一步可以直接给你一份“你当前机器可执行的命令清单（逐条复制粘贴版）”。
