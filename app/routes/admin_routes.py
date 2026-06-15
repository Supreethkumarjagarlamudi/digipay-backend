from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.user_model import User
from app.models.merchant_model import Merchant
from app.models.expense_model import Expense
from app.utils.auth_dependency import get_current_user
from app.utils.location_utils import generate_digipin

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin role required."
        )
    return current_user

# 1. GET /admin/dashboard - Global KPIs
@router.get("/dashboard")
def get_admin_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    # Transactions
    all_txs = db.query(Expense).all()
    today_txs = [tx for tx in all_txs if tx.timestamp >= today_start]
    
    today_revenue = sum(tx.amount for tx in today_txs)
    total_tx_count = len(all_txs)
    total_tx_volume = sum(tx.amount for tx in all_txs)
    avg_tx_value = (total_tx_volume / total_tx_count) if total_tx_count > 0 else 0.0
    
    # Counts
    total_users = db.query(User).filter(User.role == "customer").count()
    total_merchants = db.query(Merchant).count()
    
    return {
        "today_revenue": round(today_revenue, 2),
        "total_transactions": total_tx_count,
        "average_transaction_value": round(avg_tx_value, 2),
        "total_users": total_users,
        "total_merchants": total_merchants,
        "active_devices_today": max(5, total_users + 2) # mock activity count
    }

# 2. GET /admin/transactions - Paginated, filterable, and sortable list
@router.get("/transactions")
def get_admin_transactions(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Expense)
    
    if category:
        query = query.filter(Expense.category == category)
        
    if search:
        query = query.filter(
            (Expense.merchant_name.ilike(f"%{search}%")) |
            (Expense.category.ilike(f"%{search}%"))
        )
        
    total_count = query.count()
    txs = query.order_by(Expense.timestamp.desc()).offset(offset).limit(limit).all()
    
    results = []
    for tx in txs:
        # Resolve customer phone
        cust = db.query(User).filter(User.id == tx.user_id).first()
        results.append({
            "id": tx.id,
            "user_id": tx.user_id,
            "customer_phone": cust.phone_number if cust else "Unknown",
            "merchant_name": tx.merchant_name,
            "amount": tx.amount,
            "category": tx.category,
            "latitude": tx.latitude,
            "longitude": tx.longitude,
            "timestamp": tx.timestamp.isoformat()
        })
        
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "transactions": results
    }

# 3. GET /admin/merchants - List of all registered merchants
@router.get("/merchants")
def get_admin_merchants(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    merchants = db.query(Merchant).all()
    results = []
    
    for m in merchants:
        # Generate digipin on the fly using coordinates
        digipin = generate_digipin(m.latitude, m.longitude) if (m.latitude and m.longitude) else "UNKNOWN"
        results.append({
            "id": m.id,
            "user_id": m.user_id,
            "business_name": m.business_name,
            "owner_name": m.owner_name,
            "category": m.category,
            "gst_number": m.gst_number,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "digipin": digipin,
            "is_active": m.is_active,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })
    return results

# 4. PUT /admin/merchants/{id}/status - Toggle status (active/inactive)
@router.put("/merchants/{id}/status")
def toggle_merchant_status(
    id: int,
    is_active: bool,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    merchant = db.query(Merchant).filter(Merchant.id == id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
        
    merchant.is_active = is_active
    db.commit()
    db.refresh(merchant)
    
    return {
        "message": f"Merchant is_active state set to {is_active}",
        "merchant_id": id,
        "is_active": merchant.is_active
    }

# 5. DELETE /admin/merchants/{id} - Delete merchant profile
@router.delete("/merchants/{id}")
def delete_merchant(
    id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    merchant = db.query(Merchant).filter(Merchant.id == id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
        
    db.delete(merchant)
    db.commit()
    
    return {
        "message": "Merchant profile deleted successfully",
        "merchant_id": id
    }

# 6. GET /admin/analytics - Global analytics insights
@router.get("/analytics")
def get_admin_analytics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    all_expenses = db.query(Expense).all()
    
    # Category Distribution
    category_totals = {}
    for tx in all_expenses:
        category_totals[tx.category] = category_totals.get(tx.category, 0.0) + tx.amount
        
    category_data = []
    total_volume = sum(category_totals.values())
    for cat, amt in category_totals.items():
        pct = (amt / total_volume * 100) if total_volume > 0 else 0.0
        category_data.append({
            "category": cat,
            "amount": round(amt, 2),
            "percentage": round(pct, 1)
        })
        
    # Hourly peak activity counts
    hour_counts = {i: 0 for i in range(24)}
    for tx in all_expenses:
        hour = tx.timestamp.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
    hourly_trends = [{"hour": f"{h:02d}:00", "count": count} for h, count in hour_counts.items()]
    
    # Weekly Volume (Last 4 weeks)
    now = datetime.utcnow()
    weekly_trends = []
    for i in range(4):
        start_date = now - timedelta(days=(i+1)*7)
        end_date = now - timedelta(days=i*7)
        week_txs = [tx for tx in all_expenses if start_date <= tx.timestamp < end_date]
        weekly_trends.append({
            "week": f"{i+1} Week(s) Ago",
            "amount": round(sum(tx.amount for tx in week_txs), 2),
            "count": len(week_txs)
        })
    weekly_trends.reverse()
    
    return {
        "category_distribution": category_data,
        "hourly_trends": hourly_trends,
        "weekly_trends": weekly_trends
    }
