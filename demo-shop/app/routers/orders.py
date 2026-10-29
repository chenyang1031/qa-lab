"""订单接口层:下单与查单。真正的业务在 services/order_service.py 里。"""

from fastapi import APIRouter, Depends, HTTPException
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
    username: str = Depends(get_current_user),        # 不带有效 token 就到不了这里(401)
    db: Session = Depends(get_db),
):
    return create_order(db, username, data.product_id, data.quantity)


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
