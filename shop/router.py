from fastapi import FastAPI, HTTPException
from shop.models import *
from shop.services import *
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi import  Query
from typing import List, Optional
shop_router = APIRouter(tags=["shop"])

@shop_router.post("/shop/")
async def create(shop: shop):
    return create_shop(shop)

@shop_router.get("/shop/")
async def read_all():
    return get_shops()

@shop_router.get("/shop/{id}")
async def read_one(id: str):
    shop = get_shop(id)
    if shop:
        return shop
    raise HTTPException(status_code=404, detail="shop not found")

@shop_router.put("/shop/{id}")
async def update(id: str, shop: shop):
    updated = update_shop(id, shop.dict(exclude_unset=True))
    if updated:
        return updated
    raise HTTPException(status_code=404, detail="shop not found")

@shop_router.delete("/shop/{id}")
async def delete(id: str):
    deleted = delete_shop(id)
    if deleted:
        return {"message": "shop deleted"}
    raise HTTPException(status_code=404, detail="shop not found")


