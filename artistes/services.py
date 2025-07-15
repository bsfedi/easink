from bson import ObjectId
from database import db
from artistes.models import *

artiste_collection = db.artistes
artiste_collection = db.artistes
flashs_collection = db.flash_tatouages
fav_artiste_collection = db.fav_artistes  # Adjust this to match your actual collection name
shops_collection = db.shops
tatouages_collection = db.tatouages  # Make sure this matches your real collection name


project_collection = db.projects


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
            return "Peu importe"
    except Exception as e:
        print("Erreur parsing next_availability:", e)
        return "Non renseignée"



def artiste_helper(artiste) -> dict:
    shops = get_shops_by_ids(artiste.get("shops", [])) if artiste.get("shops") else []
    tatouages = get_tatouages_by_ids(artiste.get("tatouages", [])) if artiste.get("tatouages") else []
    formatted_availability = format_next_availability(artiste.get("next_availability"))

    avis = artiste.get("avis", [])
    
    # Calcul de la moyenne des notes
    if avis:
        total_notes = sum(item.get("avis", 0) for item in avis)
        moyenne = round(total_notes / len(avis), 2)
    else:
        moyenne = None  # ou 0 selon ton besoin

    return {
        "id": str(artiste["_id"]),
        "name": artiste["name"],
        "shops": shops[0] if shops else None,
        "tatouages": tatouages,
        "rate": moyenne,
        "description": artiste.get("description"),
        "informations": artiste.get("informations"),
        "avatar": artiste.get("avatar"),
        "questions": artiste.get("questions"),
        "sub_tags": artiste.get("sub_tags"),
        "tags": artiste.get("tags"),
        "next_availability": formatted_availability,
    }



def artiste_helper_by_id(artiste) -> dict:
    flashs = get_flashs_by_ids(artiste.get("flashs", [])) if artiste.get("flashs") else []
    shops = get_shops_by_ids(artiste.get("shops", [])) if artiste.get("shops") else []
    tatouages = get_tatouages_by_ids(artiste.get("tatouages", [])) if artiste.get("tatouages") else []

    formatted_availability = format_next_availability(artiste.get("next_availability"))
    avis = artiste.get("avis", [])
    
    # Calcul de la moyenne des notes
    if avis:
        total_notes = sum(item.get("avis", 0) for item in avis)
        moyenne = round(total_notes / len(avis), 2)
    else:
        moyenne = None  # ou 0 selon ton besoin

    return {
        "id": str(artiste["_id"]),
        "name": artiste["name"],
        "shops": shops[0],
        "tatouages": tatouages,
        "rate": moyenne,
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

# Helper to convert ObjectId to string
def serialize_project(project):
    project["_id"] = str(project["_id"])
    return project


def get_projects(user_id: str):
    projects = list(project_collection.find({"user_id": user_id}))
    serialized_projects = []

    base_url = "https://easink.onrender.com/uploads/"

    for p in projects:
        p["_id"] = str(p["_id"])
        p["user_id"] = str(p["user_id"])
        p["artiste_id"] = str(p.get("artiste_id", ""))

        # Add full image URLs
        p["images"] = [base_url + img for img in p.get("images", [])]

        # Fetch and attach artiste data
        if p["artiste_id"]:
            p["artiste"] = get_artiste(p["artiste_id"])
       
            del p["artiste"]["avis"]  # Remove shops if not needed
            del p["artiste"]["tatouages"]  # Remove tattoos if not needed
            del p["artiste"]["questions"]  # Remove questions if not needed
            del p["artiste"]["flashs"]  #

        else:
            p["artiste"] = None

        serialized_projects.append(p)

    return {"projects": serialized_projects}



def edit_project_by_id(project_id: str,new_shop_data: dict):
    try:
        result = project_collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"new_shop": new_shop_data}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating project: {e}")
        return False


def get_project_by_id(id: str):
    project= project_collection.find_one({"_id": ObjectId(id)})
    print(project)

    base_url = "https://easink.onrender.com/uploads/"

 
    project["_id"] = str(project["_id"])
    project["user_id"] = str(project["user_id"])
    project["artiste_id"] = str(project.get("artiste_id", ""))

        # Add full image URLs
    project["images"] = [base_url + img for img in project.get("images", [])]

        # Fetch and attach artiste data
    if project["artiste_id"]:
        project["artiste"] = get_artiste(project["artiste_id"])
       
        del project["artiste"]["avis"]  # Remove shops if not needed
        del project["artiste"]["tatouages"]  # Remove tattoos if not needed
        del project["artiste"]["questions"]  # Remove questions if not needed
        del project["artiste"]["flashs"]  #

    else:
        project["artiste"] = None

       

    return {"project": project}


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
    

def get_config_artiste(id: str):
    artiste =  artiste_collection.find_one({"_id": ObjectId(id)})
    if artiste:
        return artiste['configuration']


# def get_artistes_by_category():
#     # Fetch artists by category
#     nouveaux = artiste_collection.find({"category": "nouveaux"})
#     coups_coeur = artiste_collection.find({"category": "coups_coeur"})
#     populaires = artiste_collection.find({"category": "populaires"})

#     # Helper to format all artists in a cursor
#     def format_artistes(cursor):
#         return [artiste_helper(a) for a in cursor]

