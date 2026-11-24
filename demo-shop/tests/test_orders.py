"""订单模块:核心业务断言 + 反向用例。
test_order_stock_decrease 是整个套件的灵魂:接口测试最高的价值就是
"验证业务规则真的生效",而不是只看状态码。"""
import requests


def test_order_without_token(base_url):
    """不带 token 下单 → 403(HTTPBearer 拦截)"""
    r = requests.post(
        f"{base_url}/orders",
        json={"product_id": 1, "quantity": 1},
    )
    assert r.status_code == 403


def test_order_quantity_zero(auth_headers, base_url):
    """quantity=0 → 422(schemas 的 gt=0 安检)"""
    r = requests.post(
        f"{base_url}/orders",
        headers=auth_headers,
        json={"product_id": 1, "quantity": 0},
    )
    assert r.status_code == 422


def test_order_stock_decrease(auth_headers, base_url):
    """核心业务断言:下单前列表库存 N,下单成功后列表库存 = N-1"""
    before = requests.get(f"{base_url}/products").json()[0]["stock"]
    r = requests.post(
        f"{base_url}/orders",
        headers=auth_headers,
        json={"product_id": 1, "quantity": 1},
    )
    assert r.status_code == 200
    after = requests.get(f"{base_url}/products").json()[0]["stock"]
    assert after == before - 1, f"库存应减 1:下单前 {before},下单后 {after}"


def test_order_insufficient_stock(auth_headers, base_url):
    """单线程下的超卖防御:库存不足 → 400,报错文案含'库存不足'"""
    r = requests.post(
        f"{base_url}/orders",
        headers=auth_headers,
        json={"product_id": 1, "quantity": 99999},
    )
    assert r.status_code == 400
    assert "库存不足" in r.json()["detail"]


def test_order_detail_consistency(auth_headers, base_url):
    """下单后查单:order_no 一致、quantity 一致(数据一致性断言)"""
    create = requests.post(
        f"{base_url}/orders",
        headers=auth_headers,
        json={"product_id": 2, "quantity": 3},
    )
    assert create.status_code == 200
    order_no = create.json()["order_no"]

    detail = requests.get(f"{base_url}/orders/{order_no}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["order_no"] == order_no
    assert body["quantity"] == 3
    assert body["product_id"] == 2
