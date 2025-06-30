from fastapi import FastAPI, HTTPException
from flash_tatouages.models import *
from flash_tatouages.services import *
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi import  Query
from typing import List, Optional
from secuirty import *
from utilities import *
flash_tatouages_router = APIRouter(tags=["flash_tatouages"])

@flash_tatouages_router.post("/flash_tatouages/")
async def create(flash_tatouages: flash_tatouages):
    return create_flash_tatouages(flash_tatouages)

@flash_tatouages_router.get("/flash_tatouages/")
async def read_all():
    return get_flash_tatouagess()

@flash_tatouages_router.get("/flash_tatouages/{id}")
async def read_one(id: str):
    flash_tatouages = get_flash_tatouages(id)
    if flash_tatouages:
        return flash_tatouages
    raise HTTPException(status_code=404, detail="flash_tatouages not found")

@flash_tatouages_router.put("/flash_tatouages/{id}")
async def update(id: str, flash_tatouages: flash_tatouages):
    updated = update_flash_tatouages(id, flash_tatouages.dict(exclude_unset=True))
    if updated:
        return updated
    raise HTTPException(status_code=404, detail="flash_tatouages not found")

@flash_tatouages_router.get("/flash_tatouages_by_type/{type}")
async def read_by_type(type: str):
    flash_tatouages = get_flash_tatouages_by_type(type)
    if flash_tatouages:
        return flash_tatouages
    raise HTTPException(status_code=404, detail="flash_tatouages not found")



@flash_tatouages_router.get("/flash_tatouages/category/{type}")
async def read_by_category(type):
    return get_flash_tatouages_by_category(type)

@flash_tatouages_router.delete("/flash_tatouages/{id}")
async def delete(id: str):
    deleted = delete_flash_tatouages(id)
    if deleted:
        return {"message": "flash_tatouages deleted"}
    raise HTTPException(status_code=404, detail="flash_tatouages not found")


@flash_tatouages_router.post("/flash_tatouages/reserve")
async def reserve_flash_tatouages(reserver_flash: Reserver_flash,token: dict = Depends(token_required)):
    reserver_flash.user_id =token["id"]

    flash_tatouages = reserver_falsh(reserver_flash)
    if flash_tatouages:
        return {"message": "Flash tatouage reserved successfully", "flash_tatouages": flash_tatouages}
    raise HTTPException(status_code=404, detail="flash tatouage not found")

@flash_tatouages_router.get("/flash_reservations/")
async def get_reserve_flash_tatouages(token: dict = Depends(token_required)):

    
    flash_tatouages = get_reserver_falsh(token["id"])
    if flash_tatouages:
        return {"message": "Flash tatouage reserved successfully", "flash_tatouages": flash_tatouages}
    raise HTTPException(status_code=404, detail="flash tatouage not found")




