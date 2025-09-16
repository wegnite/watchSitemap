import requests
import json
import logging
from typing import List, Optional
from pathlib import Path


class FeishuWebhook:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send_text(self, text: str) -> bool:
        """发送文本消息到飞书"""
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0:
                    logging.info("飞书消息发送成功")
                    return True
                else:
                    logging.error(f"飞书消息发送失败: {result.get('msg', 'Unknown error')}")
                    return False
            else:
                logging.error(f"飞书API请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"发送飞书消息时出错: {str(e)}")
            return False
    
    def send_markdown(self, title: str, content: str) -> bool:
        """发送Markdown格式消息到飞书"""
        try:
            payload = {
                "msg_type": "interactive",
                "card": {
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": content,
                                "tag": "lark_md"
                            }
                        }
                    ],
                    "header": {
                        "title": {
                            "content": title,
                            "tag": "plain_text"
                        }
                    }
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0:
                    logging.info("飞书Markdown消息发送成功")
                    return True
                else:
                    logging.error(f"飞书Markdown消息发送失败: {result.get('msg', 'Unknown error')}")
                    return False
            else:
                logging.error(f"飞书API请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"发送飞书Markdown消息时出错: {str(e)}")
            return False
    
    def send_sitemap_update(self, url: str, new_urls: List[str], sitemap_file: Optional[Path] = None) -> bool:
        """发送sitemap更新通知"""
        try:
            if new_urls:
                title = f"🎮 Sitemap更新通知 - {len(new_urls)}个新增链接"
                
                # 构建内容
                content = f"**订阅源:** {url}\n\n"
                content += f"**发现 {len(new_urls)} 个新增链接:**\n"
                
                for i, new_url in enumerate(new_urls[:10], 1):  # 最多显示10个
                    content += f"{i}. {new_url}\n"
                
                if len(new_urls) > 10:
                    content += f"\n... 还有 {len(new_urls) - 10} 个链接"
                    
            else:
                title = f"🎮 Sitemap检查完成"
                content = f"**订阅源:** {url}\n\n**状态:** 无新增链接"
            
            return self.send_markdown(title, content)
            
        except Exception as e:
            logging.error(f"发送sitemap更新通知时出错: {str(e)}")
            return False
    
    def send_keywords_summary(self, all_new_urls: List[str]) -> bool:
        """发送关键词汇总"""
        try:
            if not all_new_urls:
                return True
                
            title = f"📊 关键词汇总 - {len(all_new_urls)}个新链接"
            
            # 简单的关键词提取（基于URL路径）
            keywords = {}
            for url in all_new_urls:
                try:
                    # 提取路径中的关键词
                    path_parts = url.split('/')
                    for part in path_parts:
                        if part and len(part) > 2 and not part.isdigit():
                            # 简单清理
                            clean_part = part.replace('-', ' ').replace('_', ' ').lower()
                            if clean_part not in ['www', 'http', 'https', 'html', 'php', 'asp']:
                                keywords[clean_part] = keywords.get(clean_part, 0) + 1
                except:
                    continue
            
            # 按频率排序，取前10个关键词
            top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
            
            content = f"**本轮更新汇总:** {len(all_new_urls)} 个新链接\n\n"
            
            if top_keywords:
                content += "**热门关键词:**\n"
                for keyword, count in top_keywords:
                    content += f"• {keyword} ({count}次)\n"
            
            content += f"\n**总计新增链接数:** {len(all_new_urls)}"
            
            return self.send_markdown(title, content)
            
        except Exception as e:
            logging.error(f"发送关键词汇总时出错: {str(e)}")
            return False