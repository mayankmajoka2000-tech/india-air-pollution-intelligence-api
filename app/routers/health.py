from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["System"])
@router.get("")
def health():
    return {"status":"healthy","version":"5.0.0"}
