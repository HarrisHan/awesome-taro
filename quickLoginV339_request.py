import os
import requests
import urllib3
import time
import random
import hashlib
import logging
from acw_utils import get_acw
from config import (
    SIGN_KEY,
    DEFAULT_HEADERS,
    API_URL
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    level=logging.INFO,
)

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def simulate_login():
    # 获取cookies
    cookies = get_acw()
    if not cookies:
        logging.error("获取cookies失败！")
        return
    
    # 构建Cookie字符串
    cookie_str = f"acw_tc={cookies.get('acw_tc', '')}; "
    cookie_str += f"aliyungf_tc={cookies.get('aliyungf_tc', '')}; "
    cookie_str += f"PHPSESSID={cookies.get('PHPSESSID', '')}"
    
    # 构造请求参数，使用环境变量
    params = {
        "version": "204",
        "version_name": "4.0.4",
        "mobileModel": os.getenv("MOBILE_MODEL", ""),
        "mobileDeviceId": os.getenv("MOBILE_DEVICE_ID", ""),
        "mobileOsVersion": os.getenv("OS_VERSION", ""),
        "ostype": "1",
        "school_id": "-1",
        "uid": "1",
        "type": "2",
        "nonce": str(random.randint(100000, 999999)),
        "timestamp": str(int(time.time())),
    }
    
    # 计算sign
    str2sign = "".join(
        map(
            lambda x: str(x[0]) + str(x[1]),
            sorted(params.items(), key=lambda x: x[0])
        )
    ) + SIGN_KEY
    params["sign"] = hashlib.md5(str2sign.encode()).hexdigest()
    
    # URL encode parameters
    data = "&".join(f"{k}={v}" for k, v in params.items())
    
    # 请求URL和数据
    url = API_URL + "/System/getIp"
    
    # 构建headers
    headers = DEFAULT_HEADERS.copy()
    headers["Cookie"] = cookie_str
    headers["Content-Length"] = str(len(data))
    
    # 显示请求信息
    logging.info("发送的请求信息:")
    logging.info("POST %s HTTP/1.1", "/System/getIp")
    logging.info("Cookie: %s", cookie_str)
    for key, value in headers.items():
        if key != "Cookie":
            logging.info("%s: %s", key, value)
    logging.info("Request body: %s", data)
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, data=data, verify=False)
        
        # 显示响应信息
        logging.info("收到的响应:")
        logging.info("HTTP/1.1 %d", response.status_code)
        for name, value in response.headers.items():
            logging.info("%s: %s", name, value)
        logging.info("\n%s", response.text)
        
    except Exception as e:
        logging.error("请求发送失败: %s", str(e))

if __name__ == "__main__":
    simulate_login()                                                                                                                                                                        