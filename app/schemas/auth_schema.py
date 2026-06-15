from pydantic import BaseModel

class SendOTPRequest(BaseModel):

    phone_number: str

class VerifyOTPRequest(BaseModel):

    phone_number: str
    otp_code: str

class UpdateProfileRequest(BaseModel):
    full_name: str
    email: str | None = None
    role: str | None = None
    monthly_budget: float | None = None
    monthly_income: float | None = None