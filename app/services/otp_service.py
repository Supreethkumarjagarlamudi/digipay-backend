import requests
from app.config import settings
def send_otp_sms(
    phone_number: str,
    otp: str
):
    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "template_id": settings.MSG91_TEMPLATE_ID,
        "mobile": f"91{phone_number}",
        "otp": otp
    }
    headers = {
        "authkey": settings.MSG91_AUTH_KEY
    }
    response = requests.post(
        url,
        data=payload,
        headers=headers
    )

    return response.json()