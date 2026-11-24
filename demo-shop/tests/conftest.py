"""公共夹具:pytest 自动发现 conftest.py 中的 fixture。
base_url = 被测服务地址
auth_headers = 会话级登录凭证(session 级:整套测试只登录一次,所有需要登录的用例共用)
"""
import time

import pytest
import requests

BASE_URL = "http://127.0.0.1:8001"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_headers(base_url):
    """注册一个本套件专用账号并登录,返回带 Authorization 头的字典"""
    username = f"qa_{int(time.time())}"
    requests.post(
        f"{base_url}/users/register",
        json={"username": username, "password": "test123456"},
    )
    r = requests.post(
        f"{base_url}/users/login",
        json={"username": username, "password": "test123456"},
    )
    assert r.status_code == 200, f"夹具登录失败:{r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
