from decimal import Decimal

from pydantic import BaseModel

from app.schemas.transaction import TransactionResponse


class FinancialSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal


class CategoryBreakdown(BaseModel):
    category: str
    total: Decimal
    count: int


class MonthlyTotal(BaseModel):
    year: int
    month: int
    income: Decimal
    expenses: Decimal


class AnalyticsDashboard(BaseModel):
    summary: FinancialSummary
    by_category: list[CategoryBreakdown]
    monthly: list[MonthlyTotal]
    recent: list[TransactionResponse]
