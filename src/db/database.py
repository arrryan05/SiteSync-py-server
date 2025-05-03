# from sqlmodel import create_engine, SQLModel
# from sqlalchemy.orm import sessionmaker
# import os

# DATABASE_URL = os.getenv("DATABASE_URL")  # loaded by python-dotenv in main.py

# # For simple sync usage:
# engine = create_engine(DATABASE_URL, echo=True)

# # SessionLocal factory
# SessionLocal = sessionmaker(
#     bind=engine, autoflush=False, autocommit=False, class_=SQLModel, expire_on_commit=False
# )

# def init_db():
#     SQLModel.metadata.create_all(engine)

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import create_engine, Session

import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False, connect_args={})

def get_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise

