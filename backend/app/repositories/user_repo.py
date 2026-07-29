"""User repository — database operations for users."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    """Find a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id: UUID) -> User | None:
    """Find a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create(db: Session, user: User) -> User:
    """Create a new user."""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User) -> User:
    """Update an existing user."""
    db.commit()
    db.refresh(user)
    return user
