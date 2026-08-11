from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, or_, SQLModel

from database.session import engine, get_session
from models.book import Book, BookCreate, BookUpdate


# Modern FastAPI Lifespan handler replacing deprecated @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Database initialization warning (skipping table creation): {e}")
    yield


app = FastAPI(
    title="Book Inventory API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", response_class=HTMLResponse)
async def portfolio():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Student Portfolio - Backend Assignments</title>
    <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }
    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
    .student-info { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
    .student-info strong { color: #2c3e50; }
    .admission { font-size: 1.2em; color: #2980b9; font-weight: bold; }
    .assignment { margin: 12px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; transition: all 0.3s ease; }
    .assignment:hover { background: #e8f4fd; transform: translateX(5px); }
    .assignment a { color: #0366d6; text-decoration: none; font-weight: 500; display: flex; align-items: center; }
    .assignment a:hover { text-decoration: underline; }
    .badge { display: inline-block; background: #3498db; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; }
    .lesson-topic { color: #7f8c8d; font-size: 0.9em; margin-left: 10px; }
    .footer { margin-top: 30px; text-align: center; color: #95a5a6; font-size: 0.9em; border-top: 1px solid #ecf0f1; padding-top: 20px; }
    </style>
    </head>
    <body>
    <div class="container">
    <h1>📚 Backend Development Portfolio</h1>

    <div class="student-info">
    <p>👨‍🎓 <strong>Student Name:</strong> DAVID ROSASI</p>
    <p>🎓 <strong>Admission Number:</strong> <span class="admission">C027-01-0922/2024</span></p>
    <p>📧 <strong>Email:</strong> nyambega.david24@students.dkut.ac.ke</p>
    </div>

    <h2>📝 Backend Assignments</h2>
    <p style="color: #7f8c8d; margin-bottom: 20px;">Click on any assignment to view the complete code on GitHub</p>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/fastapi-lab1" target="_blank">
    <span class="badge">Lesson 1,2,3</span>
    <span>HTTP & Your First API</span>
    <span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/gighub-api" target="_blank">
    <span class="badge">Lesson 4</span>
    <span>Docker - Packaging Your API</span>
    <span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/techvault-api" target="_blank">
    <span class="badge">Lesson 5</span>
    <span>Routing, Parameters & Request Bodies</span>
    <span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/library-api" target="_blank">
    <span class="badge">Lesson 6</span>
    <span>Error Handling & Validation</span>
    <span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/bookstore-api" target="_blank">
    <span class="badge">Lesson 7,11</span>
    <span>User Authentication – JWT & Password Hashing</span>
    <span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/clinicguard-api" target="_blank">
    <span class="badge">Lesson 8</span>
    <span>Authorization & Rate Limiting</span>
    <span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/sendit-api" target="_blank">
    <span class="badge">Lesson 9</span>
    <span>File Uploads & External APIs</span>
    <span class="lesson-topic">— File Validation, httpx, Environment Variables</span>
    </a>
    </div>

    <div class="assignment">
    <a href="https://github.com/david-rosasi051/product-api" target="_blank">
    <span class="badge">Lesson 10</span>
    <span>Testing & Deployment (Cloud)</span>
    <span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span>
    </a>
    </div>

    <div class="footer">
    <p>📍 Deployed on Render | 📅 Last Updated: August 2026</p>
    <p style="font-size: 0.8em;">⚠️ Click on any assignment link to view the complete source code on GitHub</p>
    </div>
    </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, session: Session = Depends(get_session)):
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
    
    update_dict = book_data.model_dump(exclude_unset=True)
    
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