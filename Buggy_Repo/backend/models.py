from pydantic import BaseModel

class Item(BaseModel):  # ✅ Inherit from BaseModel
    name: int
    description: str

class User(BaseModel):
    username: str
    bio: str
