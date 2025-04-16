from fastapi import APIRouter, HTTPException
from models import Item
from bson import ObjectId

router = APIRouter()

# Initialize DB once
from db import init_db
db = init_db()

async def get_items_collection():
    return db["items_collection"]

@router.get("/")
async def get_items():
    collection = await get_items_collection()
    items = []
    try:
        async for item in collection.find():
            item["_id"] = str(item["_id"])
            items.append(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch items: {str(e)}")
    return items

@router.post("/")
async def create_item(item: Item):
    collection = await get_items_collection()
    try:
        result = await collection.insert_one(item.dict(exclude={"_id"}))
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    collection = await get_items_collection()
    try:
        result = await collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count:
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Item not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")
