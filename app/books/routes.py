from fastapi import FastAPI, Header, status, APIRouter
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from typing import Optional, List
import os

from app.books.book_data import books
from app.books.schemas import BookCreateModel, BookUpdateModel, Book

book_router = APIRouter()


@book_router.post('/create_book')
async def create_book(book_data: BookCreateModel):
    return {
        "title": book_data.title,
        "author": book_data.author
    }

@book_router.get("/greet/{name}")
async def greet(name: str) -> dict:
    app_name = os.getenv("APP_NAME")
    return {"message": f"Hello, {name}! {app_name}"}

@book_router.get("/greet_two") 
async def greet_two(name: str) -> dict:
    return {"message": f"Hello, {name}!"}

@book_router.get("/greet_two2/{name}") 
async def greet_two2(name: str, age: int = 0) -> dict:
    return {"message": f"Hello, {name}! Votre âge est {age}."}

@book_router.get("/greet_two3") 
async def greet_two3(name: Optional[str] = "User", age: int = 0) -> dict:
    return {"message": f"Hello, {name}! Votre âge est {age}."}

@book_router.get("/get_headers", status_code=201)
async def get_headers(
    accept:str = Header(None),
    user_agent:str = Header(None),
    content_type:str = Header(None),
    host:str = Header(None),
):
    request_headers = {}
    request_headers["accept"] = accept
    request_headers["user_agent"] = user_agent
    request_headers["content_type"] = content_type
    request_headers["host"] = host
    return request_headers


@book_router.get("/", response_model=List[Book])
async def get_books():
    return books    

@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data:Book)->dict:
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book

@book_router.get("/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.patch("/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update_data: BookUpdateModel):
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update_data.title
            book["publisher"] = book_update_data.publisher
            book["page_count"] = book_update_data.page_count
            book["language"] = book_update_data.language
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Book not found"
    )

@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted successfully"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Book not found"
    )
