"""模型层:Order 新增 idempotency_key(唯一索引,允许多个 NULL)。"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)     # 单位:分
    stock = Column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    idempotency_key = Column(String(80), unique=True, nullable=True)
