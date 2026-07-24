from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# category schema
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# user schema
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


# product schema
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class ProductCreate(ProductBase):
    category_id: int  # must specify which category the product belongs to


class ProductResponse(ProductBase):
    id: int
    category_id: int
    model_config = ConfigDict(from_attributes=True)


# review schema
class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    user_id: int
    product_id: int


# what API returns when viewing the review
class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    model_config = ConfigDict(from_attributes=True)


# When you want to see a product WITH its category and ALL its reviews nested inside
class ProductDetailResponse(ProductResponse):
    category: CategoryResponse
    review: ReviewResponse