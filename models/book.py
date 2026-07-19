from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import Field as PydanticField

# Current year fallback for validation (2026)
CURRENT_YEAR = 2026

class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str = Field(index=True)
    isbn: str = Field(index=True, unique=True)
    published_year: int = Field(ge=1000, le=CURRENT_YEAR)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    available: bool = Field(default=True)

class Book(BookBase, table=True):
    __tablename__ = "book"
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BookCreate(BookBase):
    pass

class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    published_year: Optional[int] = PydanticField(default=None, ge=1000, le=CURRENT_YEAR)
    price: Optional[float] = PydanticField(default=None, gt=0)
    stock: Optional[int] = PydanticField(default=None, ge=0)
    available: Optional[bool] = None