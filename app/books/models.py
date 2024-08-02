from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.auth.models import Base

book_author = Table(
    "book_author",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("author_id", Integer, ForeignKey("author.id")),
)

book_category = Table(
    "book_category",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)

user_unavailable_book_category = Table(
    "user_unavailable_book_category",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)


class AuthorModel(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    books = relationship("BookModel", secondary=book_author, back_populates="authors")

    def __str__(self):
        return f" Author {self.name}"


class CategoryModel(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    books = relationship(
        "BookModel", secondary=book_category, back_populates="categories"
    )
    users = relationship(
        "UserModel",
        secondary=user_unavailable_book_category,
        back_populates="unavailable_book_categories",
    )

    def __str__(self):
        return f" Category {self.name}"


class BookModel(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    language = Column(String, index=True)
    publication_date = Column(String, index=True)
    isbn = Column(String, index=True)

    authors = relationship(
        "AuthorModel", secondary=book_author, back_populates="books", lazy="selectin"
    )
    categories = relationship(
        "CategoryModel",
        secondary=book_category,
        back_populates="books",
        lazy="selectin",
    )

    def __str__(self):
        return f" Book {self.title}"
