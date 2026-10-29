"""模型层(ORM):定义三张表。ORM = 用 Python 对象操作数据库,不用手写 SQL。
User ↔ users 表,Product ↔ products 表,Order ↔ orders 表。"""

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
    price = Column(Integer, nullable=False)     # 单位:分。用整数避免 0.1+0.2 浮点误差
    stock = Column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
