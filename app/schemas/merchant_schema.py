from pydantic import BaseModel


class MerchantRegistrationRequest(
    BaseModel
):

    business_name: str

    owner_name: str

    category: str

    gst_number: str | None = None

    description: str | None = None

    latitude: float

    longitude: float

    altitude: float

    accuracy: float

    heading: float

    speed: float

    upi_deep_link: str