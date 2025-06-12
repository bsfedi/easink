from pymongo import MongoClient
from pymongo.database import Database
from config import Settings


setting =Settings()

host =setting.HOST
database=  setting.DATABASE
user = setting.USER
password = setting.PASSWORD
port= setting.PORT
# Database connection details
db_params = {
    'host': host,
    'database': database,
    'user': user,
    'password': password,
    'port':port
}


db : Database = MongoClient("mongodb+srv://fedislimen98:jnEr6hM6wYS6EixZ@easink.pkrz0.mongodb.net/")["easink"]