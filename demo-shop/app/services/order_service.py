"""业务逻辑层:下单流程。★★ 这个文件是第 11-12 周"高并发专项测试"的靶子 ★★
里面故意留了两个缺陷,看到不要修:
  缺陷① 查库存和扣库存是两步,中间没有加锁 → 并发下会超卖
  缺陷② 没有任何幂等控制 → 同一用户重复提交 = 多笔订单、多扣库存
"""

import time
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Product, Order


def create_order(db: Session, username: str, product_id: int, quantity: int) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 缺陷①:check(下面这行)和扣减(再下面)之间没有锁,并发请求会同时通过检查
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail=f"库存不足,剩余 {product.stock}")

    time.sleep(0.2)   # 故意放慢 0.2 秒,第 12 周并发压测时用来放大超卖窗口

    product.stock -= quantity          # 扣库存
    order = Order(
        order_no="ORD" + datetime.now().strftime("%Y%m%d%H%M%S%f"),
        username=username,
        product_id=product_id,
        quantity=quantity,
    )
    db.add(order)
    db.commit()

    # 缺陷②:没有幂等键,调用两次 = 两笔订单、扣两次库存(Day 5 会亲眼观察这个现象)
    return {
        "order_no": order.order_no,
        "username": username,
        "product_id": product_id,
        "quantity": quantity,
        "remaining_stock": product.stock,
    }
