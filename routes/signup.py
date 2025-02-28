from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import users_collection
import bcrypt

router = APIRouter()


class SignupRequest(BaseModel):
    firstname: str
    email: EmailStr
    password: str
    repeat_password: str


@router.post("/signup")
async def signup(request: SignupRequest):
    # 检查密码是否匹配
    if request.password != request.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # 检查邮箱是否已存在
    existing_user = users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 加密密码
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt())

    # 存储用户信息
    users_collection.insert_one({
        "firstname": request.firstname,
        "email": request.email,
        "password_hash": hashed_password
    })

    return {"message": "User registered successfully"}
