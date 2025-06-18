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
        "tags":artiste.get("tags"),
        "next_availability": artiste.get("next_availability"),
    }
from datetime import datetime, date

def create_artiste(artiste: Artiste):
    artiste_dict = artiste.dict()
    # Normalize fields to lowercase
    artiste_dict["name"] = artiste_dict["name"].lower()
    if artiste_dict.get("ville"):
        artiste_dict["ville"] = artiste_dict["ville"].lower()
    if artiste_dict.get("tags"):
        artiste_dict["tags"] = [tag.lower() for tag in artiste_dict["tags"]]
        # Convert date to datetime (if needed)
    if isinstance(artiste_dict.get("next_availability"), date) and not isinstance(artiste_dict.get("next_availability"), datetime):
        artiste_dict["next_availability"] = datetime.combine(artiste_dict["next_availability"], datetime.min.time())
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


from datetime import datetime, timedelta

def get_filtered_artistes(name=None, ville=None, next_availability=None, tags=None):
    query = {}

    if name:
        query["name"] = {"$regex": name.lower(), "$options": "i"}

    if ville:
        query["ville"] = ville.lower()

    # Handle date-based filters
    if next_availability and next_availability != "Peu importe":
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if next_availability == "Aujourd'hui":
            tomorrow = today + timedelta(days=1)
            query["next_availability"] = {"$gte": today, "$lt": tomorrow}

        elif next_availability == "Demain":
            start = today + timedelta(days=1)
            end = today + timedelta(days=2)
            query["next_availability"] = {"$gte": start, "$lt": end}

        elif next_availability == "Cette semaine":
            start = today
            end = today + timedelta(days=7)
            query["next_availability"] = {"$gte": start, "$lt": end}

        elif next_availability == "Ce mois":
            start = today
            if today.month == 12:
                end = datetime(today.year + 1, 1, 1)
            else:
                end = datetime(today.year, today.month + 1, 1)
            query["next_availability"] = {"$gte": start, "$lt": end}

    if tags:
        tags_lower = [tag.lower() for tag in tags]
        query["tags"] = {"$in": tags_lower}

    artistes = artiste_collection.find(query)
    return [artiste_helper(art) for art in artistes]

