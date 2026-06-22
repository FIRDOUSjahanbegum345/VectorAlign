from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DB_FILE = "vectoralign.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Connect and configure
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define your User model
class User(Base):
    _tablename_ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

def init_db():
    # This creates the tables based on your defined models
    Base.metadata.create_all(bind=engine)
