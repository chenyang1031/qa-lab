# Day 8 · demo 商城容器化

## Dockerfile 四要点
1. `FROM python:3.11-slim`:slim 版镜像小很多,够用
2. 先 `COPY requirements.txt` 装依赖、再 `COPY . .`:**分层缓存**——改代码重建镜像时跳过 pip install(秒级)
3. `--host 0.0.0.0`:容器里必须监听所有网卡,写 127.0.0.1 宿主机永远映射不到(经典坑)
4. `EXPOSE 8000` 只是声明,真正生效的是 compose 的 ports

## compose 三服务
- db(mysql:8,3307:3306,**volume db-data 持久化**)+ healthcheck(MySQL 首启 40 秒,app 等它 healthy 才启动)
- redis(redis:7,6379)
- app(8001:8000,环境变量 DB_HOST=db / DB_PORT=3306 / REDIS_URL=redis://redis:6379/0)

## 六个日常命令
up -d / ps / logs app / restart app / down(删容器留数据)/ down -v(连卷删=数据清零,慎用)

## 验收
compose 拉起后跑 day5_fullchain.sh 全链路通过;down 后 up,数据还在(volume 的价值)
