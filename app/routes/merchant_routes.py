from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.merchant_model import Merchant
from app.models.user_model import User
from app.schemas.merchant_schema import (
    MerchantRegistrationRequest
)
from app.utils.location_utils import (
    calculate_distance
)

from app.utils.ranking_engine import (
    calculate_rank_score
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
    return {
        "message":
        "Merchant Registered Successfully"
    }
@router.get("/nearby")

def get_nearby_merchants(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):

    merchants = db.query(
        Merchant
    ).all()
    results = []
    for merchant in merchants:
        distance = calculate_distance(
            latitude,
            longitude,
            merchant.latitude,
            merchant.longitude
        )

        results.append({
            "id":
                merchant.id,
            "business_name":
                merchant.business_name,
            "category":
                merchant.category,
            "latitude":
                merchant.latitude,
            "longitude":
                merchant.longitude,
            "upi_deep_link":
                merchant.upi_deep_link,
            "distance":
                round(
                    distance,
                    2
                )
        })

    results.sort(

        key=lambda x:

        x["distance"]

    )

    return results

@router.get("/recommendations")

def get_recommendations(

    latitude: float,

    longitude: float,

    heading: float,

    speed: float,

    db: Session = Depends(get_db)

):
    merchants = db.query(
        Merchant
    ).all()

    results = []

    for merchant in merchants:
        distance = calculate_distance(

            latitude,
            longitude,

            merchant.latitude,
            merchant.longitude
        )
        score = calculate_rank_score(

            distance=
                distance,

            customer_heading=
                heading,

            merchant_heading=
                merchant.heading,

            customer_speed=
                speed,

            category=
                merchant.category
        )
        results.append({

            "id":
                merchant.id,

            "business_name":
                merchant.business_name,

            "category":
                merchant.category,

            "distance":
                round(distance, 2),

            "score":
                score,

            "upi_deep_link":
                merchant.upi_deep_link
        })
    results.sort(
        key=lambda merchant:
        merchant["score"],
        reverse=True
    )
    return results