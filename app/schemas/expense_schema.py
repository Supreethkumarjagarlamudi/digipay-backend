from pydantic import BaseModel
from datetime import datetime

class ExpenseCreate(BaseModel):
    merchant_name: str
    amount: float
    category: str
    latitude: float | None = None
    longitude: float | None = None
    heading: float | None = None
    speed: float | None = None

class ExpenseResponse(BaseModel):
    id: int
    merchant_name: str
    amount: float
    category: str
    timestamp: datetime
    latitude: float | None = None
    longitude: float | None = None
    heading: float | None = None
    speed: float | None = None

    class Config:
        from_attributes = True

class CategoryInsight(BaseModel):
    category: str
    amount: float
    percentage: float
    icon: str

class WalletAnalyticsResponse(BaseModel):
    balance: float
    spent_this_month: float
    spent_this_week: float
    saved_this_month: float
    budget_limit: float
    budget_progress: float  # e.g., 0.65 for 65%
    category_breakdown: list[CategoryInsight]
    recent_transactions: list[ExpenseResponse]
    savings_suggestions: list[str]
    peak_spending_time: str
    location_spending_summary: str
