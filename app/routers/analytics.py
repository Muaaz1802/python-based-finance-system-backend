from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.user import Role, User
from app.schemas.analytics import AnalyticsDashboard, CategoryBreakdown, FinancialSummary, MonthlyTotal
from app.schemas.transaction import TransactionResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analyst_or_admin = require_roles(Role.analyst, Role.admin)


@router.get("/summary", response_model=FinancialSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin),
):
    return analytics_service.get_summary(db, current_user)


@router.get("/by-category", response_model=list[CategoryBreakdown])
def by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin),
):
    return analytics_service.get_category_breakdown(db, current_user)


@router.get("/monthly", response_model=list[MonthlyTotal])
def monthly(
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin),
):
    return analytics_service.get_monthly_totals(db, current_user)


@router.get("/recent", response_model=list[TransactionResponse])
def recent(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin),
):
    return analytics_service.get_recent_transactions(db, current_user, limit)


@router.get("/dashboard", response_model=AnalyticsDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin),
):
    return AnalyticsDashboard(
        summary=analytics_service.get_summary(db, current_user),
        by_category=analytics_service.get_category_breakdown(db, current_user),
        monthly=analytics_service.get_monthly_totals(db, current_user),
        recent=analytics_service.get_recent_transactions(db, current_user),
    )
