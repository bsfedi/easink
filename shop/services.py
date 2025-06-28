from bson import ObjectId
from database import db
from shop.models import *

shop_collection = db.shops

def shop_helper(shop) -> dict:
    return {
        "id": str(shop["_id"]),
        "name": shop["name"],
        "lat": shop["lat"],
        "lng": shop.get("lng"),
        "images": shop.get("images")
    }
from datetime import datetime, date

def create_shop(shop: shop):
    shop_dict = shop.dict()
    # Normalize fields to lowercase
    shop_dict["name"] = shop_dict["name"].lower()
    result =  shop_collection.insert_one(shop_dict)
    new_shop =  shop_collection.find_one({"_id": result.inserted_id})
    return shop_helper(new_shop)

def get_shops():
    shops = []
    for shop in shop_collection.find():
        shops.append(shop_helper(shop))
    return shops

def get_shop(id: str):
    shop =  shop_collection.find_one({"_id": ObjectId(id)})
    if shop:
        return shop_helper(shop)

def update_shop(id: str, data: dict):
    if len(data) < 1:
        return False
    shop =  shop_collection.find_one({"_id": ObjectId(id)})
    if shop:
        updated_shop =  shop_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_shop.modified_count > 0:
            new_data =  shop_collection.find_one({"_id": ObjectId(id)})
            return shop_helper(new_data)
    return False

def delete_shop(id: str):
    result =  shop_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0

