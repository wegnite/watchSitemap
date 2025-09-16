# 游戏站Sitemap监控系统 - 飞书版

基于飞书Webhook的游戏站sitemap自动监控和通知系统。

## ✨ 功能特点

- **自动监控**: 每小时自动检查sitemap变化
- **飞书通知**: 通过飞书Webhook发送实时通知
- **多站点支持**: 同时监控多个游戏网站
- **智能对比**: 自动识别新增链接和变化
- **关键词汇总**: 提供新增内容的关键词统计
- **日志记录**: 完整的操作和错误日志

## 🎮 当前监控站点

1. **Poki (中文)** - https://poki.com/zh/sitemaps/index.xml
2. **CrazyGames** - https://www.crazygames.com/sitemap-index.xml  
3. **GameDistribution** - https://gamedistribution.com/sitemap-index.xml
4. **GamePix** - https://www.gamepix.com/sitemaps/index.xml
5. **Sprunki** - https://sprunki.com/sitemap.xml

## 🚀 快速开始

### 1. 环境准备
```bash
# Python 3.8+
python3 --version

# 进入项目目录
cd watchSitemap
```

### 2. 安装依赖
```bash
# 激活虚拟环境
source venv/bin/activate

# 已安装的依赖包括:
# - requests (HTTP请求)
# - python-dotenv (环境变量)
```

### 3. 配置飞书Webhook
配置文件 `.env` 已包含飞书webhook URL:
```
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/d55d799f-5b53-4932-84b6-f3316ff7b5c2"
```

### 4. 启动监控服务
```bash
# 方式1: 使用脚本启动（推荐）
./restart-feishu.sh

# 方式2: 直接启动
python feishu-bot.py
```

## 📊 使用方法

### 管理sitemap监控
```bash
# 查看所有监控的sitemap
python manage_sitemap.py list

# 添加新的sitemap监控
python manage_sitemap.py add --url "https://example.com/sitemap.xml"

# 删除sitemap监控
python manage_sitemap.py remove --url "https://example.com/sitemap.xml"

# 测试飞书通知
python manage_sitemap.py test
```

### 查看运行状态
```bash
# 查看实时日志
tail -f /tmp/feishu-bot.log

# 查看进程状态
ps aux | grep feishu-bot

# 停止服务
kill [PID]
```

## 🔔 通知内容

### 1. 初始监控通知
当系统开始监控新sitemap时，会发送包含当前状态的通知。

### 2. 更新通知 
发现新增链接时会发送详细通知，包括:
- 新增链接数量
- 具体的新增URL列表（最多显示10个）
- 时间戳

### 3. 关键词汇总
基于新增URL的路径提取关键词，提供内容趋势概览。

## 📁 项目结构

```
watchSitemap/
├── apps/                          # 应用层
│   ├── feishu_bot.py              # 飞书机器人服务
│   └── telegram_bot.py            # 原Telegram机器人（已弃用）
├── services/                      # 服务层
│   ├── feishu_webhook.py          # 飞书Webhook服务
│   └── rss/                       # RSS/Sitemap管理
│       ├── manager.py             # Sitemap下载和对比
│       └── commands.py            # 原Telegram命令（已弃用）
├── core/                          # 核心配置
│   └── config.py                  # 配置管理
├── storage/                       # 数据存储
│   └── rss/                       # Sitemap数据存储
│       ├── config/feeds.json      # 监控列表
│       └── sitemaps/              # 下载的sitemap文件
├── feishu-bot.py                  # 飞书版主程序
├── manage_sitemap.py              # sitemap管理工具
├── restart-feishu.sh              # 飞书服务启动脚本
├── test_feishu.py                 # 飞书功能测试
└── .env                           # 环境变量配置
```

## ⏰ 运行机制

1. **初始化**: 加载配置，初始化飞书Webhook连接
2. **定时检查**: 每小时自动检查所有监控的sitemap
3. **内容对比**: 下载新sitemap并与上次保存的版本对比
4. **通知发送**: 发现变化时通过飞书发送通知
5. **日志记录**: 所有操作记录到 `/tmp/feishu-bot.log`

## 🛠️ 技术特点

- **异步处理**: 使用asyncio提高性能
- **错误处理**: 完善的异常处理和重试机制  
- **数据持久化**: 自动保存sitemap历史版本
- **增量检测**: 智能对比算法，只通知真正的新增内容
- **防重复**: 同一天不会重复下载相同sitemap

## 📝 日志示例

```
2025-09-16 17:26:43,535 - INFO - 定时任务开始检查订阅源更新，共 6 个订阅
2025-09-16 17:26:44,018 - INFO - 正在检查订阅源: https://poki.com/zh/sitemaps/index.xml
2025-09-16 17:26:44,425 - INFO - 订阅源更新成功，无新增URL，已发送通知
2025-09-16 17:26:46,130 - INFO - 所有订阅源检查完成，等待下一次检查
```

## 🎯 下次检查时间

系统将在 **1小时** 后进行下一次自动检查（约 18:26）

---

**系统状态**: ✅ 运行中  
**监控站点**: 6个  
**通知方式**: 飞书Webhook  
**检查频率**: 每小时  