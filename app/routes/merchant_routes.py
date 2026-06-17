from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.merchant_model import Merchant
from app.models.user_model import User
from app.models.expense_model import Expense
from app.schemas.merchant_schema import (
    MerchantRegistrationRequest,
    MerchantUpdateRequest
)
from app.utils.location_utils import (
    calculate_distance,
    generate_digipin
)

from app.utils.ranking_engine import (
    calculate_rank_score
)

from app.utils.auth_dependency import (
    get_current_user,
    get_optional_current_user
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
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    merchants = db.query(Merchant).all()
    results = []

    for merchant in merchants:
        distance = calculate_distance(
            latitude,
            longitude,
            merchant.latitude,
            merchant.longitude
        )
        score = calculate_rank_score(
            distance=distance,
            customer_heading=heading,
            merchant_heading=merchant.heading or 0.0,
            customer_speed=speed,
            category=merchant.category
        )
        
        has_history = False
        if current_user:
            hist_count = db.query(Expense).filter(
                Expense.user_id == current_user.id,
                Expense.merchant_name == merchant.business_name
            ).count()
            if hist_count > 0:
                has_history = True
                score += 15.0 # Boost score for history
        
        score = min(100.0, round(score, 2))

        # Dynamic AI Reason
        heading_diff = abs(heading - (merchant.heading or 0.0))
        if has_history:
            ai_reason = "Recommended because you paid this merchant recently."
        elif heading_diff < 45 and speed > 1.5:
            ai_reason = "Recommended because you are moving toward this store."
        elif speed < 1.0 and merchant.category in ["Cafe", "Restaurant"]:
            ai_reason = "Perfect spot nearby for a quick bite."
        else:
            ai_reason = f"Popular {merchant.category} near your area."

        results.append({
            "id": merchant.id,
            "business_name": merchant.business_name,
            "category": merchant.category,
            "distance": round(distance, 2),
            "score": score,
            "upi_deep_link": merchant.upi_deep_link,
            "ai_reason": ai_reason,
            "latitude": merchant.latitude,
            "longitude": merchant.longitude
        })

    results.sort(
        key=lambda merchant: merchant["score"],
        reverse=True
    )
    return results

@router.get("/dashboard")
def get_merchant_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    # Fetch transactions received by this merchant based on business name matching
    all_received = db.query(Expense).filter(
        Expense.merchant_name == merchant.business_name
    ).order_by(Expense.timestamp.desc()).all()

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    today_received = [e for e in all_received if e.timestamp >= today_start]
    today_revenue = sum(e.amount for e in today_received)
    
    # Customer count
    today_customer_ids = {e.user_id for e in today_received}
    today_customers = len(today_customer_ids)

    # Active customer activity counts
    active_customers_count = db.query(User).filter(User.role == "customer").count()
    nearby_activity_count = max(3, active_customers_count)

    digipin = generate_digipin(merchant.latitude, merchant.longitude)

    payments = []
    for p in all_received[:10]:
        cust = db.query(User).filter(User.id == p.user_id).first()
        payments.append({
            "id": p.id,
            "amount": p.amount,
            "timestamp": p.timestamp.isoformat(),
            "customer_phone": cust.phone_number if cust else "Unknown"
        })

    # Calculate last 7 days daily revenue history
    daily_history = []
    for i in range(6, -1, -1):
        day_date = now - timedelta(days=i)
        day_start = datetime(day_date.year, day_date.month, day_date.day)
        day_end = day_start + timedelta(days=1)
        day_received = [e for e in all_received if day_start <= e.timestamp < day_end]
        day_revenue = sum(e.amount for e in day_received)
        day_label = day_start.strftime("%a")
        daily_history.append({
            "day": day_label,
            "revenue": round(day_revenue, 2)
        })

    return {
        "business_name": merchant.business_name,
        "owner_name": merchant.owner_name,
        "category": merchant.category,
        "digipin": digipin,
        "today_revenue": round(today_revenue, 2),
        "today_customers": today_customers,
        "total_payments_count": len(all_received),
        "nearby_activity_count": nearby_activity_count,
        "recent_payments": payments,
        "upi_status": "Connected" if merchant.upi_deep_link else "Disconnected",
        "digipin_status": "Active",
        "daily_revenue_history": daily_history,
        "gst_number": merchant.gst_number,
        "description": merchant.description,
        "latitude": merchant.latitude,
        "longitude": merchant.longitude,
        "upi_deep_link": merchant.upi_deep_link or ""
    }

@router.put("/update")
def update_merchant(
    payload: MerchantUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    merchant.business_name = payload.business_name
    merchant.owner_name = payload.owner_name
    merchant.category = payload.category
    merchant.gst_number = payload.gst_number
    merchant.description = payload.description
    merchant.latitude = payload.latitude
    merchant.longitude = payload.longitude
    merchant.upi_deep_link = payload.upi_deep_link

    db.commit()
    db.refresh(merchant)
    return {
        "message": "Merchant profile updated successfully"
    }

@router.get("/payments")
def get_merchant_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    all_received = db.query(Expense).filter(
        Expense.merchant_name == merchant.business_name
    ).order_by(Expense.timestamp.desc()).all()

    payments = []
    for p in all_received:
        cust = db.query(User).filter(User.id == p.user_id).first()
        payments.append({
            "id": p.id,
            "amount": p.amount,
            "timestamp": p.timestamp.isoformat(),
            "customer_phone": cust.phone_number if cust else "Unknown"
        })
    return payments