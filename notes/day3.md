# Day 3 · MongoDB 动手 + Nginx 502 亲手复现

> 当天目标:Mongo 建立文档型数据库认知;Nginx 实验——亲手"杀"出一个 502 并从日志找到证据。

## Part 1 · MongoDB(mongo7 容器)

### 实验

```javascript
use testdb                                                        // 库和集合"用到才建",没有先建表一说
db.hardwares.insertOne({device:"sign-pad-01", temp:26, tags:["签批板","国产化"], reportTime: new Date()})
db.hardwares.insertOne({device:"sign-pad-02", temp:30, battery:88, note:"新固件多了电量字段"})
db.hardwares.insertOne({temp:99})                                 // 残缺数据,照样成功!
db.hardwares.find()                                               // 三条都在,字段各不相同
db.hardwares.find({device:"sign-pad-01"})                         // 条件查询 ≈ SELECT WHERE
new Date()                                                        // 比手表慢 8 小时
```

### 三个结论(批改后定稿)

1. **字段不同的文档能共存**,根因:Mongo 是文档型数据库、没有固定 schema(不是"它不校验"这么浅)——适合存格式多变的数据:硬件上报、日志、语音转写文本
2. **数据库不兜底数据质量** → 测试要主动设计脏数据用例:空值、超长字符串、类型错误、缺必填字段,验证程序层拦截 + 库里落没落脏数据 + 页面表现
3. **Mongo 存的是 UTC 世界标准时间,不是"服务器时间"**(服务器放在哪个时区都不影响)。"我上午 10 点操作、记录显示凌晨 2 点"类 bug,先查 UTC→北京的转换

## Part 2 · Nginx 502 亲手复现(当天主菜)

### 环境

```bash
docker network create lab
docker run -d --name backend --network lab nginx:alpine                # 假装后端
docker run -d --name nginx-front --network lab -p 8080:80 \
  -v ~/qa-lab/sandbox/nginx-proxy.conf:/etc/nginx/conf.d/default.conf nginx:alpine   # 前台
```

配置核心:

```nginx
proxy_pass http://backend:80;    # backend 是容器名 —— Docker 内置 DNS 直接解析(K8s 服务发现雏形)
```

### 因果链(批改后)

```
curl localhost:8080(本机映射端口,不是容器内的 80)
  → nginx-front 接住
  → 转发给 backend
  → docker stop backend(精确命令;stop 温和停止,kill 强杀,是两个命令)
  → curl 再次请求 → 502 Bad Gateway
```

### 证据

```bash
docker logs nginx-front
# connect() failed (111: Connection refused) while connecting to upstream, upstream: "http://...backend:80/"
```

报错白纸黑字写着 upstream 是谁、错在哪——**先拿证据,再下结论**。

### 复活

```bash
docker start backend
curl http://localhost:8080     # 直接恢复 200,nginx-front 没有重启
```

原因:nginx 每收到一个请求才临时连一次后端,连不上才当场报 502——**无状态、不记仇**。后端复活后下一个请求自动恢复。

### 批改记录

- curl 的是 **8080**(本机映射端口),不是容器内的 80
- 排查 502 的第一步是**看 Nginx 日志拿 upstream 证据**,再去看那台后端——不是直接猜"后端挂了"

## 面试可用

- **502 vs 504**:502 = 后端挂了/连不上;504 = 后端活着但处理超时。先探后端存活,再查超时配置
- 页面报 502 → 前台(nginx)大概率没问题,第一动作看它的日志里 upstream 指向谁
