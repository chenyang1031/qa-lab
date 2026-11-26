"""并发超卖验证探针(Day 12)
用法: python concurrent_order_test.py [base_url]
流程: 自动把商品 3 库存削到 1 → 5 线程并发各抢 1 件 → 统计成功笔数与最终库存
判定: 恰好 1 笔成功且库存归 0 = 正确;多笔成功或库存为负 = 超卖缺陷复现
"""
import sys
import time
import threading

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
PID = 3

# 1. 注册测试账号并登录
u = f"conc_{int(time.time())}"
requests.post(f"{BASE}/users/register", json={"username": u, "password": "test123456"})
tok = requests.post(
    f"{BASE}/users/login", json={"username": u, "password": "test123456"}
).json()["access_token"]
H = {"Authorization": f"Bearer {tok}"}

# 2. 把库存削到只剩 1 件(制造"最后一件"场景)
stock = requests.get(f"{BASE}/products").json()[PID - 1]["stock"]
print(f"商品 {PID} 当前库存:{stock}")
if stock > 1:
    r = requests.post(f"{BASE}/orders", headers=H, json={"product_id": PID, "quantity": stock - 1})
    assert r.status_code == 200, f"削库存失败:{r.text}"
print("库存已削到 1,发车:5 个线程同时抢最后 1 件!\n")

# 3. 五线程并发抢购
results = []

def buy(i):
    r = requests.post(f"{BASE}/orders", headers=H, json={"product_id": PID, "quantity": 1})
    try:
        body = r.json()
    except Exception:
        body = {}
    results.append((i, r.status_code, body.get("order_no", "-"), body.get("remaining_stock", "-")))

threads = [threading.Thread(target=buy, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 4. 统计与判定
final = requests.get(f"{BASE}/products").json()[PID - 1]["stock"]
success = [r for r in results if r[1] == 200]

for i, code, order_no, remain in sorted(results):
    print(f"线程{i}: 状态码={code} 订单={order_no} 剩余库存={remain}")

print(f"\n成功 {len(success)} 笔 | 最终库存 {final}")
if len(success) > 1 or final < 0:
    print("❌ 超卖缺陷复现:多笔成功/库存异常 —— 查库存与扣库存之间存在竞态窗口")
elif len(success) == 1 and final == 0:
    print("✅ 验证通过:恰好 1 笔成功、库存归 0 —— 并发安全")
else:
    print("⚠️ 异常状态,需人工检查")
