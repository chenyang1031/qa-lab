"""订单接口层:新增 X-Idempotency-Key 请求头透传。"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import Order
from app.schemas import OrderIn, OrderOut
from app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["订单"])


@router.post("", response_model=OrderOut)
def create_order_api(
    data: OrderIn,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
):
    return create_order(db, username, data.product_id, data.quantity, idempotency_key)


@router.get("/{order_no}")
def order_detail(
    order_no: str,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {
        "order_no": order.order_no,
        "username": order.username,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "created_at": str(order.created_at),
    }
