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

# Device Constants - Use environment variables for sensitive data
DEVICE_CONSTANTS = {
    "mobileDeviceId": "${MOBILE_DEVICE_ID}",  # Set via environment
    "mobileModel": "${MOBILE_MODEL}",         # Set via environment
    "mobileOsVersion": "${OS_VERSION}",       # Set via environment
    "ostype": "1",
    "version": "204",
    "version_name": "4.0.4",
    "uid": "1"
}

# Default Headers
DEFAULT_HEADERS = {
    "Connection": "close",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "User-Agent": "${USER_AGENT}",  # Set via environment
    "Host": "${API_HOST}",          # Set via environment
    "Accept-Encoding": "gzip"
}

# Login Constants - Use environment variables for sensitive data
LOGIN_CONSTANTS = {
    "school_id": "-1",
    "type": "2"
}

# LPN7 Generation Constants
LPN_DEVICE_MODEL = "ONEPLUS_A6010"  # Used for generating lpn7 parameter
