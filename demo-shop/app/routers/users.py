"""用户接口层:只做"接请求 → 调用下层 → 返回响应",不写业务细节。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import hash_password, create_token
from app.core.database import get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn, TokenOut

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"id": user.id, "username": user.username}


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if user is None or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenOut(access_token=create_token(user.username))
