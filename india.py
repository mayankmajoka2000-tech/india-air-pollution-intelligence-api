from fastapi import APIRouter
router = APIRouter(prefix="/india", tags=["India"])
STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli and Daman and Diu","Delhi","Jammu and Kashmir","Ladakh","Lakshadweep","Puducherry"]
@router.get("/states")
def states(): return {"country":"India","count":len(STATES),"states_ut":STATES}
@router.get("/hierarchy")
def hierarchy(): return {"levels":["India","State/UT","District","City/ULB","Station","Source Sector"],"sectors":["transport","industry","power","construction","road_dust","waste","agriculture","residential"]}
