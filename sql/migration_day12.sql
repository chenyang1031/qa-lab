-- Day 12 迁移:幂等键列 + 唯一索引(数据库层面的最后一道幂等防线)
ALTER TABLE orders
  ADD COLUMN idempotency_key VARCHAR(80) NULL,
  ADD UNIQUE KEY uq_orders_idem (idempotency_key);

-- 库存重置(教学环境:把三个商品恢复到 100,方便回归)
UPDATE products SET stock = 100 WHERE id IN (1, 2, 3);
