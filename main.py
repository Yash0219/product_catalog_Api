from fastapi import FastAPI,Depends , HTTPException
from sqlalchemy.orm import Session
from database import engine , Base ,get_db
import models
import schemas
from typing import List

app = FastAPI(title="product_catalog_api")

#Command SQLAlchemy to physically build all registered tables inside catalog.db
Base.metadata.create_all(bind = engine)

@app.get("/")
def get_root():
    return{"status":"online",
           "message":"welcome!"}
    
@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    # check if category already exists in the database
    existing_category = db.query(models.Category).filter(models.Category.name == category.name).first()

    if existing_category:
        raise HTTPException(status_code=409, detail="Category already exists")

    # Translate incoming Pydantic schema data into a concrete SQLAlchemy ORM object row
    new_category = models.Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@app.get("/categories/",response_model=List[schemas.CategoryResponse])
def read_all_categories(db:Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.get("/categories/{category_id}/", response_model=schemas.CategoryResponse)
def read_category(category_id:int , db:Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="category not found")
    return category
        

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user:schemas.UserCreate, db:Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400 , detail="user already exist")
    
    new_user = models.User(username = user.username,email = user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Fetch every registered user
@app.get("/users/", response_model=List[schemas.UserResponse])
def read_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

#Fetch a specific user by their unique ID
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/products/",response_model=schemas.ProductResponse)
def create_product(product:schemas.ProductCreate,db:Session = Depends(get_db)):
    # DUPLICATE GUARD: Block products with duplicate names
    existing_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product name already exists")

    # RELATIONAL GUARD: Make sure the target category exists 
    category_exists = db.query(models.Category).filter(models.Category.id == product.category_id).first()
    if not category_exists:
        raise HTTPException(status_code=400, detail="Target category_id does not exist")
 
    #define the new product orm object
    new_product = models.Product(name=product.name,
                                 price = product.price,
                                 description = product.description,
                                 category_id = product.category_id)
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@app.get("/products/",response_model=List[schemas.ProductResponse])
def read_all_products(db:Session = Depends(get_db)):
    return db.query(models.Product).all()   

@app.get("/products/{product_id}/",response_model=schemas.ProductDetailResponse)
def get_product(product_id:int , db:Session = Depends(get_db)):
    product= db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return product

@app.post("/reviews/", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Relational Integrity: Does the product exist?
    product_exists = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if not product_exists:
        raise HTTPException(status_code=400, detail="Target product_id does not exist")

    # Relational Integrity: Does the user exist?
    user_exists = db.query(models.User).filter(models.User.id == review.user_id).first()
    if not user_exists:
        raise HTTPException(status_code=400, detail="Target user_id does not exist")

    # Instantiate the Review ORM object row
    new_review = models.Review(
        rating=review.rating,
        comment=review.comment,
        product_id=review.product_id,
        user_id=review.user_id
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# delete category with no active products
@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # Fetch the target row from disk
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Check if any products are actively linked to this category
    # with help of relationship handshake, we can check 'category.products' directly!
    if category.products:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete category. It contains active products. Empty the category first."
        )
        
    db.delete(category) 
    db.commit()         
    
    return {"status": "success", "message": f"Category {category_id} deleted successfully."}

#  Remove a user who has no active history
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Safety Firewall: Block deletion if this user has written active reviews
    if user.reviews:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete user with active product reviews. Clear or delete their reviews first."
        )
        
    db.delete(user)
    db.commit()
    return {"status": "success", "message": f"User {user_id} deleted successfully."}

# Remove a product from the inventory
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Block deletion if customers have already reviewed this item
    if product.reviews:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete product with active customer reviews. Delete associated reviews first."
        )
        
    db.delete(product)
    db.commit()
    return {"status": "success", "message": f"Product {product_id} deleted successfully."}