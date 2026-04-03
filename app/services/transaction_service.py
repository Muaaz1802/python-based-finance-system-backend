from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.models.user import Role, User
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def get_transactions(
    db: Session,
    current_user: User,
    type: TransactionType | None,
    category: str | None,
    from_date: date | None,
    to_date: date | None,
    page: int,
    page_size: int,
) -> tuple[list[Transaction], int]:
    query = db.query(Transaction)

    if current_user.role != Role.admin:
        query = query.filter(Transaction.user_id == current_user.id)

    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if from_date:
        query = query.filter(Transaction.transaction_date >= from_date)
    if to_date:
        query = query.filter(Transaction.transaction_date <= to_date)

    total = query.with_entities(func.count()).scalar()
    total = db.query(func.count()).select_from(query.subquery()).scalar()
    results = (
        query.order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return results, total


def get_transaction_by_id(
    db: Session, transaction_id: int, current_user: User
) -> Transaction | None:
    query = db.query(Transaction).filter(Transaction.id == transaction_id)
    if current_user.role != Role.admin:
        query = query.filter(Transaction.user_id == current_user.id)
    return query.first()


def create_transaction(
    db: Session, data: TransactionCreate, user_id: int
) -> Transaction:
    transaction = Transaction(**data.model_dump(), user_id=user_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(
    db: Session, transaction: Transaction, data: TransactionUpdate
) -> Transaction:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()
