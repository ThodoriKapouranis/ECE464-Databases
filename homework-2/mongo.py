from pymongo import MongoClient
from pprint import pprint

client = MongoClient("mongodb+srv://root:123@cluster0.nubhe.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.hw2
