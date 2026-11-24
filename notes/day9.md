# Day 9 · 接口自动化测试套件(2026-11-24)

## 套件结构

| 文件 | 用例数 | 内容 |
|---|---|---|
| conftest.py | — | 公共夹具:base_url + auth_headers(session 级,全套只登录一次) |
| test_users.py | 4 | 注册 200 / 重复 400 / 坏参数 422 / 密码错 401 |
| test_products.py | 3 | 列表 / 缓存标志 / 404(这条是我手写的) |
| test_orders.py | 5 | 无 token 403 / quantity=0 422 / 库存递减业务断言 / 库存不足 400 / 查单一致性 |

总计 **12 条用例**,全绿,2 秒跑完。

## fixture 一句话

session 级 `auth_headers` = 整套测试只登录一次,token 装进 Authorization 头供全部用例共用。

## 断言的三种境界

1. **状态码**断言(404/403/422/401)
2. **字段一致性**断言(order_no 一致、from_cache 字段存在)
3. **业务规则**断言(下单后库存 = 下单前 - 1)——最有价值的一层

## 我手写的用例

test_product_not_found(GET /products/999 → 404)——我自己的第一条手写自动化用例。

## 遗留问题

- 暂无
