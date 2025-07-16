from fastapi import FastAPI, HTTPException
from artistes.models import *
from artistes.services import *
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi import  Query
from typing import List, Optional
from secuirty import *
from utilities import *

artistes_router = APIRouter(tags=["Artistes"])

@artistes_router.post("/artistes/")
async def create(artiste: Artiste):
    return create_artiste(artiste)

@artistes_router.get("/artistes/")
async def read_all():
    return get_artistes()


@artistes_router.post("/fav_artiste/")
async def create_fav_artiste(favorite_artiste: favorite_artiste,token: dict = Depends(token_required)):
    return fav_artiste(favorite_artiste.artiste_id,token['id'] , favorite_artiste.favorite)





@artistes_router.get("/get_fav_artistes/")
async def read_all_fav_artistes(token: dict = Depends(token_required)):
    return get_fav_artistes(token['id'])



@artistes_router.get("/all_fav_artistes/")
async def read_all_fav_artistes(token: dict = Depends(token_required)):
    return get_all_fav_artistes(token['id'])







@artistes_router.get("/artistes/category/")
async def read_all_by_category():
    return get_artistes_by_category()





@artistes_router.get("/artiste_config/{id}")
async def artiste_config(id: str):
    artiste = get_config_artiste(id)
    if artiste:
        return artiste
    raise HTTPException(status_code=404, detail="Artiste not found")

@artistes_router.get("/artistes/{id}")
async def read_one(id: str):
    artiste = get_artiste(id)
    if artiste:
        return artiste
    raise HTTPException(status_code=404, detail="Artiste not found")

@artistes_router.put("/artistes/{id}")
async def update(id: str, artiste: Artiste):
    updated = update_artiste(id, artiste.dict(exclude_unset=True))
    if updated:
        return updated
    raise HTTPException(status_code=404, detail="Artiste not found")

@artistes_router.delete("/artistes/{id}")
async def delete(id: str):
    deleted = delete_artiste(id)
    if deleted:
        return {"message": "Artiste deleted"}
    raise HTTPException(status_code=404, detail="Artiste not found")



@artistes_router.get("/filter")
async def filter_artistes(
    name: Optional[str] = None,
    ville: Optional[str] = None,
    next_availability: Optional[str] = Query(None, enum=["Peu importe", "Aujourd'hui", "Demain", "Cette semaine", "Ce mois"]),
    tags: Optional[List[str]] = Query(None)
):
    return get_filtered_artistes(name, ville, next_availability, tags)




import os
import shutil
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@artistes_router.post("/projects/")
async def create_project(
    images: Optional[List[UploadFile]] = File(None),
    description: str = Form(...),
    taille: str = Form(...),
    emplacement: str = Form(...),
    budget: str = Form(...),
    status: str = Form(...),
    artiste_id: str = Form(...),
    token: dict = Depends(token_required)
):
    saved_filenames = []

    if images:
        for image in images:
            filename = image.filename
            filepath = os.path.join(UPLOAD_DIR, filename)

            # If file already exists, you might want to handle conflict
            with open(filepath, "wb") as f:
                shutil.copyfileobj(image.file, f)

            saved_filenames.append(filename)

    # Prepare project data
    project_dict = {
        "images": saved_filenames,
        "description": description,
        "taille": taille,
        "emplacement": emplacement,
        "budget": budget,
        "status": status,
        "estimation":"",
        "arrhes":0,
        "date":None,

        "shop":"",
        "type_validation":"",
        "time":[],

        "status_shop":"waiting for confirmation",
        "user_id": token["id"],  # Assuming token contains user ID
        "artiste_id": artiste_id
    }

    # Insert into MongoDB
    result = project_collection.insert_one(project_dict)
    project_dict["_id"] = str(result.inserted_id)
    return {"message": "Project created successfully", "project": project_dict}

# Helper to convert ObjectId to string
def serialize_project(project):
    project["_id"] = str(project["_id"])
    return project

@artistes_router.get("/projects/")
def get_all_projects( token: dict = Depends(token_required)):
    return get_projects(token["id"])

@artistes_router.get("/projects/{id}")
def get_project( id:str ,token: dict = Depends(token_required)):
    return get_project_by_id(id)

