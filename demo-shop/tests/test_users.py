"""用户模块接口测试:注册/登录的正反用例"""
import time

import requests


def test_register_success(base_url):
    """正向:唯一用户名注册成功,响应带回用户名"""
    username = f"reg_{int(time.time() * 1000)}"
    r = requests.post(
        f"{base_url}/users/register",
        json={"username": username, "password": "test123456"},
    )
    assert r.status_code == 200
    assert r.json()["username"] == username


def test_register_duplicate(base_url):
    """反向:重复用户名 → 400(唯一约束)。
    先注册一次(无论成败),第二次必然撞唯一约束 → 400"""
    requests.post(
        f"{base_url}/users/register",
        json={"username": "dup_tester", "password": "test123456"},
    )
    r = requests.post(
        f"{base_url}/users/register",
        json={"username": "dup_tester", "password": "test123456"},
    )
    assert r.status_code == 400


def test_register_bad_username(base_url):
    """反向:用户名只有 1 个字符 → 422(schemas 安检)"""
    r = requests.post(
        f"{base_url}/users/register",
        json={"username": "a", "password": "test123456"},
    )
    assert r.status_code == 422


def test_login_wrong_password(base_url):
    """反向:密码错误 → 401"""
    r = requests.post(
        f"{base_url}/users/login",
        json={"username": "day5tester", "password": "wrong-password"},
    )
    assert r.status_code == 401
