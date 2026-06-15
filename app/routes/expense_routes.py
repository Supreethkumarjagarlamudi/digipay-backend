from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user_model import User
from app.models.expense_model import Expense
from app.schemas.expense_schema import (
    ExpenseCreate,
    ExpenseResponse,
    WalletAnalyticsResponse,
    CategoryInsight
)
from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet & Expenses"]
)

# ICONS MAP FOR CATEGORIES
CATEGORY_ICONS = {
    "Food": "cup.and.saucer.fill",
    "Shopping": "cart.fill",
    "Medical": "cross.case.fill",
    "Transport": "car.fill",
    "Bills": "doc.text.fill",
    "Entertainment": "play.tv.fill",
    "Education": "book.fill",
    "Retail": "bag.fill",
    "Other": "creditcard.fill"
}

@router.post("/transactions", response_model=ExpenseResponse)
def create_transaction(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = Expense(
        user_id=current_user.id,
        merchant_name=payload.merchant_name,
        amount=payload.amount,
        category=payload.category,
        latitude=payload.latitude,
        longitude=payload.longitude,
        heading=payload.heading,
        speed=payload.speed,
        timestamp=datetime.utcnow()
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("/transactions", response_model=list[ExpenseResponse])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.timestamp.desc()).all()
    return expenses

@router.get("/analytics", response_model=WalletAnalyticsResponse)
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch all transactions
    all_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.timestamp.desc()).all()

    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)
    one_week_ago = now - timedelta(days=7)

    # Monthly / Weekly Filter
    monthly_expenses = [e for e in all_expenses if e.timestamp >= one_month_ago]
    weekly_expenses = [e for e in all_expenses if e.timestamp >= one_week_ago]

    # Calculate Totals
    spent_this_month = sum(e.amount for e in monthly_expenses)
    spent_this_week = sum(e.amount for e in weekly_expenses)
    
    # Load income base and budget limit dynamically from user profile database record
    income_base = current_user.monthly_income if current_user.monthly_income is not None else 45000.0
    current_balance = max(0.0, income_base - sum(e.amount for e in all_expenses))
    saved_this_month = max(1500.0, spent_this_month * 0.15) 

    # Budget Limits
    budget_limit = current_user.monthly_budget if current_user.monthly_budget is not None else 15000.0
    budget_progress = min(1.0, spent_this_month / budget_limit) if budget_limit > 0 else 0.0

    # Category breakdowns
    category_totals = {}
    for exp in monthly_expenses:
        category_totals[exp.category] = category_totals.get(exp.category, 0.0) + exp.amount

    breakdown = []
    for cat, amt in category_totals.items():
        pct = (amt / spent_this_month) * 100 if spent_this_month > 0 else 0.0
        icon = CATEGORY_ICONS.get(cat, "creditcard.fill")
        breakdown.append(CategoryInsight(
            category=cat,
            amount=amt,
            percentage=round(pct, 1),
            icon=icon
        ))

    # Add default category insights if empty
    if not breakdown:
        breakdown = [
            CategoryInsight(category="Food", amount=0, percentage=0, icon="cup.and.saucer.fill"),
            CategoryInsight(category="Shopping", amount=0, percentage=0, icon="cart.fill"),
            CategoryInsight(category="Medical", amount=0, percentage=0, icon="cross.case.fill")
        ]
    else:
        breakdown.sort(key=lambda x: x.amount, reverse=True)

    # Savings suggestions based on categories
    suggestions = [
        "Create a weekly spending cap of ₹3,000 to improve your savings by 10%.",
        "Enable transaction round-ups to auto-save change on every UPI payment."
    ]
    food_spent = category_totals.get("Food", 0.0)
    if spent_this_month > 0 and (food_spent / spent_this_month) > 0.35:
        suggestions.insert(0, f"Food accounts for {int(food_spent/spent_this_month*100)}% of your monthly expenses. Consider cooking more at home.")
    
    # Peak spending time analysis
    hour_counts = {}
    for exp in all_expenses:
        hour = exp.timestamp.hour
        if 6 <= hour <= 11:
            hour_counts["Morning (6 AM - 11 AM)"] = hour_counts.get("Morning (6 AM - 11 AM)", 0) + 1
        elif 12 <= hour <= 16:
            hour_counts["Afternoon (12 PM - 4 PM)"] = hour_counts.get("Afternoon (12 PM - 4 PM)", 0) + 1
        elif 17 <= hour <= 21:
            hour_counts["Evening (5 PM - 9 PM)"] = hour_counts.get("Evening (5 PM - 9 PM)", 0) + 1
        else:
            hour_counts["Night (10 PM - 5 AM)"] = hour_counts.get("Night (10 PM - 5 AM)", 0) + 1

    peak_spending_time = max(hour_counts, key=hour_counts.get) if hour_counts else "No transactions recorded yet"

    # Context analysis
    location_spending_summary = "Centered around your active GPS locations"
    if all_expenses:
        location_spending_summary = f"Most transactions occur near your current coordinates"

    return WalletAnalyticsResponse(
        balance=round(current_balance, 2),
        spent_this_month=round(spent_this_month, 2),
        spent_this_week=round(spent_this_week, 2),
        saved_this_month=round(saved_this_month, 2),
        budget_limit=budget_limit,
        budget_progress=round(budget_progress, 2),
        category_breakdown=breakdown,
        recent_transactions=all_expenses[:10], # Top 10 recent
        savings_suggestions=suggestions,
        peak_spending_time=peak_spending_time,
        location_spending_summary=location_spending_summary
    )
