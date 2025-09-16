#!/usr/bin/env python3
"""
测试飞书通知功能的脚本
"""
import asyncio
from services.feishu_webhook import FeishuWebhook
from services.rss.manager import RSSManager

async def test_feishu_notification():
    """测试飞书通知功能"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/d55d799f-5b53-4932-84b6-f3316ff7b5c2"
    feishu = FeishuWebhook(webhook_url)
    
    # 测试文本消息
    print("测试发送文本消息...")
    success = feishu.send_text("🎮 Sitemap监控机器人测试消息")
    print(f"文本消息发送结果: {success}")
    
    await asyncio.sleep(2)
    
    # 测试Markdown消息
    print("测试发送Markdown消息...")
    title = "🎮 Sitemap监控测试"
    content = """**功能测试:**
• 飞书Webhook集成 ✅
• Markdown格式支持 ✅ 
• 链接监控准备就绪 ✅

**下一步:** 添加sitemap监控链接开始使用"""
    
    success = feishu.send_markdown(title, content)
    print(f"Markdown消息发送结果: {success}")
    
    await asyncio.sleep(2)
    
    # 测试sitemap更新通知
    print("测试sitemap更新通知...")
    test_urls = [
        "https://example.com/game1",
        "https://example.com/game2",
        "https://example.com/game3"
    ]
    success = feishu.send_sitemap_update("https://example.com/sitemap.xml", test_urls)
    print(f"sitemap更新通知发送结果: {success}")
    
    await asyncio.sleep(2)
    
    # 测试关键词汇总
    print("测试关键词汇总...")
    test_urls_for_summary = [
        "https://game-site.com/action/shooter/game1",
        "https://game-site.com/action/rpg/game2", 
        "https://game-site.com/puzzle/strategy/game3",
        "https://game-site.com/action/adventure/game4"
    ]
    success = feishu.send_keywords_summary(test_urls_for_summary)
    print(f"关键词汇总发送结果: {success}")

def test_rss_manager():
    """测试RSS管理器功能"""
    print("\n测试RSS管理器...")
    manager = RSSManager()
    
    # 添加一个测试sitemap（这里使用一个公开的sitemap作为测试）
    test_sitemap_url = "https://www.sitemaps.org/sitemap.xml"
    print(f"添加测试sitemap: {test_sitemap_url}")
    
    success, error_msg, dated_file, new_urls = manager.add_feed(test_sitemap_url)
    print(f"添加结果: {success}, 错误信息: {error_msg}")
    if new_urls:
        print(f"发现新URL数量: {len(new_urls)}")
    
    # 列出所有feeds
    feeds = manager.get_feeds()
    print(f"当前监控的feeds: {feeds}")

if __name__ == "__main__":
    print("开始测试飞书通知功能...\n")
    
    # 测试RSS管理器
    test_rss_manager()
    
    # 测试飞书通知
    asyncio.run(test_feishu_notification())
    
    print("\n测试完成！")