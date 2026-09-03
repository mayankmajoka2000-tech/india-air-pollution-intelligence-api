from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
router=APIRouter(prefix="/auth",tags=["Security"])
class Login(BaseModel): username:str; password:str
@router.post("/login")
def login(x:Login):
    if not x.username or not x.password: raise HTTPException(400,"Credentials required")
    token=hashlib.sha256(f"{x.username}:{x.password}".encode()).hexdigest()
    return {"access_token":token,"token_type":"bearer","note":"Replace with JWT/OAuth2 and persistent user store in production."}
