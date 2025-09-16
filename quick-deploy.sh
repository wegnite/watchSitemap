#!/bin/bash

echo "🚀 Cloudflare Workers 快速部署脚本"
echo "=================================="

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 已安装: $(node --version)"

# 检查是否安装了 wrangler
if ! command -v wrangler &> /dev/null; then
    echo "📦 安装 Wrangler CLI..."
    npm install -g wrangler
else
    echo "✅ Wrangler 已安装: $(wrangler --version)"
fi

# 检查是否已登录
echo ""
echo "🔐 检查 Cloudflare 登录状态..."
if ! wrangler whoami &> /dev/null; then
    echo "请登录 Cloudflare 账户..."
    wrangler login
else
    echo "✅ 已登录 Cloudflare"
fi

echo ""
echo "📊 创建 KV 存储命名空间..."

# 创建 KV namespace
echo "创建生产环境 KV namespace..."
PROD_KV=$(wrangler kv:namespace create SITEMAP_STORAGE --preview false 2>/dev/null | grep -o 'id = "[^"]*"' | head -1)

echo "创建预览环境 KV namespace..."  
PREVIEW_KV=$(wrangler kv:namespace create SITEMAP_STORAGE --preview true 2>/dev/null | grep -o 'id = "[^"]*"' | head -1)

if [ ! -z "$PROD_KV" ] && [ ! -z "$PREVIEW_KV" ]; then
    echo "✅ KV namespace 创建成功"
    echo "生产环境: $PROD_KV"
    echo "预览环境: $PREVIEW_KV"
    
    # 更新 wrangler.toml
    echo ""
    echo "📝 更新 wrangler.toml 配置..."
    
    # 备份原文件
    cp wrangler.toml wrangler.toml.backup
    
    # 替换 ID
    PROD_ID=$(echo $PROD_KV | grep -o '"[^"]*"' | tr -d '"')
    PREVIEW_ID=$(echo $PREVIEW_KV | grep -o '"[^"]*"' | tr -d '"')
    
    sed -i.bak "s/your-kv-namespace-id/$PROD_ID/g" wrangler.toml
    sed -i.bak "s/your-preview-kv-namespace-id/$PREVIEW_ID/g" wrangler.toml
    
    echo "✅ 配置文件已更新"
else
    echo "⚠️  KV namespace 可能已存在，继续部署..."
fi

echo ""
echo "🚀 部署 Worker..."
wrangler deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "📍 访问地址:"
    echo "   状态检查: https://sitemap-monitor.$(wrangler whoami | grep -o '@.*' | tr -d '@').workers.dev/status"
    echo "   手动触发: https://sitemap-monitor.$(wrangler whoami | grep -o '@.*' | tr -d '@').workers.dev/check"
    echo ""
    echo "🔍 查看日志:"
    echo "   wrangler tail"
    echo ""
    echo "⏰ 定时任务已设置为每小时执行一次"
    echo "📱 监控变化将通过飞书发送通知"
    echo ""
    echo "🎮 当前监控的游戏网站:"
    echo "   • Poki (中文)"
    echo "   • CrazyGames" 
    echo "   • GameDistribution"
    echo "   • GamePix"
    echo "   • Sprunki"
    
else
    echo "❌ 部署失败，请检查错误信息"
    exit 1
fi