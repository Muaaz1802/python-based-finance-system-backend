from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.transaction import TransactionType
from app.models.user import Role, User
from app.schemas.transaction import PaginatedTransactions, TransactionCreate, TransactionResponse, TransactionUpdate
from app.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=PaginatedTransactions)
def list_transactions(
    type: TransactionType | None = Query(default=None),
    category: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results, total = transaction_service.get_transactions(
        db, current_user, type, category, from_date, to_date, page, page_size
    )
    return PaginatedTransactions(total=total, page=page, page_size=page_size, results=results)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = transaction_service.get_transaction_by_id(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin)),
):
    return transaction_service.create_transaction(db, data, current_user.id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin)),
):
    transaction = transaction_service.get_transaction_by_id(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction_service.update_transaction(db, transaction, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin)),
):
    transaction = transaction_service.get_transaction_by_id(db, transaction_id, current_user)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    transaction_service.delete_transaction(db, transaction)
