"""数据库连接层:SQLAlchemy 的引擎与 会话 工厂。
get_db 是 FastAPI 的依赖:每个请求进来发一个连接,请求结束自动归还。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# pymysql 是 Python 连 MySQL 的驱动;utf8mb4 支持中文和 emoji
# pool_pre_ping:取连接前探活,死连接自动换新(修复 MySQL 重启后首个请求 500)
# pool_size/max_overflow:连接池扩容(默认 5+10,压测下排队严重,扩到 20+30)
engine = create_engine(
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4",
    pool_pre_ping=True,
    pool_size=20,        # 默认 5
    max_overflow=30,     # 默认 10
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()   # 所有 ORM 模型的基类


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
