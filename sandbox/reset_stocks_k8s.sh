#!/bin/bash
# K8s 环境库存重置(对应 compose 的 reset_stocks.sh)
# 用法: bash sandbox/reset_stocks_k8s.sh
kubectl exec deploy/demo-db -- mysql -uroot -proot123 demo_shop \
  -e "UPDATE products SET stock = 100 WHERE id IN (1,2,3);" 2>/dev/null
echo "K8s 环境库存已重置为 100/100/100"
