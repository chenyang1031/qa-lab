# Day 12 · 并发实战:超卖与幂等的完整闭环

## 复现(红)
探针脚本自动把商品 3 库存削到 1,5 线程并发各抢 1 件:
**5 笔全部 200、5 个不同订单号**——1 件库存卖出 5 单。
更隐蔽:最终库存显示 0"看起来正常",实际是 5 个线程各自回写过期内存值(丢失更新/last-write-wins),**超卖 4 件且账实不符**。

## 根因
- 缺陷①:查库存 → if 判断 → 扣减 三步分离,无锁;sleep(0.2) 放大竞态窗口
- 缺陷②:无幂等键,重复提交 = 多笔订单

## 修复
- 超卖:改单条原子 `UPDATE ... WHERE stock >= quantity`,判定写进 WHERE,数据库行锁保证唯一胜者(sleep 保留,证明原子性由 DB 保证)
- 幂等:`X-Idempotency-Key` 请求头 + orders 表 idempotency_key 唯一索引;同键重复请求返回原订单(响应带 idempotent_replay: true)
- 迁移:ALTER TABLE 加列+唯一索引(**注意:create_all 不会改已有表,存量库必须跑迁移**)

## 回归(绿)
并发探针:恰好 1 笔成功、4 笔 400、库存归 0;全量 **14 passed**。

## 环境差异教训
- WSL 里裸敲 python 会命中 Windows 的 Python 桩(/mnt/c/Windows/System32/python)——零输出假象
- 规矩:跑脚本前先 source .venv/bin/activate,或用 python3
