from sqlalchemy import Column , Integer , String ,Float, DateTime , ForeignKey
from sqlalchemy.orm import declarative_base , relationship

Base = declarative_base()

class User(Base):
    __tablename__  = "users"
    
    id = Column(Integer,primary_key=True , index= True)
    name = Column(String(100),unique=True, nullable=False)
    email = Column(String , unique=True , nullable=False)
    
    #relationship with review
    review = relationship("review" , back_populates="user")
    
    
class category(Base):
    __tablename__ = "categories"
    
    id = Column()
    name =Column()
    
    #relationship with product
    products = relationship("product", back_populates="category")
    
    
    
class product(Base):
    __tablename__ = "products"
    
    id =Column(Integer , primary_key=True , index=True)
    name =(String, nullable = False)
    price = (Float, nullable = False)
    description = (String , nullable = False)
    
class review(Base):
    __tablename__ = "review"
    
    id = Column(Integer , primary_key=True , index=True)
    rating = Column(Integer , nullable= False)
    comment = Column(String, nullable=False)
    