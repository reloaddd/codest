from app.config import settings
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

# thus engine manages connection pool to our database
engine = create_engine(settings.database_url)

#create a local, short lived and sindle database session

localSession=sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base=declarative_base()

def get_db():
    db=localSession()
    try:
        yield db
    finally:
        db.close




