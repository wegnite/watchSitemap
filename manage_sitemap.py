#!/usr/bin/env python3
"""
Sitemap监控管理脚本
用于添加、删除和查看sitemap监控
"""
import argparse
import sys
from services.rss.manager import RSSManager
from services.feishu_webhook import FeishuWebhook


def main():
    parser = argparse.ArgumentParser(description='Sitemap监控管理工具')
    parser.add_argument('action', choices=['add', 'remove', 'list', 'test'], 
                       help='操作类型: add(添加), remove(删除), list(列出), test(测试通知)')
    parser.add_argument('--url', help='Sitemap URL')
    
    args = parser.parse_args()
    
    manager = RSSManager()
    
    if args.action == 'list':
        feeds = manager.get_feeds()
        if feeds:
            print(f"\n当前监控的sitemap ({len(feeds)}个):")
            for i, feed in enumerate(feeds, 1):
                print(f"{i}. {feed}")
        else:
            print("\n暂无监控的sitemap")
    
    elif args.action == 'add':
        if not args.url:
            print("错误: 添加sitemap需要提供--url参数")
            sys.exit(1)
        
        if not args.url.endswith('.xml'):
            print("警告: URL应该指向一个XML格式的sitemap文件")
        
        print(f"正在添加sitemap监控: {args.url}")
        success, error_msg, dated_file, new_urls = manager.add_feed(args.url)
        
        if success:
            print("✅ 添加成功!")
            if new_urls:
                print(f"发现 {len(new_urls)} 个新URL")
                # 测试飞书通知
                webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/d55d799f-5b53-4932-84b6-f3316ff7b5c2"
                feishu = FeishuWebhook(webhook_url)
                if feishu.send_sitemap_update(args.url, new_urls, dated_file):
                    print("✅ 飞书通知发送成功")
                else:
                    print("❌ 飞书通知发送失败")
        else:
            print(f"❌ 添加失败: {error_msg}")
    
    elif args.action == 'remove':
        if not args.url:
            print("错误: 删除sitemap需要提供--url参数")
            sys.exit(1)
        
        print(f"正在删除sitemap监控: {args.url}")
        success, error_msg = manager.remove_feed(args.url)
        
        if success:
            print("✅ 删除成功!")
        else:
            print(f"❌ 删除失败: {error_msg}")
    
    elif args.action == 'test':
        print("正在测试飞书通知...")
        webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/d55d799f-5b53-4932-84b6-f3316ff7b5c2"
        feishu = FeishuWebhook(webhook_url)
        
        success = feishu.send_text("🎮 Sitemap监控系统测试消息")
        if success:
            print("✅ 测试成功! 飞书通知正常工作")
        else:
            print("❌ 测试失败! 请检查飞书webhook配置")


if __name__ == "__main__":
    main()