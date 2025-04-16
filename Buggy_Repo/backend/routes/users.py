from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from models import User
from bson import ObjectId
from typing import List

router = APIRouter(tags=["users"])

# Response models
class UserResponse(BaseModel):
    id: str
    username: str
    bio: str

class UserCreateResponse(BaseModel):
    id: str

async def get_users_collection():
    from db import init_db
    return init_db()["users_collection"]

@router.get("/", response_model=List[UserResponse],
           summary="Get all users",
           description="Returns a list of all registered users")
async def get_users():
    """Get all users"""
    collection = await get_users_collection()
    users = []
    async for user in collection.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "bio": user["bio"]
        })
    return users

@router.post("/", response_model=UserCreateResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create a new user",
            description="Creates a new user with username and bio")
async def create_user(user: User):
    """Create a new user"""
    collection = await get_users_collection()
    
    # Check if username already exists
    existing_user = await collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    result = await collection.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@router.delete("/{user_id}", 
              summary="Delete a user",
              description="Deletes a user with the specified ID")
async def delete_user(user_id: str):
    """Delete a user by ID"""
    collection = await get_users_collection()
    
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    result = await collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"status": "deleted"}

@router.get("/{user_id}", response_model=UserResponse,
           summary="Get user by ID",
           description="Returns details for a specific user")
async def get_user(user_id: str):
    """Get a user by ID"""
    collection = await get_users_collection()
    
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await collection.find_one({"_id": obj_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "bio": user["bio"]
    }
