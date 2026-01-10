from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import logging # <--- Added

# Setup logging for database events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

DB_USER = os.getenv("DB_USER", "todo_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "todo_pass")
DB_HOST = os.getenv("DB_HOST", "mysql")      
DB_NAME = os.getenv("DB_NAME", "todo_db")
DB_PORT = os.getenv("DB_PORT", "3306")       

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Log the connection attempt (helps debug in Grafana)
logger.info(f"Connecting to database at {DB_HOST}:{DB_PORT}")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise e
