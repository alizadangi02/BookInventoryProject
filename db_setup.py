from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey

DATABASE_URL = "postgresql+psycopg2://postgres:aesthetic0@localhost:5432/book_inventory"

Base = declarative_base()

# Author Table
class Author(Base):
    __tablename__ = "author"
    author_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)

    books = relationship("Book", back_populates="author", cascade="all, delete")

# Book Table
class Book(Base):
    __tablename__ = "book"
    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    author_id = Column(Integer, ForeignKey("author.author_id"))

    author = relationship("Author", back_populates="books")

# Create tables
if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
