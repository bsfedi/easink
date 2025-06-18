from fastapi import FastAPI, HTTPException
from artistes.models import *
from artistes.services import create_artiste , get_artistes, get_artiste, update_artiste, delete_artiste
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File

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
