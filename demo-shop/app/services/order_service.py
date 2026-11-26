"""业务逻辑层:下单流程。

Day 12 修复记录(并发实战):
- 缺陷① 超卖:查库存→判断→扣减 三步分离,并发下全部通过检查再各自回写旧值(丢失更新)
  修复:改为单条原子 UPDATE,判定条件写进 WHERE,由数据库行锁保证只有一个请求成功
- 缺陷② 不幂等:无幂等键,重复提交 = 多笔订单
  修复:支持 X-Idempotency-Key,同键重复请求直接返回原订单(库存只减一次)
- 保留 time.sleep(0.2):证明原子性由数据库保证,应用层慢一点也不怕
"""


import time
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Product, Order


def create_order(db, username, product_id, quantity, idempotency_key=None):
    """缺陷②修复:幂等键命中 → 直接返回原订单,不产生新订单、不扣库存"""
    if idempotency_key:
        existing = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
        if existing:
            product = db.get(Product, existing.product_id)
            return {
                "order_no": existing.order_no,
                "username": existing.username,
                "product_id": existing.product_id,
                "quantity": existing.quantity,
                "remaining_stock": product.stock if product else None,
                "idempotent_replay": True,
            }

    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 缺陷①修复:原子扣减——条件写进 WHERE,判定与扣减在数据库内一次完成
    updated = (
        db.query(Product)
        .filter(Product.id == product_id, Product.stock >= quantity)
        .update({Product.stock: Product.stock - quantity}, synchronize_session=False)
    )
    if updated == 0:
        raise HTTPException(status_code=400, detail=f"库存不足,剩余 {product.stock}")

    time.sleep(0.2)  # 保留:修复后即使有应用层延迟也不会超卖

    order = Order(
        order_no="ORD" + datetime.now().strftime("%Y%m%d%H%M%S%f"),
        username=username,
        product_id=product_id,
        quantity=quantity,
        idempotency_key=idempotency_key,
    )
    db.add(order)
    db.commit()

    product = db.get(Product, product_id)  # 提交后读真实库存
    return {
        "order_no": order.order_no,
        "username": username,
        "product_id": product_id,
        "quantity": quantity,
        "remaining_stock": product.stock,
        "idempotent_replay": False,
    }
