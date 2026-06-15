from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.auth_schema import UpdateProfileRequest
from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/me")
def get_profile(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "phone_number": current_user.phone_number,
        "is_verified": current_user.is_verified,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "profile_completed": current_user.profile_completed
    }

@router.post("/update-profile")
def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = payload.full_name
    current_user.email = payload.email
    current_user.profile_completed = True
    
    if payload.role:
        current_user.role = payload.role
        
    if payload.monthly_budget is not None:
        current_user.monthly_budget = payload.monthly_budget
        
    if payload.monthly_income is not None:
        current_user.monthly_income = payload.monthly_income
        
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "phone_number": current_user.phone_number,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "profile_completed": current_user.profile_completed,
            "monthly_budget": current_user.monthly_budget,
            "monthly_income": current_user.monthly_income
        }
    }