from bson import ObjectId
from database import db
from artistes.models import *

artiste_collection = db.artistes

def artiste_helper(artiste) -> dict:
    return {
        "id": str(artiste["_id"]),
        "name": artiste["name"],
        "studio": artiste["studio"],
        "ville": artiste.get("ville"),
        "rate": artiste.get("rate"),
        "images": artiste.get("images"),
        "next_availability": artiste.get("next_availability"),
    }

def create_artiste(artiste: Artiste):
    artiste_dict = artiste.dict()
    result =  artiste_collection.insert_one(artiste_dict)
    new_artiste =  artiste_collection.find_one({"_id": result.inserted_id})
    return artiste_helper(new_artiste)

def get_artistes():
    artistes = []
    for artiste in artiste_collection.find():
        artistes.append(artiste_helper(artiste))
    return artistes

def get_artiste(id: str):
    artiste =  artiste_collection.find_one({"_id": ObjectId(id)})
    if artiste:
        return artiste_helper(artiste)

def update_artiste(id: str, data: dict):
    if len(data) < 1:
        return False
    artiste =  artiste_collection.find_one({"_id": ObjectId(id)})
    if artiste:
        updated_artiste =  artiste_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_artiste.modified_count > 0:
            new_data =  artiste_collection.find_one({"_id": ObjectId(id)})
            return artiste_helper(new_data)
    return False

def delete_artiste(id: str):
    result =  artiste_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
