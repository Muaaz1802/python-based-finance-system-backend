from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.models.user import Role, User
from app.schemas.analytics import CategoryBreakdown, FinancialSummary, MonthlyTotal


def _base_query(db: Session, current_user: User):
    query = db.query(Transaction)
    if current_user.role != Role.admin:
        query = query.filter(Transaction.user_id == current_user.id)
    return query


def get_summary(db: Session, current_user: User) -> FinancialSummary:
    base = _base_query(db, current_user)

    total_income = (
        base.filter(Transaction.type == TransactionType.income)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    total_expenses = (
        base.filter(Transaction.type == TransactionType.expense)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    return FinancialSummary(
        total_income=Decimal(str(total_income)),
        total_expenses=Decimal(str(total_expenses)),
        balance=Decimal(str(total_income)) - Decimal(str(total_expenses)),
    )


def get_category_breakdown(db: Session, current_user: User) -> list[CategoryBreakdown]:
    base = _base_query(db, current_user)

    rows = (
        base.with_entities(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return [
        CategoryBreakdown(
            category=row.category, total=Decimal(str(row.total)), count=row.count
        )
        for row in rows
    ]


def get_monthly_totals(db: Session, current_user: User) -> list[MonthlyTotal]:
    base = _base_query(db, current_user)

    rows = (
        base.with_entities(
            extract("year", Transaction.transaction_date).label("year"),
            extract("month", Transaction.transaction_date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .group_by("year", "month", Transaction.type)
        .order_by("year", "month")
        .all()
    )

    aggregated: dict[tuple, dict] = {}
    for row in rows:
        key = (int(row.year), int(row.month))
        if key not in aggregated:
            aggregated[key] = {"income": Decimal("0"), "expenses": Decimal("0")}
        if row.type == TransactionType.income:
            aggregated[key]["income"] = Decimal(str(row.total))
        else:
            aggregated[key]["expenses"] = Decimal(str(row.total))

    return [
        MonthlyTotal(year=year, month=month, **data)
        for (year, month), data in sorted(aggregated.items())
    ]


def get_recent_transactions(
    db: Session, current_user: User, limit: int = 10
) -> list[Transaction]:
    return (
        _base_query(db, current_user)
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
