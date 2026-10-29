# Day 4 · demo 下单服务跑通(2026-10-29)

> 说明:表格里的数字是今天跑出来的记录,如有出入以自己实际看到的为准。

## 一、今天搭起来的环境

- 被测服务:qa-lab demo 商城(FastAPI + MySQL 8 + Redis),代码在 `~/qa-lab/demo-shop`
- 启动方式:`DB_PORT=3307 uvicorn app.main:app --reload --port 8001`
- 依赖容器:mysql8(端口映射 3307→3306)、redis7(6379)
- 启动成功标志:日志出现「种子数据已写入:3 个商品,库存各 100」

## 二、环境排障实战(今天踩的 4 个坑)

1. **mysql8 起不来**:`ports are not available` → 本机 Windows 装了 MySQL(`mysqld.exe`)占着 3306。排查:`netstat -ano | grep 3306` 找 PID → `tasklist` 查进程名 → 解决:换 `-p 3307:3306`
2. **8000 端口被占**:旧容器 api_automation_test 占用 → 服务改用 8001
3. **venv 创建失败**:`ensurepip is not available` → `sudo apt install python3.10-venv` 后删掉半成品重建
4. **配置层的价值**:数据库端口变了,一行代码没改——`DB_PORT=3307` 环境变量覆盖了 config.py 里的默认值。第 3 周容器化时用的就是同一招

## 三、/docs 全链路测试记录

| 步骤 | 接口 | 关键入参 | 状态码 | 观察与结论 |
|---|---|---|---|---|
| 注册 | POST /users/register | chenyang / test123456 | 200 | 返回 id=1 |
| 重复注册 | 同上 | 同上 | 400 | 用户名已存在——唯一约束在起作用 |
| 坏参数注册 | 同上 | username 只有 1 个字符 | **422** | schemas.py 的 `Field(min_length=3)` 拦截,响应里写明哪个字段违规——参数校验层先于业务层生效 |
| 登录 | POST /users/login | 同上 | 200 | 返回 access_token(JWT,30 分钟过期) |
| 商品列表 | GET /products | 无 | 200 | 3 个商品,stock 全是 100 |
| 首次下单 | POST /orders | product_id=1, quantity=2 | 200 | `remaining_stock: 98`,返回 order_no |
| 再次下单 | 同上 | 同上 | 200 | `remaining_stock: 96`——**连下两单扣两份,不幂等实锤**(缺陷②) |
| 详情查两次 | GET /products/1 | 无 | 200 | 第一次 `from_cache: false`,第二次 `true`——缓存命中 |
| 下单后立刻查详情 | GET /products/1 | 无 | 200 | **库存还是旧值**(60 秒缓存未失效,缺陷③);同一时刻查列表 /products 却是新值 |

补充:order_no 形如 `ORD2026102915xxxxxx`(时间戳生成);token 过期后再调接口会得到 401。

## 四、今天理解的一个请求的旅程(v1)

浏览器 /docs → routers 路由接住请求 → schemas 参数校验(不过 → 422)→ auth 校验 token(不过 → 401)→ services 业务逻辑 → models/ORM → MySQL;商品详情接口顺路查 Redis 缓存(命中就不碰数据库)。

## 五、服务的三个故意缺陷(后续测试的靶子,代码里有 ⚠️ 注释)

1. **下单不幂等**:重复提交 = 多笔订单、多扣库存 → 第 12 周幂等测试对象
2. **并发可超卖**:查库存与扣库存之间无锁,且有 0.2 秒延迟放大窗口 → 第 12 周并发测试对象
3. **商品详情缓存 60 秒不主动失效**:下单扣库存后详情页显示旧库存 → 缓存一致性素材

## 六、待办

- [ ] Day 5:curl 全链路,学会 `Authorization: Bearer <token>` 请求头;同一订单连发 3 次做幂等观察
- [ ] 加测一个:不带 token 直接 POST /orders,看返回什么(FastAPI 的 HTTPBearer 默认返回 403)
