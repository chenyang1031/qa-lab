"""商品接口层:列表直查 MySQL;详情走 Redis 缓存(60 秒)——用来观察缓存行为。
⚠️ 教学设计:缓存 60 秒且不主动失效。下单扣库存后,详情页最长 60 秒仍显示旧库存,
这是"缓存一致性"的活教材(改了库、页面没变,答案就在这)。"""

import json

import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Product

router = APIRouter(prefix="/products", tags=["商品"])
rds = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("")
def list_products(db: Session = Depends(get_db)):
    rows = db.query(Product).all()
    return [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in rows]


@router.get("/{product_id}")
def product_detail(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"

    cached = rds.get(cache_key)
    if cached:                                        # 缓存命中:不查数据库,直接返回
        return {"from_cache": True, **json.loads(cached)}

    row = db.query(Product).filter(Product.id == product_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    data = {"id": row.id, "name": row.name, "price": row.price, "stock": row.stock}
    rds.set(cache_key, json.dumps(data), ex=60)       # 写缓存,60 秒后自动过期
    return {"from_cache": False, **data}
