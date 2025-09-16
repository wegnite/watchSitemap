# 游戏站Sitemap监控系统 - Cloudflare Workers版

基于Cloudflare Workers的游戏站sitemap自动监控和飞书通知系统，无需服务器，自动定时执行。

## ✨ 特点

- **☁️ 无服务器**: 基于Cloudflare Workers，零服务器维护
- **⏰ 自动定时**: 每小时自动检查，支持cron表达式配置
- **📱 飞书通知**: 实时推送更新通知到飞书
- **💾 持久化存储**: 使用Cloudflare KV存储历史数据
- **🚀 高性能**: 全球CDN加速，响应快速
- **💰 低成本**: 免费额度足够个人使用

## 🎮 监控站点

- **Poki (中文)** - https://poki.com/zh/sitemaps/index.xml
- **CrazyGames** - https://www.crazygames.com/sitemap-index.xml
- **GameDistribution** - https://gamedistribution.com/sitemap-index.xml
- **GamePix** - https://www.gamepix.com/sitemaps/index.xml
- **Sprunki** - https://sprunki.com/sitemap.xml

## 🚀 部署步骤

### 1. 准备工作

确保你有：
- Cloudflare账户
- GitHub账户
- Node.js 环境（本地开发用）

### 2. 克隆并配置

```bash
# 克隆仓库
git clone https://github.com/wegnite/watchSitemap.git
cd watchSitemap

# 安装Wrangler CLI (Cloudflare Workers开发工具)
npm install -g wrangler

# 登录Cloudflare
wrangler login
```

### 3. 创建KV命名空间

```bash
# 创建生产环境KV存储
wrangler kv:namespace create SITEMAP_STORAGE

# 创建预览环境KV存储  
wrangler kv:namespace create SITEMAP_STORAGE --preview
```

记下输出的namespace ID，更新 `wrangler.toml` 中的配置：

```toml
[[kv_namespaces]]
binding = "SITEMAP_STORAGE"
id = "你的-kv-namespace-id"
preview_id = "你的-preview-kv-namespace-id"
```

### 4. 配置飞书Webhook

在 `worker.js` 中更新飞书Webhook URL：

```javascript
const FEISHU_WEBHOOK_URL = '你的飞书webhook地址';
```

### 5. 部署到Cloudflare

```bash
# 部署到Cloudflare Workers
wrangler deploy

# 查看部署日志
wrangler tail
```

### 6. 设置定时任务

定时任务已在 `wrangler.toml` 中配置：

```toml
[triggers]
crons = ["0 * * * *"]  # 每小时执行一次
```

其他cron表达式示例：
- `"*/30 * * * *"` - 每30分钟
- `"0 */2 * * *"` - 每2小时
- `"0 9 * * *"` - 每天上午9点

## 📡 API接口

部署后可通过以下接口管理：

### 手动触发检查
```bash
curl https://your-worker.your-subdomain.workers.dev/check
```

### 查看系统状态
```bash
curl https://your-worker.your-subdomain.workers.dev/status
```

## 🛠️ 本地开发

```bash
# 安装依赖
npm install

# 本地开发服务器
npm run dev

# 部署到生产环境
npm run deploy

# 查看实时日志
npm run tail
```

## 📊 监控和日志

### Cloudflare Dashboard
- 访问 [Cloudflare Dashboard](https://dash.cloudflare.com)
- 进入 Workers & Pages
- 查看 `sitemap-monitor` worker
- 监控请求量、错误率等指标

### 实时日志
```bash
wrangler tail --format=pretty
```

## 🔧 自定义配置

### 修改监控站点

编辑 `worker.js` 中的 `SITEMAP_URLS` 数组：

```javascript
const SITEMAP_URLS = [
  'https://your-site.com/sitemap.xml',
  // 添加更多站点...
];
```

### 修改检查频率

编辑 `wrangler.toml` 中的cron表达式：

```toml
[triggers]
crons = ["0 */4 * * *"]  # 改为每4小时检查一次
```

## 💡 使用技巧

1. **测试部署**: 使用 `wrangler dev` 在本地测试
2. **查看KV数据**: 使用 `wrangler kv:key list --binding SITEMAP_STORAGE`
3. **监控费用**: 免费额度包括每天100,000次请求
4. **性能优化**: Worker会自动缓存和优化，无需额外配置

## 🔍 故障排除

### 常见问题

**1. KV存储访问失败**
```bash
# 检查KV namespace是否正确创建
wrangler kv:namespace list
```

**2. 定时任务不触发**
- 检查 `wrangler.toml` 中的cron表达式
- 确认Worker已正确部署
- 查看Cloudflare Dashboard中的触发记录

**3. 飞书通知失败**
- 检查webhook URL是否正确
- 确认飞书机器人权限设置

### 日志调试

```bash
# 查看详细日志
wrangler tail --format=json

# 过滤特定日志
wrangler tail | grep "ERROR"
```

## 📈 扩展功能

### 添加其他通知方式

可以轻松扩展支持：
- Slack
- Discord  
- 企业微信
- 邮件通知

### 数据分析

利用Cloudflare Analytics：
- 监控执行频率
- 分析错误率
- 追踪性能指标

---

**部署状态**: 🚀 准备就绪  
**监控频率**: 每小时  
**通知方式**: 飞书Webhook  
**存储**: Cloudflare KV  