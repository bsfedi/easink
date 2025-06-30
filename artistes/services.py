from bson import ObjectId
from database import db
from artistes.models import *

artiste_collection = db.artistes
artiste_collection = db.artistes
flashs_collection = db.flash_tatouages
shops_collection = db.shops
tatouages_collection = db.tatouages  # Make sure this matches your real collection name



def get_flashs_by_ids(ids):
    return [
        {
            "id": str(f["_id"]),
            "image": f["image"],
            "type": f.get("type"),
           "prix": f.get("prix"),
             "tags": f.get("tags", []),
                "description": f.get("description")
        }
        for f in flashs_collection.find({"_id": {"$in": [ObjectId(i) for i in ids]}})
    ]

def get_shops_by_ids(ids):
    return [
        {
            "id": str(s["_id"]),
                "images": s.get("images", []),
            "name": s["name"],
            "ville": s.get("city"),
            "lat": s.get("lat"),
            "lng": s.get("lng")
        }
        for s in shops_collection.find({"_id": {"$in": [ObjectId(i) for i in ids]}})
    ]

def get_tatouages_by_ids(ids):
    print(ids)
    tatouages_map = {
        str(t["_id"]): {
            "id": str(t["_id"]),
               "prix": t.get("prix"),
            "image": t.get("image"),
            "type": t.get("type"),
            "tags": t.get("tags", []),
            "description": t.get("description")
        }
        for t in flashs_collection.find({"_id": {"$in": [ObjectId(i) for i in ids]}})
    }

    return [tatouages_map.get(i) for i in ids if tatouages_map.get(i)]


from datetime import datetime

def format_next_availability(next_avail_raw):
    try:
        # 🧠 Vérifie si c'est déjà un objet datetime (comme retourné par PyMongo parfois)
        if isinstance(next_avail_raw, datetime):
            next_avail = next_avail_raw
        # 📦 Sinon, c'est probablement un dictionnaire avec "$date"
        elif isinstance(next_avail_raw, dict) and "$date" in next_avail_raw:
            date_str = next_avail_raw["$date"].split('.')[0]
            next_avail = datetime.fromisoformat(date_str.replace("Z", ""))
        else:
            return "Non renseignée"

        today = datetime.today().date()
        avail_date = next_avail.date()
        delta = (avail_date - today).days

        if delta == 0:
            return "Aujourd'hui"
        elif delta == 1:
            return "Demain"
        elif 2 <= delta <= 6 and avail_date.isocalendar()[1] == today.isocalendar()[1]:
            return "Cette semaine"
        elif avail_date.month == today.month and avail_date.year == today.year:
            return "Ce mois"
        else:
            return "Le mois prochain"
    except Exception as e:
        print("Erreur parsing next_availability:", e)
        return "Non renseignée"



def artiste_helper(artiste) -> dict:
    # flashs = get_flashs_by_ids(artiste.get("flashs", [])) if artiste.get("flashs") else []
    shops = get_shops_by_ids(artiste.get("shops", [])) if artiste.get("shops") else []
    tatouages = get_tatouages_by_ids(artiste.get("tatouages", [])) if artiste.get("tatouages") else []

    formatted_availability = format_next_availability(artiste.get("next_availability"))


    return {
        "id": str(artiste["_id"]),
        "name": artiste["name"],
        "shops": shops[0],
        "tatouages": tatouages,
        "rate": artiste.get("rate"),
        "description": artiste.get("description"),
        "informations": artiste.get("informations"),
        # "avis": artiste.get("avis"),
        "avatar": artiste.get("avatar"),
        "questions": artiste.get("questions"),
        "sub_tags": artiste.get("sub_tags"),
        # "flashs": flashs,
        "tags": artiste.get("tags"),
        "next_availability": formatted_availability,
    }


def artiste_helper_by_id(artiste) -> dict:
    flashs = get_flashs_by_ids(artiste.get("flashs", [])) if artiste.get("flashs") else []
    shops = get_shops_by_ids(artiste.get("shops", [])) if artiste.get("shops") else []
    tatouages = get_tatouages_by_ids(artiste.get("tatouages", [])) if artiste.get("tatouages") else []

    formatted_availability = format_next_availability(artiste.get("next_availability"))


    return {
        "id": str(artiste["_id"]),
        "name": artiste["name"],
        "shops": shops[0],
        "tatouages": tatouages,
        "rate": artiste.get("rate"),
        "description": artiste.get("description"),
        "informations": artiste.get("informations"),
        "avis": artiste.get("avis"),
        "avatar": artiste.get("avatar"),
        "questions": artiste.get("questions"),
        "sub_tags": artiste.get("sub_tags"),
        "flashs": flashs,
        "tags": artiste.get("tags"),
        "next_availability": formatted_availability,
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
        return artiste_helper_by_id(artiste)


def get_artistes_by_category():
    # Fetch artists by category
    nouveaux = artiste_collection.find({"category": "nouveaux"})
    coups_coeur = artiste_collection.find({"category": "coups_coeur"})
    populaires = artiste_collection.find({"category": "populaires"})

    # Helper to format all artists in a cursor
    def format_artistes(cursor):
        return [artiste_helper(a) for a in cursor]

    # Fetch 5 flashs and 5 tatouages from db.flash_tatouages
    flashs = db.flash_tatouages.find({"type": "flash"}).limit(5)
    tatouages = db.flash_tatouages.find({"type": "tatouage"}).limit(5)

    # Format flashs and tatouages (assuming you need only selected fields or convert ObjectId)
    def format_flash_tatouage(item):
        return {
            "id": str(item["_id"]),
            "type": item["type"],
            "image": item.get("image"),
            "name": item.get("name"),  # Assuming you have a name field
            "artiste": get_artiste(item["artiste"]) if item.get("artiste") else None,            # Add more fields if needed, like "image", "description", etc.
        }

    return {
        "nouveaux": format_artistes(nouveaux),
        "coups_coeur": format_artistes(coups_coeur),
        "populaires": format_artistes(populaires),
        "flashs": [format_flash_tatouage(f) for f in flashs],
        "tatouages": [format_flash_tatouage(t) for t in tatouages],
    }


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

