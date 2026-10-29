"""鉴权层:签发 JWT、校验 JWT。
JWT(令牌)= 登录成功后发给你的"临时工牌",之后每次请求都带着它(HTTP 头 Authorization)。"""

import hashlib
import time

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

bearer = HTTPBearer()   # 声明"这个接口需要 Authorization 头",/docs 里会出现 Authorize 按钮


def hash_password(raw: str) -> str:
    # ⚠️ 教学简化:固定盐 + sha256。生产环境必须用 bcrypt 等慢哈希,这里不展开
    return hashlib.sha256(("qa-demo-salt:" + raw).encode()).hexdigest()


def create_token(username: str) -> str:
    payload = {
        "sub": username,                                   # 工牌上写的"你是谁"
        "exp": int(time.time()) + settings.JWT_EXPIRE_MINUTES * 60,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    """依赖项:每个需要登录的接口带上它,就自动完成 token 校验"""
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token 已过期,请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="token 无效")
    return payload["sub"]                                  # 把用户名交给接口用
