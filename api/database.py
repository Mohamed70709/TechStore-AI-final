from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["techstore"]

products_collection = db["products"]
orders_collection = db["orders"]
customers_collection = db["customers"]
messages_collection = db["messages"]
support_tickets_collection = db["support_tickets"]