from functools import reduce
import os
from typing import List, Any

from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.database import Database

from data_modeling.library import ObjectIdField, DomainException, to_objectid_str

load_dotenv()

app = FastAPI(
    title="Webshop API",
    version="1.0.0",
    description="A webshop API written on top of MongoDb",
)


@app.exception_handler(DomainException)
def handle_invalid_usage(response, error):
    return JSONResponse(error.to_dict(), status_code=error.status_code)


def get_db():
    client = MongoClient(host=os.getenv("MONGODB_URI"))
    return client.test_database


def get_client():
    return MongoClient(host=os.getenv("MONGODB_URI"))


class NotFound(DomainException):
    code = "NOT_FOUND"
    status_code = 404


# Orders


class OrderItem(BaseModel):
    sku: str
    qty: int
    price: float


class OrderBase(BaseModel):
    customer_id: ObjectIdField
    total: float = Field(default=0)
    items: List[OrderItem]


class OrderAdd(OrderBase):
    pass


class OrderGet(OrderBase):
    class Config:
        json_encoders = {
            ObjectId: to_objectid_str,
        }

    id: ObjectIdField = Field(alias='_id')


class OrderAddResult(BaseModel):
    class Config:
        json_encoders = {
            ObjectId: to_objectid_str,
        }

    id: ObjectIdField


@app.get("/")
async def index():
    return {"application": "Webshop API"}


def order_total(items: List[OrderItem]):
    total = 0
    for item in items:
        total = total + (item.qty * item.price)
    return total


@app.post("/orders/", status_code=201, response_model=OrderAddResult, tags=["Orders"])
async def add_order(order: OrderAdd, client: MongoClient = Depends(get_client)):
    customers = client.test_database.customers
    orders = client.test_database.orders

    customer = customers.find_one(order.customer_id)

    if not customer:
        raise NotFound(f"Customer {order.customer_id} not found!")
    customer = CustomerBase(**customer)

    with client.start_session() as session:
        with session.start_transaction():
            total = order_total(order.items)
            customer.total_orders = customer.total_orders + 1
            customer.total_purchased = customer.total_purchased + total

            # Exercise 1 - make sure the customer document is updated
            # TODO Update Customer

            # Insert order
            order.total = total
            result = orders.insert_one(order.dict())
    return OrderAddResult(id=result.inserted_id)


@app.delete("/orders/{id}", status_code=204, tags=["Orders"])
async def delete_order(id: ObjectIdField, db: Database = Depends(get_db)):
    db.orders.delete_one({"_id": id})
    return Response(status_code=204)


@app.get("/orders/", response_model=List[OrderGet], tags=["Orders"])
async def get_orders(db: Database = Depends(get_db)):
    orders = db.orders.find({})
    return [OrderGet(**order) for order in orders]


@app.get("/orders/{id}", response_model=OrderGet, tags=["Orders"])
async def get_order(id: ObjectIdField, db: Database = Depends(get_db)):
    order = db.orders.find_one(id)
    if order:
        return OrderGet(**order)
    raise NotFound(f"Order by id {id!r} not found!")


# Customers


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    mobile_mobile: str
    email_address: str
    total_purchased: float = Field(default=0)
    total_orders: int = Field(default=0)


class CustomerAdd(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerGet(CustomerBase):
    class Config:
        json_encoders = {
            ObjectId: to_objectid_str,
        }

    id: ObjectIdField = Field(alias='_id')


class CustomerAddResult(BaseModel):
    class Config:
        json_encoders = {
            ObjectId: to_objectid_str,
        }

    id: ObjectIdField


@app.post(
    "/customers/", status_code=201, response_model=CustomerAddResult, tags=["Customers"]
)
async def add_customer(customer: CustomerAdd, db: Database = Depends(get_db)):
    result = db.customers.insert_one(customer.dict())
    return CustomerAddResult(id=result.inserted_id)


@app.put("/customers/{id}", status_code=204, tags=["Customers"])
async def update_customer(
    id: ObjectIdField, customer: CustomerUpdate, db: Database = Depends(get_db)
):
    db.customers.update_one({"_id": id}, {"$set": customer.dict()})
    return Response(status_code=204)


@app.get("/customers/", response_model=List[CustomerGet], tags=["Customers"])
async def get_customers(db: Database = Depends(get_db)):
    customers = db.customers.find({})
    return [CustomerGet(**customer) for customer in customers]
