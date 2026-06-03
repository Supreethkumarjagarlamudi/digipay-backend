from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.merchant_model import Merchant
from app.models.user_model import User
from app.schemas.merchant_schema import (
    MerchantRegistrationRequest
)

from app.utils.auth_dependency import (
    get_current_user
)

router = APIRouter(
    prefix="/merchant",
    tags=["Merchant"]
)

@router.post("/register")
def register_merchant(

    payload: MerchantRegistrationRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    merchant = Merchant(

        user_id=current_user.id,

        business_name=
        payload.business_name,

        owner_name=
        payload.owner_name,

        category=
        payload.category,

        gst_number=
        payload.gst_number,

        description=
        payload.description,

        latitude=
        payload.latitude,

        longitude=
        payload.longitude,

        altitude=
        payload.altitude,

        accuracy=
        payload.accuracy,

        heading=
        payload.heading,

        speed=
        payload.speed,

        upi_deep_link=
        payload.upi_deep_link
    )

    db.add(merchant)

    current_user.role = "merchant"

    current_user.profile_completed = True

    db.commit()

    existing_merchant = db.query(

        Merchant

    ).filter(

        Merchant.user_id ==

        current_user.id

    ).first()

    if existing_merchant:

        return {

            "message":

            "Merchant already registered"

        }