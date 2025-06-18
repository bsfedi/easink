from fastapi import FastAPI, HTTPException
from artistes.models import *
from artistes.services import *
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi import  Query
from typing import List, Optional
artistes_router = APIRouter(tags=["Artistes"])

@artistes_router.post("/artistes/")
async def create(artiste: Artiste):
    return create_artiste(artiste)

@artistes_router.get("/artistes/")
async def read_all():
    return get_artistes()

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