from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be blank")
        return v.strip()


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    type: TransactionType | None = None
    category: str | None = None
    transaction_date: date | None = None
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[TransactionResponse]
