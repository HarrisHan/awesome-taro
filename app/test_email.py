#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
邮件发送测试模块

本模块用于测试监控系统的邮件发送功能，包括：
- SMTP服务器连接测试
- 邮件发送认证测试
- 本地邮件发送备用方案测试

测试流程：
1. 首先尝试通过SMTP发送测试邮件
2. 如果SMTP发送失败，自动切换到本地邮件发送模式
3. 记录详细的测试日志
"""

import asyncio
import logging
from app.modules.monitor import TokenMonitor

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_email():
    """
    测试邮件发送功能
    
    测试步骤：
    1. 初始化监控器
    2. 尝试SMTP邮件发送
    3. 如果失败，切换到本地邮件发送
    4. 清理资源
    
    异常处理：
    - 捕获所有SMTP相关错误
    - 自动切换到备用发送方式
    - 记录详细错误信息
    """
    monitor = TokenMonitor()
    await monitor.initialize()
    try:
        logging.info("正在测试SMTP邮件发送...")
        await monitor.send_email_alert(
            "测试告警: Solana监控系统",
            "这是来自Solana代币监控系统的测试告警消息。\n"
            "时间: " + asyncio.get_event_loop().time().__str__()
        )
    except Exception as e:
        logging.error(f"SMTP邮件测试失败: {str(e)}")
        # 尝试本地邮件发送作为备用方案
        logging.info("正在尝试本地邮件发送...")
        from config import MAIL_DELIVERY_MODE
        import os
        os.environ['MAIL_DELIVERY_MODE'] = 'local'
        await monitor.send_email_alert(
            "测试告警: Solana监控系统 (本地发送)",
            "这是通过本地邮件服务发送的测试告警消息。\n"
            "时间: " + asyncio.get_event_loop().time().__str__()
        )
    finally:
        if monitor.session:
            await monitor.session.close()

if __name__ == "__main__":
    asyncio.run(test_email())
