#!/bin/bash
# 本地跑 pytest 前重置库存(教学环境默认 100,方便回归)
# 用法: bash sandbox/reset_stocks.sh
docker exec demo-shop-db-1 mysql -uroot -proot123 demo_shop \
  -e "UPDATE products SET stock = 100 WHERE id IN (1,2,3);" 2>/dev/null
echo "库存已重置为 100/100/100"
