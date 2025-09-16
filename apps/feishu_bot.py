import logging
import asyncio
from core.config import feishu_config
from services.feishu_webhook import FeishuWebhook

feishu_webhook = None


async def init_task():
    """初始化飞书Webhook"""
    global feishu_webhook
    webhook_url = feishu_config.get('webhook_url')
    
    if not webhook_url:
        logging.error("未配置飞书Webhook URL")
        return
    
    feishu_webhook = FeishuWebhook(webhook_url)
    logging.info("飞书Webhook初始化完成")


async def start_task():
    """启动任务（飞书webhook不需要持续运行）"""
    logging.info("飞书Webhook服务已准备就绪")
    # 飞书webhook是被动接收，不需要像Telegram bot那样持续轮询
    while True:
        await asyncio.sleep(3600)  # 每小时检查一次服务状态


def close_all():
    """关闭所有连接"""
    logging.info("关闭飞书Webhook连接")


async def scheduled_task():
    """定时任务 - 检查sitemap更新"""
    await asyncio.sleep(5)  # 等待初始化完成
    
    global feishu_webhook
    if not feishu_webhook:
        logging.error("飞书Webhook未初始化")
        return
    
    # 导入RSS管理器
    from services.rss.manager import RSSManager
    
    # 创建RSS管理器实例
    rss_manager = RSSManager()
    
    while True:
        try:
            feeds = rss_manager.get_feeds()
            logging.info(f"定时任务开始检查订阅源更新，共 {len(feeds)} 个订阅")
            
            # 存储所有新增的URL用于关键词汇总
            all_new_urls = []
            
            for url in feeds:
                logging.info(f"正在检查订阅源: {url}")
                
                # 检查更新
                success, error_msg, dated_file, new_urls = rss_manager.add_feed(url)
                
                if success and dated_file and dated_file.exists():
                    # 发送更新通知
                    await send_update_notification(url, new_urls, dated_file)
                    if new_urls:
                        logging.info(f"订阅源 {url} 更新成功，发现 {len(new_urls)} 个新URL，已发送通知。")
                        all_new_urls.extend(new_urls)
                    else:
                        logging.info(f"订阅源 {url} 更新成功，无新增URL，已发送通知。")
                elif "今天已经更新过此sitemap" in error_msg:
                    logging.info(f"订阅源 {url} {error_msg}")
                else:
                    logging.warning(f"订阅源 {url} 更新失败: {error_msg}")
            
            # 发送关键词汇总
            if all_new_urls:
                await asyncio.sleep(10)  # 等待所有更新通知发送完成
                await send_keywords_summary(all_new_urls)
            
            logging.info("所有订阅源检查完成，等待下一次检查")
            await asyncio.sleep(3600)  # 1小时检查间隔
            
        except Exception as e:
            logging.error(f"检查订阅源更新失败: {str(e)}", exc_info=True)
            await asyncio.sleep(60)  # 出错后等待1分钟再试


async def send_update_notification(url: str, new_urls: list, dated_file=None):
    """发送更新通知"""
    global feishu_webhook
    if feishu_webhook:
        feishu_webhook.send_sitemap_update(url, new_urls, dated_file)


async def send_keywords_summary(all_new_urls: list):
    """发送关键词汇总"""
    global feishu_webhook
    if feishu_webhook:
        feishu_webhook.send_keywords_summary(all_new_urls)