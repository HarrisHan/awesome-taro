import requests
import urllib3
import time
import random
import hashlib
import json
import logging
from acw获取 import get_acw
from 请求解密 import LPDecryptor
from config import (
    DEVICE_CONSTANTS,
    SIGN_KEY,
    LOGIN_CONSTANTS,
    DEFAULT_HEADERS,
    API_URL,
    ENDPOINTS,
    LPN_DEVICE_MODEL
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    level=logging.INFO,
)

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_lpn7(timestamp):
    """Generate lpn7 parameter based on timestamp.
    
    Args:
        timestamp (str): Current timestamp string
        
    Returns:
        tuple: (param_key, param_value) for lpn7 parameter
    """
    j2 = LPN_DEVICE_MODEL
    j3 = str(timestamp)
    
    param_key = "lp" + j2[1:2].lower() + j3[3:4]  # e.g. "lpn7"
    param_value = hashlib.md5(str(int(j3) * 2).encode('utf-8')).hexdigest()
    
    return param_key, param_value

def signed_params(extra_params=None):
    """Generate signed parameters for API requests.
    
    Args:
        extra_params (dict, optional): Additional parameters to include
        
    Returns:
        dict: Parameters with timestamp, nonce, lpn7 and sign
    """
    ret = DEVICE_CONSTANTS.copy()
    timestamp = str(int(time.time()))
    ret["timestamp"] = timestamp
    ret["nonce"] = str(random.randint(100000, 999999))
    
    lpn_key, lpn_value = generate_lpn7(timestamp)
    ret[lpn_key] = lpn_value
    
    if extra_params:
        ret.update(extra_params)
        
    str2sign = "".join(
        map(
            lambda x: str(x[0]) + str(x[1]),
            sorted(ret.items(), key=lambda x: x[0])
        )
    ) + SIGN_KEY
    
    ret["sign"] = hashlib.md5(str2sign.encode()).hexdigest()
    return ret

def generate_login_data():
    """Generate login request parameters with proper signing.
    
    Returns:
        dict: Signed parameters for login request
    """
    return signed_params(LOGIN_CONSTANTS)

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
    
    # 生成登录数据并加密
    login_data = generate_login_data()
    logging.info("登录数据: %s", login_data)
    # 使用 LPDecryptor 加密数据
    encryptor = LPDecryptor()
    json_str = json.dumps(login_data, ensure_ascii=False, separators=(',', ':'))
    encrypted_key = encryptor.encrypt_params(json_str)
    
    # 请求URL和数据
    url = API_URL + ENDPOINTS["quick_login"]
    data = {"key": encrypted_key}
    
    # 构建headers
    headers = DEFAULT_HEADERS.copy()
    headers["Cookie"] = cookie_str
    headers["Content-Length"] = str(len(encrypted_key))
    
    # 显示请求信息
    logging.info("发送的请求信息:")
    logging.info("POST %s HTTP/1.1", ENDPOINTS['quick_login'])
    logging.info("Cookie: %s", cookie_str)
    for key, value in headers.items():
        if key != "Cookie":
            logging.info("%s: %s", key, value)
    logging.info("key=%s", encrypted_key)
    
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