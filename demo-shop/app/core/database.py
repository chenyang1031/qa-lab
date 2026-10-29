"""数据库连接层:SQLAlchemy 的引擎与 会话 工厂。
get_db 是 FastAPI 的依赖:每个请求进来发一个连接,请求结束自动归还。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# pymysql 是 Python 连 MySQL 的驱动;utf8mb4 支持中文和 emoji
engine = create_engine(
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()   # 所有 ORM 模型的基类


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
