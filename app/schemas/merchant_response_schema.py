from pydantic import BaseModel

class NearbyMerchantResponse(
    BaseModel
):
    id: int
    business_name: str
    category: str
    latitude: float
    longitude: float
    upi_deep_link: str
    distance: float