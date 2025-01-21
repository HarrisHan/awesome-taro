#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代币监控测试数据生成器

本模块用于生成测试数据，用以验证代币监控系统的功能：
- 生成满足条件的代币数据
- 模拟多个买家地址
- 设置合适的价格变化
"""

import asyncio
from datetime import datetime, timedelta
from app.modules.monitor import TokenMonitor, TokenMetrics

async def generate_test_data():
    """生成测试数据并添加到监控器中"""
    monitor = TokenMonitor()
    await monitor.initialize()
    
    # 创建测试代币数据
    test_token = TokenMetrics(
        address="So11111111111111111111111111111111111111112",  # 使用SOL代币地址作为测试
        initial_price=100.0,
        current_price=104.0  # 4%的价格上涨
    )
    
    # 生成70个不同的买家地址
    for i in range(70):
        test_token.add_buyer(f"buyer{i}")
    
    # 添加到监控器
    monitor.tokens[test_token.address] = test_token
    
    print(f"已生成测试数据:")
    print(f"代币地址: {test_token.address}")
    print(f"买家数量: {test_token.unique_buyers_count}")
    print(f"价格变化: {test_token.price_change_percentage:.2f}%")
    
    return monitor

if __name__ == "__main__":
    asyncio.run(generate_test_data())
