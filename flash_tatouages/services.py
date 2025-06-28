from bson import ObjectId
from database import db
from flash_tatouages.models import *
from datetime import datetime

flash_tatouages_collection = db.flash_tatouages
artistes_collection = db.artistes  # Adjust this to match your actual collection name
shops_collection = db.shops        # Adjust this to match your actual collection name

def get_artiste_by_id(artiste_id: str):
    artiste = artistes_collection.find_one({"_id": ObjectId(artiste_id)})
    if artiste:
        artiste["id"] = str(artiste["_id"])
        del artiste["_id"]
    return artiste

def get_shop_by_id(shop_id: str):
    shop = shops_collection.find_one({"_id": ObjectId(shop_id)})
    if shop:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
    return shop

def flash_tatouages_helper(flash_tatouages) -> dict:
    return {
        "id": str(flash_tatouages["_id"]),
        "image": flash_tatouages["image"],
        "type": flash_tatouages.get("type"),
        "artiste": get_artiste_by_id(flash_tatouages["artiste"]) if flash_tatouages.get("artiste") else None,
        "shop": get_shop_by_id(flash_tatouages["shop"]) if flash_tatouages.get("shop") else None
    }

def create_flash_tatouages(flash_tatouages: flash_tatouages):
    flash_tatouages_dict = flash_tatouages.dict()
    result = flash_tatouages_collection.insert_one(flash_tatouages_dict)
    new_flash_tatouages = flash_tatouages_collection.find_one({"_id": result.inserted_id})
    return flash_tatouages_helper(new_flash_tatouages)

def get_flash_tatouagess():
    flash_tatouagess = []
    for flash_tatouages in flash_tatouages_collection.find():
        flash_tatouagess.append(flash_tatouages_helper(flash_tatouages))
    return flash_tatouagess

def get_flash_tatouages(id: str):
    flash_tatouages = flash_tatouages_collection.find_one({"_id": ObjectId(id)})
    if flash_tatouages:
        return flash_tatouages_helper(flash_tatouages)

def get_flash_tatouages_by_type(type: str):
    results = flash_tatouages_collection.find({"type": type})
    return [flash_tatouages_helper(item) for item in results]

def update_flash_tatouages(id: str, data: dict):
    if len(data) < 1:
        return False
    flash_tatouages = flash_tatouages_collection.find_one({"_id": ObjectId(id)})
    if flash_tatouages:
        updated_flash_tatouages = flash_tatouages_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_flash_tatouages.modified_count > 0:
            new_data = flash_tatouages_collection.find_one({"_id": ObjectId(id)})
            return flash_tatouages_helper(new_data)
    return False

def delete_flash_tatouages(id: str):
    result = flash_tatouages_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
