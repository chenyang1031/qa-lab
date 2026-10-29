"""服务入口:装配路由、建表、灌种子数据。
启动命令(在 demo-shop 目录下):
    uvicorn app.main:app --reload --port 8000
然后浏览器打开 http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine, SessionLocal, Base
from app.models import Product        # noqa: F401  必须导入,模型才会注册进 Base
from app.routers import users, products, orders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-shop")

SEED_PRODUCTS = [                     # 种子数据:3 个商品,库存各 100
    {"name": "测试原型机", "price": 99900, "stock": 100},
    {"name": "签批板 Pro", "price": 59900, "stock": 100},
    {"name": "语音质检盒子", "price": 199900, "stock": 100},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)              # 建表(已存在则跳过)
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            for item in SEED_PRODUCTS:
                db.add(Product(**item))
            db.commit()
            log.info("种子数据已写入:3 个商品,库存各 100")
    finally:
        db.close()
    yield


app = FastAPI(
    title="qa-lab demo 商城",
    description="教学用被测服务:故意带 3 个缺陷——下单不幂等、并发可超卖、商品详情缓存 60 秒不失效",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/", tags=["健康检查"])
def root():
    return {"service": "qa-lab demo shop", "docs": "/docs"}