#     # Fetch 5 flashs and 5 tatouages from db.flash_tatouages
#     flashs = db.flash_tatouages.find({"type": "flash"}).limit(5)
#     tatouages = db.flash_tatouages.find({"type": "tatouage"}).limit(5)

#     # Format flashs and tatouages (assuming you need only selected fields or convert ObjectId)
#     def format_flash_tatouage(item):
#         return {
#             "id": str(item["_id"]),
#             "type": item["type"],
#             "image": item.get("image"),
#             "name": item.get("name"),  # Assuming you have a name field
#             "artiste": get_artiste(item["artiste"]) if item.get("artiste") else None,            # Add more fields if needed, like "image", "description", etc.
#         }

#     return {
#         "nouveaux": format_artistes(nouveaux),
#         "coups_coeur": format_artistes(coups_coeur),
#         "populaires": format_artistes(populaires),
#         "flashs": [format_flash_tatouage(f) for f in flashs],
#         "tatouages": [format_flash_tatouage(t) for t in tatouages],
#     }


from datetime import datetime, timedelta

def get_artistes_by_category():
    now = datetime.utcnow()
    last_30_days = now - timedelta(days=30)
    print(f"Last 30 days: {last_30_days}")

    # Nouveaux : artistes créés dans les 30 derniers jours
    nouveaux = artiste_collection.find({
        "created_at": {"$gte": last_30_days}
    })

    # Pipeline pour trouver les artistes populaires
    # Étape 1: Compter les réservations par flash_id dans les 30 derniers jours
    reservation_pipeline = [
        {"$match": {"date": {"$gte": last_30_days}}},
        {"$addFields": {
            "flash_id": {"$toObjectId": "$flash_id"}
        }},
        {"$lookup": {
            "from": "flash_tatouages",
            "localField": "flash_id",
            "foreignField": "_id",
            "as": "flash_info"
        }},
        {"$unwind": "$flash_info"},
        {"$group": {
            "_id": "$flash_info.artiste",
            "reservation_count": {"$sum": 1}
        }},
        {"$match": {
            "reservation_count": {"$gte": 1}  # Au moins 10 réservations
        }}
    ]

    popular_artistes_data = list(db.reservation_flash.aggregate(reservation_pipeline))
    
    # Extraire les IDs des artistes populaires
    popular_artistes_ids = []
    for doc in popular_artistes_data:
        artiste_id = doc["_id"]
        if isinstance(artiste_id, str):
            try:
                popular_artistes_ids.append(ObjectId(artiste_id))
            except:
                pass  # Skip invalid ObjectId strings
        elif isinstance(artiste_id, ObjectId):
            popular_artistes_ids.append(artiste_id)

    # Récupérer les artistes populaires
    populaires = list(artiste_collection.find({
        "_id": {"$in": popular_artistes_ids}
    }))
    
    # Coups de coeur : catégorie attribuée manuellement
    coups_coeur = artiste_collection.find({"category": "coups_coeur"})

    def format_artistes(cursor):
        return [artiste_helper(a) for a in cursor]

    # Flashs et tatouages
    flashs = db.flash_tatouages.find({"type": "flash"}).limit(5)
    tatouages = db.flash_tatouages.find({"type": "tatouage"}).limit(5)

    def format_flash_tatouage(item):
        return {
            "id": str(item["_id"]),
            "type": item["type"],
            "image": item.get("image"),
            "name": item.get("name"),
            "artiste": get_artiste(item["artiste"]) if item.get("artiste") else None,
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


def fav_artiste(artiste_id, user_id, favorite):
    # Update if exists, otherwise insert
    result = fav_artiste_collection.update_one(
        {"user_id": user_id, "artiste_id": artiste_id},
        {"$set": {"favorite": favorite}},
        upsert=True
    )

    if result.matched_count > 0:
        return {"message": "Favorite status updated"}
    else:
        return {"message": "Artiste added to favorites"}
    
def get_fav_artistes(user_id):
    # Fetch all favorite artistes for the user
    # Fetch all favorite artistes for the user
    all_fav_artistes = []
    fav_artistes = fav_artiste_collection.find({"user_id": user_id, "favorite": True})
    for fav in fav_artistes:
        all_fav_artistes.append(fav["artiste_id"])

    # Convert to a list of dictionaries
    return all_fav_artistes

def get_all_fav_artistes(user_id):
    # Fetch all favorite artistes for the user
    all_fav_artistes = []
    fav_artistes = fav_artiste_collection.find({"user_id": user_id, "favorite": True})
    for fav in fav_artistes:
        all_fav_artistes.append(fav["artiste_id"])

    # Convert to a list of dictionaries
    return all_fav_artistes


def get_all_fav_artistes(user_id):
    # Fetch all favorite artistes for the user
    all_fav_artistes = []
    fav_artistes = fav_artiste_collection.find({"user_id": user_id, "favorite": True})
    for fav in fav_artistes:
        all_fav_artistes.append(get_artiste(fav["artiste_id"]))

    # Convert to a list of dictionaries
    return all_fav_artistes



def create_project(project: Project):
    project_dict = project.dict()
    # Normalize fields to lowercase
    project_dict["name"] = project_dict["name"].lower()
    if project_dict.get("tags"):
        project_dict["tags"] = [tag.lower() for tag in project_dict["tags"]]
    result =  artiste_collection.insert_one(project_dict)
    new_project =  artiste_collection.find_one({"_id": result.inserted_id})
    return artiste_helper(new_project)




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

