from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import users_collection
import bcrypt

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    # 查找用户
    user = users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials, please turn to signup page and first register")

    # 验证密码
    if not bcrypt.checkpw(request.password.encode("utf-8"), user["password_hash"]):
        raise HTTPException(status_code=401, detail="The password is not correct! Please check your password!")

    return {"message": "Login successful"}
