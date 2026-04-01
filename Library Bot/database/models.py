from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Table, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

favorites = Table(
    'favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('book_id', Integer, ForeignKey('books.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    language = Column(String(5), default='en')
    created_at = Column(DateTime, default=datetime.utcnow)

    saved_books = relationship("Book", secondary=favorites, back_populates="favorited_by", lazy='selectin')

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    
    books = relationship("Book", back_populates="category", cascade="all, delete-orphan", lazy='selectin')

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String)
    file_id = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    price = Column(Integer, default=0)
    is_paid = Column(Boolean, default=False)
    
    category = relationship("Category", back_populates="books", lazy='selectin')
    favorited_by = relationship("User", secondary=favorites, back_populates="saved_books")

class Purchase(Base):
    __tablename__ = 'purchases'
    __table_args__ = (UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

class Request(Base):
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    book_name = Column(String, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
