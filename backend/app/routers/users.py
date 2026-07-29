"""Users router — profile search and user lookup endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.transfer import UserSearchResult

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=list[UserSearchResult])
def search_users(
    q: str = Query(..., min_length=2, description="Email query string"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for users by email (excluding the current user)."""
    users = (
        db.query(User)
        .filter(
            User.email.ilike(f"%{q}%"),
            User.id != current_user.id,
        )
        .limit(10)
        .all()
    )
    return [
        UserSearchResult(
            id=str(u.id),
            email=u.email,
            display_name=u.display_name,
            default_currency=u.default_currency,
        )
        for u in users
    ]
