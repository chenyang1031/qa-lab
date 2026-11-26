"""入参/出参模型:OrderOut 增加 idempotent_replay 字段(标记幂等重放)。"""

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6, max_length=32)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OrderIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="购买数量,必须大于 0")


class OrderOut(BaseModel):
    order_no: str
    username: str
    product_id: int
    quantity: int
    remaining_stock: int
    idempotent_replay: bool = False
