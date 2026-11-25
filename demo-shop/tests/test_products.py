"""商品模块接口测试:列表与详情(含缓存标志)"""
import requests


def test_list_products(base_url):
    """列表返回 3 个种子商品,库存非负"""
    r = requests.get(f"{base_url}/products")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert all(p["stock"] >= 0 for p in data)


def test_product_detail_has_cache_flag(base_url):
    """详情响应带 from_cache 字段(无论 true/false,字段必须在)"""
    r = requests.get(f"{base_url}/products/2")
    assert r.status_code == 200
    assert "from_cache" in r.json()
def test_product_not_found(base_url):
    """查不存在的商品 → 404"""
    r = requests.get(f"{base_url}/products/999")
    assert r.status_code == 500
    assert "商品不存在" in r.json()["detail"]