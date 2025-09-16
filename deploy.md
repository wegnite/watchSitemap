# Cloudflare Workers 部署指南

## 快速部署步骤

### 1. 安装 Wrangler CLI
```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare
```bash
wrangler login
```
会自动打开浏览器进行OAuth登录。

### 3. 创建 KV 存储命名空间
```bash
# 生产环境
wrangler kv:namespace create SITEMAP_STORAGE

# 预览环境
wrangler kv:namespace create SITEMAP_STORAGE --preview
```

**重要**: 记下返回的 namespace IDs，需要更新到 `wrangler.toml` 文件中。

### 4. 更新配置文件

编辑 `wrangler.toml`，替换KV namespace IDs：

```toml
[[kv_namespaces]]
binding = "SITEMAP_STORAGE"
id = "替换为你的生产环境ID"
preview_id = "替换为你的预览环境ID"
```

### 5. 部署 Worker
```bash
wrangler deploy
```

### 6. 测试部署
```bash
# 访问状态接口
curl https://sitemap-monitor.你的用户名.workers.dev/status

# 手动触发检查
curl https://sitemap-monitor.你的用户名.workers.dev/check
```

## 详细配置说明

### 飞书 Webhook 配置
在 `worker.js` 第7行修改：
```javascript
const FEISHU_WEBHOOK_URL = '你的飞书webhook地址';
```

### 定时任务配置
在 `wrangler.toml` 中已配置每小时执行：
```toml
[triggers]
crons = ["0 * * * *"]
```

### 监控站点配置
在 `worker.js` 第9-15行修改监控的站点列表：
```javascript
const SITEMAP_URLS = [
  'https://poki.com/zh/sitemaps/index.xml',
  // 添加或修改你要监控的站点...
];
```

## 验证部署成功

1. **检查 Worker 状态**
   - 访问: `https://sitemap-monitor.你的用户名.workers.dev/status`
   - 应返回监控站点列表

2. **手动触发测试**
   - 访问: `https://sitemap-monitor.你的用户名.workers.dev/check`
   - 检查飞书群是否收到通知

3. **查看运行日志**
   ```bash
   wrangler tail
   ```

## 常见问题解决

### KV 存储问题
```bash
# 检查 KV namespace
wrangler kv:namespace list

# 查看存储的数据
wrangler kv:key list --binding SITEMAP_STORAGE
```

### 定时任务问题
- 定时任务可能需要等待最多1小时才开始运行
- 可以通过 `/check` 接口手动测试功能

### 飞书通知问题
- 确认 webhook URL 正确
- 检查飞书机器人是否有发送消息权限

## 成本说明

Cloudflare Workers 免费版本额度：
- 每天 100,000 次请求
- 每次执行最多 10ms CPU 时间
- KV 存储：每天 100,000 次读取，1,000 次写入

对于这个监控系统来说，免费额度完全够用。