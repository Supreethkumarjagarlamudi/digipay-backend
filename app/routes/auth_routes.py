import random

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.otp_model import OTPVerification
from app.models.user_model import User
from app.utils.jwt_handler import create_access_token
from app.services.otp_service import send_otp_sms
from app.schemas.auth_schema import (
    SendOTPRequest,
    VerifyOTPRequest
)
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# SEND OTP

@router.post("/send-otp")
def send_otp(
    payload: SendOTPRequest,
    db: Session = Depends(get_db)
):

    otp = str(random.randint(100000, 999999))
    db.query(OTPVerification).filter(
        OTPVerification.phone_number == payload.phone_number,
        OTPVerification.verified == False
    ).delete()
    db.commit()

    otp_entry = OTPVerification(
        phone_number=payload.phone_number,
        otp_code=otp
    )

    db.add(otp_entry)
    db.commit()


    return {
        "message": "OTP Sent Successfully",
        "otp": otp
    }

# VERIFY OTP

@router.post("/verify-otp")

def verify_otp(

    payload: VerifyOTPRequest,

    db: Session = Depends(get_db)

):

    otp_entry = db.query(

        OTPVerification

    ).filter(

        OTPVerification.phone_number == payload.phone_number,

        OTPVerification.otp_code == payload.otp_code,

        OTPVerification.verified == False

    ).first()

    # OTP NOT FOUND

    if otp_entry is None:

        raise HTTPException(

            status_code=400,

            detail="Invalid OTP"

        )

    # OTP EXPIRED

    if datetime.utcnow() - otp_entry.created_at > timedelta(minutes=5):

        raise HTTPException(

            status_code=400,

            detail="OTP Expired"

        )

    # MARK VERIFIED

    otp_entry.verified = True

    user = db.query(User).filter(

        User.phone_number == payload.phone_number

    ).first()

    # CREATE USER IF NOT EXISTS

    if user is None:

        user = User(

            phone_number=payload.phone_number,

            is_verified=True

        )

        db.add(user)

        db.commit()

        db.refresh(user)

    else:

        user.is_verified = True

        db.commit()

        db.refresh(user)

    # ACCESS TOKEN

    access_token = create_access_token({

        "user_id": user.id,

        "phone_number": user.phone_number

    })

    return {

        "message": "OTP Verified Successfully",

        "access_token": access_token,

        "token_type": "bearer",

        "user": {

            "id": user.id,

            "phone_number": user.phone_number

        },

        "role": user.role,

        "profile_completed": user.profile_completed

    }