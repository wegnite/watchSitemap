/**
 * Cloudflare Workers - 游戏站Sitemap监控系统
 * 用于监控游戏网站sitemap变化并通过飞书发送通知
 */

// 配置常量
const FEISHU_WEBHOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/d55d799f-5b53-4932-84b6-f3316ff7b5c2';

// 监控的sitemap列表
const SITEMAP_URLS = [
  'https://poki.com/zh/sitemaps/index.xml',
  'https://www.crazygames.com/sitemap-index.xml', 
  'https://gamedistribution.com/sitemap-index.xml',
  'https://www.gamepix.com/sitemaps/index.xml',
  'https://sprunki.com/sitemap.xml'
];

/**
 * 飞书通知服务
 */
class FeishuService {
  constructor(webhookUrl) {
    this.webhookUrl = webhookUrl;
  }

  async sendText(text) {
    try {
      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          msg_type: 'text',
          content: {
            text: text
          }
        })
      });

      const result = await response.json();
      return result.StatusCode === 0;
    } catch (error) {
      console.error('发送飞书文本消息失败:', error);
      return false;
    }
  }

  async sendMarkdown(title, content) {
    try {
      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          msg_type: 'interactive',
          card: {
            elements: [
              {
                tag: 'div',
                text: {
                  content: content,
                  tag: 'lark_md'
                }
              }
            ],
            header: {
              title: {
                content: title,
                tag: 'plain_text'
              }
            }
          }
        })
      });

      const result = await response.json();
      return result.StatusCode === 0;
    } catch (error) {
      console.error('发送飞书Markdown消息失败:', error);
      return false;
    }
  }

  async sendSitemapUpdate(url, newUrls = []) {
    try {
      let title, content;
      
      if (newUrls.length > 0) {
        title = `🎮 Sitemap更新通知 - ${newUrls.length}个新增链接`;
        content = `**订阅源:** ${url}\\n\\n`;
        content += `**发现 ${newUrls.length} 个新增链接:**\\n`;
        
        for (let i = 0; i < Math.min(newUrls.length, 10); i++) {
          content += `${i + 1}. ${newUrls[i]}\\n`;
        }
        
        if (newUrls.length > 10) {
          content += `\\n... 还有 ${newUrls.length - 10} 个链接`;
        }
      } else {
        title = `🎮 Sitemap检查完成`;
        content = `**订阅源:** ${url}\\n\\n**状态:** 无新增链接`;
      }

      return await this.sendMarkdown(title, content);
    } catch (error) {
      console.error('发送sitemap更新通知失败:', error);
      return false;
    }
  }

  async sendKeywordsSummary(allNewUrls) {
    try {
      if (allNewUrls.length === 0) return true;

      const title = `📊 关键词汇总 - ${allNewUrls.length}个新链接`;
      
      // 简单的关键词提取
      const keywords = {};
      for (const url of allNewUrls) {
        try {
          const pathParts = url.split('/');
          for (const part of pathParts) {
            if (part && part.length > 2 && !part.match(/^\\d+$/)) {
              const cleanPart = part.replace(/-/g, ' ').replace(/_/g, ' ').toLowerCase();
              if (!['www', 'http', 'https', 'html', 'php', 'asp'].includes(cleanPart)) {
                keywords[cleanPart] = (keywords[cleanPart] || 0) + 1;
              }
            }
          }
        } catch (e) {
          continue;
        }
      }

      // 按频率排序，取前10个
      const topKeywords = Object.entries(keywords)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);

      let content = `**本轮更新汇总:** ${allNewUrls.length} 个新链接\\n\\n`;
      
      if (topKeywords.length > 0) {
        content += '**热门关键词:**\\n';
        for (const [keyword, count] of topKeywords) {
          content += `• ${keyword} (${count}次)\\n`;
        }
      }

      content += `\\n**总计新增链接数:** ${allNewUrls.length}`;

      return await this.sendMarkdown(title, content);
    } catch (error) {
      console.error('发送关键词汇总失败:', error);
      return false;
    }
  }
}

/**
 * Sitemap管理器
 */
class SitemapManager {
  constructor() {
    this.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36';
  }

