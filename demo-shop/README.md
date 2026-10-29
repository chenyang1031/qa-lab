# qa-lab demo 商城(被测服务)

教学用电商后端:**FastAPI + MySQL 8 + Redis**,故意带 3 个缺陷,是后续所有测试环节的靶子。

## 目录职责(Day 6 逐层读懂的就是这些)

| 文件 | 职责 |
|---|---|
| app/main.py | 入口:装配路由、建表、灌种子数据 |
| app/core/config.py | 配置层:连接信息/密钥,支持环境变量覆盖 |
| app/core/database.py | 数据库连接层:引擎与每请求连接 |
| app/core/auth.py | 鉴权层:JWT 签发与校验 |
| app/models.py | 模型层:users/products/orders 三张表 |
| app/schemas.py | 入参出参模型:自动参数校验(非法参数直接 422) |
| app/routers/users.py | 注册/登录接口 |
| app/routers/products.py | 商品列表/详情(详情走 Redis 缓存) |
| app/routers/orders.py | 下单/查单接口 |
| app/services/order_service.py | 下单业务:★故意带缺陷★ |

## ⚠️ 故意保留的 3 个缺陷(测试靶子,不要修)

1. **下单不幂等**(order_service.py 末尾):重复提交 = 多笔订单、多扣库存 → 第 12 周幂等测试的对象
2. **并发可超卖**(order_service.py 中部):查库存与扣库存之间无锁,且有 0.2 秒延迟放大窗口 → 第 12 周超卖测试的对象
3. **缓存不主动失效**(products.py):商品详情缓存 60 秒,下单扣库存后详情页最长 60 秒显示旧库存 → 缓存一致性实验素材

## 本地启动(WSL Ubuntu,依赖容器:mysql8 + redis7)

```bash
# 1. 起依赖(如已启动可跳过)
docker run -d --name mysql8 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root123 -e MYSQL_DATABASE=demo_shop mysql:8
docker start redis7
docker logs -f mysql8        # 等到出现 "ready for connections"(Ctrl+C 退出日志)

# 2. 装依赖并启动
cd ~/qa-lab/demo-shop
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. 浏览器打开 http://127.0.0.1:8000/docs
```

## 全链路 curl(第 5 天用)

```bash
# 注册
curl -X POST http://127.0.0.1:8000/users/register -H "Content-Type: application/json" \
  -d '{"username":"chenyang","password":"test123456"}'
# 登录(把返回的 access_token 复制下来)
curl -X POST http://127.0.0.1:8000/users/login -H "Content-Type: application/json" \
  -d '{"username":"chenyang","password":"test123456"}'
# 下单(TOKEN 换成上一步的值)
curl -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" -d '{"product_id":1,"quantity":1}'
# 商品列表(看库存变化)
curl http://127.0.0.1:8000/products
# 商品详情(看 from_cache 是 true 还是 false)
curl http://127.0.0.1:8000/products/1
```
