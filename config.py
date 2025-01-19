"""
Configuration file for the LP API client.
Contains all constants used in the API requests.
"""

import uuid

# API Configuration
API_URL = "https://api2.lptiyu.com/v3/api.php"
ENDPOINTS = {
    "quick_login": "/Login/quickLoginV339",
}

# Sign Algorithm Configuration
SIGN_KEY = "rDJiNB9j7vD2"

# AES Encryption Configuration
RESP_KEY = "Wet2C8d34f62ndi3"
RESP_IV = "K6iv85jBD8jgf32D"

# Device Constants
DEVICE_CONSTANTS = {
    "mobileDeviceId": "ffffffff-ebde-a8ec-ffff-ffffef05ac4a",
    "mobileModel": "ONEPLUS_A6010",
    "mobileOsVersion": "11",
    "ostype": "1",
    "version": "204",
    "version_name": "4.0.4",
    "token": "2195851A813A80A0E576D5E622719CFD",
    "uid": "1",
}

# Default Headers
DEFAULT_HEADERS = {
    "Connection": "close",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ONEPLUS A6010 Build/RKQ1.201217.002)",
    "Host": "api2.lptiyu.com",
    "Accept-Encoding": "gzip"
}

# Login Constants
LOGIN_CONSTANTS = {
    "accesstoken": "5DDBAECA9CF132C4D976B1763D391C45",
    "avatar_url": "http://thirdqq.qlogo.cn/ek_qqapp/AQKSicLsdcXrOW4734eWeduicIfnXm6BXJ7zbWVk6yzqxDpzLSICj3kSUhQBacf4v7eUicqiaeiaCjGq5iaxNOKCKVovdOaqSstwSRcgiauxu50TamR7XMqHpyARnibWnoRqSA/100",
    "nick_name": "123456789",
    "openid": "7669442B2937B6D79C48778F249688AA",
    "school_id": "0",
    "type": "2"
}

# LPN7 Generation Constants
LPN_DEVICE_MODEL = "ONEPLUS_A6010"  # Used for generating lpn7 parameter
