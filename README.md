# MongoDb Training

Training material for MongoDb Cross-Team Training Day

## Prerequisites

- [Python 3.8 or higher](https://www.python.org/downloads/release/python-380/)
- [Pipenv](https://pipenv.pypa.io/en/latest/)

## Installation

Use `pipenv` to install the necessary dependencies.

```shell
$ pipenv install --dev
```

Start the `pipenv` shell with the following command

```shell
$ pipenv shell
```

## Env File

Create a `.env` in the root of the repository with the following value

```
export MONGODB_URI=mongodb+srv://<username:<password>@<your-cluster>.mongodb.net/myTestDatabase?retryWrites=true&w=majority
```

## Data Modelling

The `data_modelling` directory contains the code for the data-modelling lesson. To run the application
use the following command

```shell
$ uvicorn data_modelling.main:app --reload
```

This repo contains a [Postman](https://www.postman.com/downloads/) collection for testing the API called `Book API.postman_collection.json`.
This file can be imported into the Postman application.

### Exercise 1

The update endpoint allows `tags` to be updated. Right now it will overwrite the existing tags.
Update the `update_book` function to add new tags without over-writing the old.

### Exercise 2

We want to know more information about the author. Convert the author property to a nested document including
the following fields using a Pydantic model

- bio - a text field where some information about the author can be stored
- rating - a numerical field where users can rate the author with 1 - 10 stars in increments of 0.5
- first_name - the author's first name
- last_name - the author's last name

Note: When updating a book, the author information should not be over-written.

### Exercise 3

We want to add chapters to the book with a chapter title. Use a Pydantic model with the following fields and add the
chapter to the Book entity.

- chapter_title - a text field of the chapter title. (i.e. Foreword, 1, Index)
- synopsis - a text field with a summary of the chapter in a few sentences.
- pages - the number of pages in the chapter

## Transactions

MongoDb 4.x supports ACID compliant transactions. To use transactions you will need to use the session object
in a with-statement. [Documentation](https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html#transactions)

The `transactions` directory contains the code for the transactions lesson. To run the application
use the following command

```shell
$ uvicorn transactions.main:app --reload
```

This repo contains a [Postman](https://www.postman.com/downloads/) collection for testing the API called `Webshop API.postman_collection.json`.
This file can be imported into the Postman application.

### Exercise 1

The customer has two properties which need to be updated and saved back to the `customers` collection. Add an appropriate
update statement.

Use the data below to insert a new customer and a new order.

#### Example Data

Sample Customer Document

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "mobile_mobile": "0611111111",
  "email_address": "john@email.com",
  "total_purchased": 0,
  "total_orders": 0
}
```

Sample Order Document

```json
{
  "customer_id": "<insert customer id>",
  "items": [
    {
      "sku": "1111",
      "qty": 1,
      "price": 5.25
    },
    {
      "sku": "2222",
      "qty": 2,
      "price": 11.5
    }
  ],
  "total": 0
}
```

### Bonus Exercise

Implement a stock keeping collection which will keep the quantity of a given sku.
When an item is sold the stock quantity should be decreased when a new order is created.

Sample Stock Document

```json
{
  "sku": "1111",
  "qty": 100
}
```
