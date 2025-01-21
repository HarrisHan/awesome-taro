# -*- coding: utf-8 -*-

"""
Solana代币监控系统 - FastAPI Web接口

本模块提供基于FastAPI的Web接口，用于：
1. 启动/停止代币监控
2. 查看监控状态和配置
3. 提供API接口供前端调用
4. 实现基本的身份验证
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import jwt
import secrets
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
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME,
    EMAIL_FROM, EMAIL_TO, MONITORING_INTERVAL
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Solana Token Monitor")
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

# JWT配置
JWT_SECRET = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Handle OPTIONS requests without authentication
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """
    Handle OPTIONS requests for CORS preflight
    
    参数:
        request: FastAPI请求对象
        path: 请求路径
        
    返回:
        Response: 空响应，带有CORS头
    """
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
            "Access-Control-Max-Age": "600",
        }
    )

# 全局变量
monitor = None
monitor_task = None

async def verify_auth(request: Request):
    """
    验证Basic Auth或JWT令牌
    
    参数:
        request: FastAPI请求对象
        
    返回:
        str: 用户名，如果验证失败则抛出异常
    """
    logger = logging.getLogger(__name__)
    
    # 首先尝试Basic Auth
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Basic "):
        try:
            import base64
            decoded = base64.b64decode(auth[6:]).decode()
            username, password = decoded.split(":")
            logger.debug(f"Attempting authentication for user: {username}")
            
            # 检查应用程序凭据
            if username == "1259767623" and password == "g1259767623":
                logger.info(f"Successful app authentication for user: {username}")
                return username
                
            # 检查隧道凭据
            if username == "user" and password == "3535437f4587fc9138cc84ce9d25593e":
                logger.info("Successful tunnel authentication")
                return "tunnel_user"
                
            logger.warning(f"Invalid credentials for user: {username}")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            pass
    else:
        logger.debug("No Basic Auth header found")
    
    # 如果Basic Auth失败，尝试JWT
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            username = payload.get("sub")
            logger.info(f"Successful JWT authentication for user: {username}")
            return username
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            pass
    else:
        logger.debug("No JWT token found")
    
    logger.warning("Authentication failed - no valid credentials found")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Basic realm='Login Required'"}
    )

@app.post("/api/login")
async def login(response: Response, credentials: HTTPBasicCredentials):
    """
    登录API
    
    参数:
        response: FastAPI响应对象
        credentials: 用户凭据
        
    返回:
        Dict: 包含登录状态的响应
    """
    correct_username = "1259767623"
    correct_password = "g1259767623"
    
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"),
        correct_username.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"),
        correct_password.encode("utf8")
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成JWT令牌
    token = jwt.encode(
        {"sub": credentials.username},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    
    # 设置cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {"status": "success", "message": "登录成功"}

@app.get("/api/status")
async def get_status(username: str = Depends(verify_auth)) -> Dict[str, Any]:
    """
    获取监控状态API
    
    返回:
        Dict: 包含运行状态和配置信息的字典
    """
    global monitor_task
    return {
        "running": monitor_task is not None and not monitor_task.done(),
        "config": {
            "smtp_server": SMTP_SERVER,
            "smtp_port": SMTP_PORT,
            "email_from": EMAIL_FROM,
            "email_to": EMAIL_TO,
            "interval": MONITORING_INTERVAL
        }
    }

@app.post("/api/start")
async def start_monitoring(username: str = Depends(verify_auth)):
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
async def stop_monitoring(username: str = Depends(verify_auth)):
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
async def index(request: Request, username: str = Depends(verify_auth)):
    """
    主页路由
    
    功能:
    - 显示监控系统的Web界面
    - 提供当前监控状态
    - 显示系统配置信息
    
    参数:
        request: FastAPI请求对象
        username: 通过认证的用户名
    
    返回:
        HTMLResponse: 渲染后的HTML页面
    """
    global monitor_task
    status = {
        'running': monitor_task is not None and not monitor_task.done(),
        'config': {
            'smtp_server': SMTP_SERVER,
            'smtp_port': SMTP_PORT,
            'email_from': EMAIL_FROM,
            'email_to': EMAIL_TO,
            'interval': MONITORING_INTERVAL
        }
    }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "status": status,
            "initial_status": status,
            "username": username
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
