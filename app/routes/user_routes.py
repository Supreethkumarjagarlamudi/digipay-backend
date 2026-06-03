from fastapi import APIRouter
from fastapi import Depends

from app.models.user_model import User

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
        "is_verified": current_user.is_verified
    }