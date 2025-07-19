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
    import random

    # Generate a random integer between 1 and 10 (inclusive)
    arrhes = random.randint(25, 99)

    type_validation= 'without suggestion' or 'With suggestion'
    if type_validation == 'With suggestion':
        time = [
                    {
                    "date": datetime.now(),
                    "time": "16:00 - 18:00"
                    },
                    {
                    "date": datetime.now()+1,
                    "time": "14:00 - 18:00"
                    },
                    {
                    "date": datetime.now()+2,
                    "time": "15:00 - 16:00"
                    }
                ]
    else:
        time = []



    # Prepare project data
    project_dict = {
        "images": saved_filenames,
        "couverture":saved_filenames[0] if saved_filenames else "400x400.svg",
        "description": description,
        "taille": taille,
        "emplacement": emplacement,
        "budget": budget,
        "status": status,
        "estimation":"",
        "arrhes":arrhes ,
        "date":None,

        "shop":"",
        "type_validation":type_validation ,
        "time":time,

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


@artistes_router.put("/projects/{id}")
def update_project(id: str, edit_project: dict, token: dict = Depends(token_required)):
    updated_project = update_project_by_id(id, edit_project)
    if updated_project:
        return {"message": "Project updated successfully", "project": updated_project}
    raise HTTPException(status_code=404, detail="Project not found")


@artistes_router.post("/avis/{artiste_id}/{project_id}")
def create_avis(
    artiste_id: str,
    project_id: str,
    avis: str = Form(...),  # stringified JSON input
    image: Optional[UploadFile] = File(None),
    token: dict = Depends(token_required)
):
    try:
        avis_data = json.loads(avis)  # parse avis JSON
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for 'avis'")

    avis_data['user'] = token['id']
    avis_data['date'] = datetime.now().isoformat()  # Add current date

    print(image)

    # Optionally process the image if it was provided
    if image:
        # Example: read and save the image or store metadata
        filename = image.filename
        name, ext = os.path.splitext(filename)
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        
        new_filename = f"{name}_{date_str}{ext}"
        avis_data['image'] = new_filename
        filepath = os.path.join(UPLOAD_DIR, new_filename)

            # If file already exists, you might want to handle conflict
        with open(filepath, "wb") as f:
            shutil.copyfileobj(image.file, f)
    else:
        avis_data['image'] = ""

    created_avis = insert_avis_artiste(artiste_id, project_id,avis_data)

    if created_avis:
        return {"message": "Avis created successfully", "avis": created_avis}

    raise HTTPException(status_code=404, detail="Artiste not found or Avis creation failed")

@artistes_router.put("/project/{project_id}/couverture")
async def update_project_couverture(project_id: str, couverture: UploadFile = File(...)):
    # Find project
    project = project_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Save the new image

    filename = couverture.filename
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(couverture.file, f)

    # Update MongoDB document
    project_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"couverture": filename}}
    )

    return {
        "message": "Couverture updated successfully",
        "couverture_url": base_url + filename
    }