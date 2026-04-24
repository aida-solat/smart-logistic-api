from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Use the database URL from the settings to create the database engine
DATABASE_URL = settings.DATABASE_URL

# Create an SQLAlchemy engine to interact with the database
engine = create_engine(DATABASE_URL)

# Configure session maker for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency to provide a database session.

    Yields:
        Session: An active database session.
    """
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Provide the session for the request lifecycle
    finally:
        db.close()  # Ensure the session is closed after use
