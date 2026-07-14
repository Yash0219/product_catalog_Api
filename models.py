from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # One User has many reviews. Expects variable name 'user' inside Review class.
    reviews = relationship("Review", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # One Category has many products. Expects variable name 'category' inside Product class.
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    
    #  Points to the categories table name directly
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    #Links to Category class. Expects 'products' variable inside Category.
    category = relationship("Category", back_populates="products")
    #Links to Review class. Expects 'product' variable inside Review.
    reviews = relationship("Review", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False) 
    comment = Column(Text, nullable=True)

    # Pointing to the parent table names directly
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Handshakes pointing back to single parent variables
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    
