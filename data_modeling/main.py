import os
from typing import List, Any

from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.database import Database

from data_modelling.library import ObjectIdField, DomainException, to_objectid_str

load_dotenv()

app = FastAPI(
    title="Books API", version="1.0.0", description="A book repository using MongoDb"
)


@app.exception_handler(DomainException)
def handle_invalid_usage(response, error):
    return JSONResponse(error.to_dict(), status_code=error.status_code)


def get_db():
    client = MongoClient(host=os.getenv("MONGODB_URI"))
    return client.test_database


class NotFound(DomainException):
    code = "NOT_FOUND"
    status_code = 404


class BookBase(BaseModel):
    name: str
    # Exercise 2 - Refactor to a nested document using Pydantic
    author: str
    isbn: str
    pages: int
    # Exercise 3 - add chapters documents. Hint: List[Chapters]
    chapters: Any
    tags: List[str] = Field(default=[])


class BookAdd(BookBase):
    pass


class BookUpdate(BaseModel):
    name: str
    tags: List[str] = Field(default=[])


class BookGet(BookBase):
    class Config:
        json_encoders = {
            ObjectId: to_objectid_str,
        }

    id: ObjectIdField = Field(alias='_id')


@app.get("/")
async def index():
    return {"application": "Book API"}


@app.post("/books/", status_code=204)
async def add_book(book: BookAdd, db: Database = Depends(get_db)):
    db.books.insert_one(book.dict())
    return Response(status_code=204)


@app.put("/books/{id}", status_code=204)
async def update_book(
    id: ObjectIdField, book: BookUpdate, db: Database = Depends(get_db)
):
    # Exercise 1 - the new tags should be added to the list/array without overriding the existing
    db.books.update_one({"_id": id}, {"$set": book.dict()})
    return Response(status_code=204)


@app.delete("/books/{id}", status_code=204)
async def delete_book(id: ObjectIdField, db: Database = Depends(get_db)):
    db.books.delete_one({"_id": id})
    return Response(status_code=204)


@app.get("/books/", response_model=List[BookGet])
async def get_books(db: Database = Depends(get_db)):
    books = db.books.find({})
    return [BookGet(**book) for book in books]


@app.get("/books/{id}", response_model=BookGet)
async def get_book(id: ObjectIdField, db: Database = Depends(get_db)):
    book = db.books.find_one(id)
    if book:
        return BookGet(**book)
    raise NotFound(f"Book by id {id!r} not found!")
