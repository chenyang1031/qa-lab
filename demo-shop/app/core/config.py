"""配置层:所有可变参数(连接信息、密钥)集中在这,支持环境变量覆盖。
容器化时(第 2-3 周)只需要改环境变量,不改代码。"""

import os


class Settings:
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")          # 本地跑=127.0.0.1,进容器后=host.docker.internal
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root123")
    DB_NAME = os.getenv("DB_NAME", "demo_shop")

    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

    JWT_SECRET = os.getenv("JWT_SECRET", "qa-demo-secret")
    JWT_EXPIRE_MINUTES = 30                               # token 30 分钟过期


settings = Settings()
