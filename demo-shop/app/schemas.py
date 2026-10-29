"""入参/出参模型层(Pydantic):声明每个接口收什么、返什么,自动做参数校验。
比如 quantity 定义了 gt=0,传 0 或负数会直接被 FastAPI 挡下返回 422,根本到不了业务层。"""

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