  async downloadSitemap(url) {
    try {
      console.log(`下载sitemap: ${url}`);
      
      const response = await fetch(url, {
        headers: {
          'User-Agent': this.userAgent
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const content = await response.text();
      console.log(`sitemap下载成功: ${url}`);
      return { success: true, content, error: null };
    } catch (error) {
      console.error(`下载sitemap失败: ${url}`, error);
      return { success: false, content: null, error: error.message };
    }
  }

  extractUrlsFromSitemap(content) {
    try {
      // 简单的XML URL提取，适用于sitemap格式
      const urlPattern = /<loc>(.*?)<\\/loc>/g;
      const urls = [];
      let match;
      
      while ((match = urlPattern.exec(content)) !== null) {
        urls.push(match[1]);
      }
      
      return urls;
    } catch (error) {
      console.error('提取URL失败:', error);
      return [];
    }
  }

  compareUrls(currentUrls, previousUrls) {
    const currentSet = new Set(currentUrls);
    const previousSet = new Set(previousUrls);
    
    return Array.from(currentSet).filter(url => !previousSet.has(url));
  }
}

/**
 * KV存储服务
 */
class StorageService {
  constructor() {
    this.namespace = 'SITEMAP_STORAGE';
  }

  async getSitemapData(url) {
    try {
      const key = this.generateKey(url);
      const data = await SITEMAP_STORAGE.get(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error(`获取KV数据失败: ${url}`, error);
      return null;
    }
  }

  async saveSitemapData(url, data) {
    try {
      const key = this.generateKey(url);
      await SITEMAP_STORAGE.put(key, JSON.stringify(data));
      return true;
    } catch (error) {
      console.error(`保存KV数据失败: ${url}`, error);
      return false;
    }
  }

  generateKey(url) {
    // 生成安全的KV key
    return 'sitemap_' + btoa(url).replace(/[^a-zA-Z0-9]/g, '_');
  }
}

/**
 * 主要的监控逻辑
 */
async function checkSitemapUpdates() {
  const feishu = new FeishuService(FEISHU_WEBHOOK_URL);
  const sitemapManager = new SitemapManager();
  const storage = new StorageService();
  
  console.log(`开始检查 ${SITEMAP_URLS.length} 个sitemap`);
  
  const allNewUrls = [];
  
  for (const url of SITEMAP_URLS) {
    try {
      console.log(`检查sitemap: ${url}`);
      
      // 下载当前sitemap
      const downloadResult = await sitemapManager.downloadSitemap(url);
      if (!downloadResult.success) {
        console.error(`跳过失败的sitemap: ${url}`);
        continue;
      }
      
      // 提取URLs
      const currentUrls = sitemapManager.extractUrlsFromSitemap(downloadResult.content);
      console.log(`提取到 ${currentUrls.length} 个URL from ${url}`);
      
      // 获取之前保存的数据
      const previousData = await storage.getSitemapData(url);
      const previousUrls = previousData ? previousData.urls : [];
      
      // 比较找出新增URL
      const newUrls = sitemapManager.compareUrls(currentUrls, previousUrls);
      console.log(`发现 ${newUrls.length} 个新URL in ${url}`);
      
      // 保存当前数据
      await storage.saveSitemapData(url, {
        urls: currentUrls,
        lastCheck: new Date().toISOString(),
        urlCount: currentUrls.length
      });
      
      // 发送通知
      if (newUrls.length > 0) {
        allNewUrls.push(...newUrls);
        await feishu.sendSitemapUpdate(url, newUrls);
        console.log(`已发送更新通知: ${url} (${newUrls.length} 个新URL)`);
      } else {
        await feishu.sendSitemapUpdate(url, []);
        console.log(`已发送检查完成通知: ${url}`);
      }
      
      // 添加延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.error(`处理sitemap时出错: ${url}`, error);
    }
  }
  
  // 发送汇总
  if (allNewUrls.length > 0) {
    console.log(`发送关键词汇总，总计 ${allNewUrls.length} 个新URL`);
    await feishu.sendKeywordsSummary(allNewUrls);
  }
  
  console.log('所有sitemap检查完成');
}

/**
 * Cloudflare Workers 事件处理器
 */
export default {
  async fetch(request, env, ctx) {
    // 处理HTTP请求（用于手动触发或状态检查）
    const url = new URL(request.url);
    
    if (url.pathname === '/check') {
      // 手动触发检查
      ctx.waitUntil(checkSitemapUpdates());
      return new Response('sitemap检查已触发', { status: 200 });
    }
    
    if (url.pathname === '/status') {
      // 状态检查
      return new Response(JSON.stringify({
        status: 'running',
        monitored_sites: SITEMAP_URLS.length,
        sites: SITEMAP_URLS
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('游戏站Sitemap监控系统 - Cloudflare Workers版本', { status: 200 });
  },

  async scheduled(controller, env, ctx) {
    // 处理定时任务（cron job）
    console.log('定时任务触发，开始检查sitemap更新');
    ctx.waitUntil(checkSitemapUpdates());
  }
};