# -*- coding: utf-8 -*-

"""
Solana代币监控系统 - FastAPI Web接口

本模块提供基于FastAPI的Web接口，用于：
1. 启动/停止代币监控
2. 查看监控状态和配置
3. 提供API接口供前端调用
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import Dict, Any
import sys
import os
from pathlib import Path

# Add parent directory to Python path for imports
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR.parent))

# Initialize FastAPI app
app = FastAPI(title="Solana Token Monitor")

# Configure templates and static files
TEMPLATES_DIR = BASE_DIR / "templates"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR = BASE_DIR.parent / "app" / "templates"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create and mount static directory
STATIC_DIR = TEMPLATES_DIR.parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

from app.modules.monitor import TokenMonitor
from app.modules.config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
    EMAIL_FROM, EMAIL_TO, MONITORING_INTERVAL
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Disable credentials for cross-origin requests
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# 全局变量
monitor = None
monitor_task = None

# 移除身份验证相关代码

@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    """
    获取监控状态API
    
    返回:
        Dict: 包含运行状态和配置信息的字典
    """
    global monitor_task
    return {
        "running": monitor_task is not None and not monitor_task.done(),
        "config": {
            "monitoring_interval": MONITORING_INTERVAL,
            "email_configured": bool(SMTP_USERNAME and SMTP_PASSWORD)
        }
    }

@app.post("/api/start")
async def start_monitoring():
    """
    启动监控API
    
    返回:
        Dict: 包含操作状态和消息的响应
    """
    global monitor, monitor_task
    if monitor_task and not monitor_task.done():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "监控已在运行中"}
        )
    
    try:
        monitor = TokenMonitor()
        monitor_task = asyncio.create_task(monitor.run())
        return {"status": "success", "message": "监控已启动"}
    except Exception as e:
        logging.error(f"启动监控失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"启动监控失败: {str(e)}"}
        )

@app.post("/api/stop")
async def stop_monitoring():
    """
    停止监控API
    
    返回:
        Dict: 包含操作状态和消息的响应
    """
    global monitor_task
    if monitor_task:
        monitor_task.cancel()
        return {"status": "success", "message": "监控已停止"}
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "没有正在运行的监控任务"}
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    主页路由
    
    功能:
    - 显示监控系统的Web界面
    - 提供当前监控状态
    - 显示系统配置信息
    
    参数:
        request: FastAPI请求对象
    
    返回:
        HTMLResponse: 渲染后的HTML页面
    """
    global monitor_task
    status = {
        'running': monitor_task is not None and not monitor_task.done(),
        'config': {
            'monitoring_interval': MONITORING_INTERVAL,
            'email_configured': bool(SMTP_USERNAME and SMTP_PASSWORD)
        }
    }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "status": status,
            "initial_status": status
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
