import logging
import os
import asyncio

from apps import feishu_bot
from core.config import feishu_config


def main():
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
        level=logging.INFO
    )

    # 检查飞书配置
    webhook_url = str(feishu_config['webhook_url'])
    logging.info(f'飞书webhook URL: {webhook_url}')

    if not webhook_url or webhook_url == "":
        logging.error("未配置飞书Webhook URL，请设置FEISHU_WEBHOOK_URL环境变量")
        return

    # 设置事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tasks = []
    
    # 添加飞书bot任务
    tasks.append(feishu_bot.init_task())
    tasks.append(feishu_bot.start_task())
    tasks.append(feishu_bot.scheduled_task())

    try:
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Ctrl-C close!!")
        feishu_bot.close_all()
    finally:
        loop.close()


if __name__ == '__main__':
    main()