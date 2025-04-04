import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from book_management import Base



class GenreEnum(enum.Enum):  # ?
    FICTION = "Fiction"
    NON_FICTION = "Non-Fiction"
    SCIENCE = "Science"
    HISTORY = "History"


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    genre = Column(Enum(GenreEnum), nullable=False)
    published_year = Column(Integer, nullable=False)

    author = relationship("Author", back_populates="books")
