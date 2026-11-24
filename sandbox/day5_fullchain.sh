#!/bin/bash
BASE=http://127.0.0.1:8001
U="day5_$(date +%s)"
echo "== 1. 注册 $U =="
curl -s -X POST $BASE/users/register -H "Content-Type: application/json" \
  -d "{\"username\":\"$U\",\"password\":\"test123456\"}"; echo
echo "== 2. 登录提取 token =="
TOKEN=$(curl -s -X POST $BASE/users/login -H "Content-Type: application/json" \
  -d "{\"username\":\"$U\",\"password\":\"test123456\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "TOKEN=${TOKEN:0:20}..."
echo "== 3. 连下三单(幂等观察) =="
for i in 1 2 3; do
  echo "--- 第 ${i} 单 ---"
  curl -s -X POST $BASE/orders -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" -d '{"product_id":1,"quantity":1}'; echo
done
echo "== 4. 最终库存 =="
curl -s $BASE/products; echo
