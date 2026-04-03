import random
from datetime import date, timedelta

from app.database import SessionLocal
from app.models.transaction import Transaction, TransactionType
from app.models.user import Role, User
from app.services.auth_service import hash_password

USERS = [
    {"email": "admin@finance.dev", "password": "admin123", "role": Role.admin},
    {"email": "analyst@finance.dev", "password": "analyst123", "role": Role.analyst},
    {"email": "viewer@finance.dev", "password": "viewer123", "role": Role.viewer},
]

INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Bonus", "Rental"]
EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Rent",
]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def seed():
    db = SessionLocal()

    existing = db.query(User).filter(User.email == USERS[0]["email"]).first()
    if existing:
        print("Database already seeded.")
        db.close()
        return

    users = []
    for u in USERS:
        user = User(
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        users.append(user)

    db.commit()
    for u in users:
        db.refresh(u)

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    transactions = []
    for user in users:
        for _ in range(40):
            tx_type = random.choice(list(TransactionType))
            category = random.choice(
                INCOME_CATEGORIES
                if tx_type == TransactionType.income
                else EXPENSE_CATEGORIES
            )
            amount = round(random.uniform(100, 5000), 2)
            transactions.append(
                Transaction(
                    user_id=user.id,
                    amount=amount,
                    type=tx_type,
                    category=category,
                    date=random_date(start_date, end_date),
                    notes=f"Seeded transaction for {category}",
                )
            )

    db.add_all(transactions)
    db.commit()
    db.close()

    print(f"Seeded {len(users)} users and {len(transactions)} transactions.")
    print("\nCredentials:")
    for u in USERS:
        print(f"  {u['role'].value:10s}  {u['email']}  /  {u['password']}")


if __name__ == "__main__":
    seed()
