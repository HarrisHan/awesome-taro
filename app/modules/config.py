# -*- coding: utf-8 -*-

"""
Solana代币监控系统 - 配置模块

本模块负责管理系统的所有配置参数，包括：
- Solana RPC连接设置
- 邮件服务器配置
- 监控间隔和阈值设置

配置优先级：
1. 环境变量
2. .env文件
3. 默认值
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# 从.env文件加载环境变量
load_dotenv()

# 基础配置
BASE_DIR = Path(__file__).parent.parent  # 项目根目录

# Solana配置
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')  # Solana RPC节点URL

# 邮件配置
# 邮件发送模式：'smtp'使用SMTP服务器，'local'使用本地邮件服务
MAIL_DELIVERY_MODE = os.getenv('MAIL_DELIVERY_MODE', 'smtp')

# SMTP服务器设置
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')  # SMTP服务器地址
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))  # SMTP服务器端口
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')  # SMTP用户名
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # SMTP密码（QQ邮箱需要使用授权码）

# 邮件地址配置
EMAIL_FROM = os.getenv('EMAIL_FROM', '')  # 发件人地址
EMAIL_TO = os.getenv('EMAIL_TO', '')  # 收件人地址

# 监控配置
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '300'))  # 监控间隔（秒），默认5分钟
