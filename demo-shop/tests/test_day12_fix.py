"""Day 12 修复回归:幂等修复验证 + 并发不超卖验证。
跑之前先执行 bash sandbox/reset_stocks.sh 重置库存。"""

import threading
import time

import requests


def test_idempotent_same_key(auth_headers, base_url):
    """同 key 两次下单 → 同一订单号 + 第二次是幂等重放,库存只扣一次"""
    key = f"idem-{int(time.time() * 1000)}"
    h = {**auth_headers, "X-Idempotency-Key": key}

    r1 = requests.post(f"{base_url}/orders", headers=h, json={"product_id": 2, "quantity": 1})
    r2 = requests.post(f"{base_url}/orders", headers=h, json={"product_id": 2, "quantity": 1})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["order_no"] == r2.json()["order_no"], "同 key 应返回同一订单"
    assert r2.json()["idempotent_replay"] is True


def test_concurrent_no_oversell(auth_headers, base_url):
    """并发回归:5 线程抢最后 1 件 → 恰好 1 笔成功,库存归 0,不为负"""
    H = dict(auth_headers)
    stock = requests.get(f"{base_url}/products").json()[2]["stock"]
    if stock > 1:
        r = requests.post(
            f"{base_url}/orders",
            headers=H,
            json={"product_id": 3, "quantity": stock - 1},
        )
        assert r.status_code == 200, f"削库存失败:{r.text}"

    results = []

    def buy():
        results.append(
            requests.post(f"{base_url}/orders", headers=H, json={"product_id": 3, "quantity": 1})
        )

    threads = [threading.Thread(target=buy) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = [r for r in results if r.status_code == 200]
    final = requests.get(f"{base_url}/products").json()[2]["stock"]
    assert len(success) == 1, f"并发下应有且仅有 1 笔成功,实际 {len(success)} 笔"
    assert final == 0, f"库存应恰好归 0,实际 {final}"
