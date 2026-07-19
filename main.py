from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_
from database.session import engine, get_session
from models.book import Book, BookCreate, BookUpdate

app = FastAPI(title="Book Inventory API", version="1.0.0")

# Note: If you aren't using Alembic right away, this line will auto-create tables on startup
@app.on_event("startup")
def on_startup():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, session: Session = Depends(get_session)):
    # Check if ISBN already exists
    existing_book = session.exec(select(Book).where(Book.isbn == book_data.isbn)).first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A book with this ISBN already exists."
        )
    
    db_book = Book.model_validate(book_data)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books", response_model=List[Book])
def list_books(
    author: Optional[str] = None,
    available: Optional[bool] = None,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    statement = select(Book)
    if author:
        statement = statement.where(Book.author == author)
    if available is not None:
        statement = statement.where(Book.available == available)
        
    books = session.exec(statement.offset(offset).limit(limit)).all()
    return books


@app.get("/books/search", response_model=List[Book])
def search_books(
    q: str = Query(..., min_length=1, description="Search keyword for title or author"),
    session: Session = Depends(get_session)
):
    # Case-insensitive partial match search using ILIKE
    statement = select(Book).where(
        or_(
            Book.title.ilike(f"%{q}%"),
            Book.author.ilike(f"%{q}%")
        )
    )
    books = session.exec(statement).all()
    return books


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_data: BookUpdate, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    # Extract explicitly passed fields
    update_dict = book_data.model_dump(exclude_unset=True)
    
    # If updating ISBN, ensure it doesn't conflict with another book
    if "isbn" in update_dict and update_dict["isbn"] != db_book.isbn:
        isbn_conflict = session.exec(select(Book).where(Book.isbn == update_dict["isbn"])).first()
        if isbn_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="A book with this ISBN already exists."
            )

    for key, value in update_dict.items():
        setattr(db_book, key, value)
        
    db_book.updated_at = datetime.utcnow()
    
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    session.delete(book)
    session.commit()
    return None