"""Auth router — signup, login, and token refresh endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.currencies import is_valid_currency
from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import DuplicateWalletError
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.services.wallet_service import create_wallet

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user and create their default wallet."""

    # Validate currency
    if not is_valid_currency(request.default_currency):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported currency: {request.default_currency}",
        )

    # Check for duplicate email
    existing = user_repo.get_by_email(db, request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        display_name=request.display_name,
        default_currency=request.default_currency.upper(),
    )
    user = user_repo.create(db, user)

    # Create default wallet in user's preferred currency
    create_wallet(db, user.id, user.default_currency)

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT tokens."""

    user = user_repo.get_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for new access + refresh tokens."""

    user_id = verify_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify user still exists
    from uuid import UUID

    user = user_repo.get_by_id(db, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        default_currency=current_user.default_currency,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile."""
    if request.default_currency is not None:
        if not is_valid_currency(request.default_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported currency: {request.default_currency}",
            )
        # Create wallet if it doesn't exist
        try:
            create_wallet(db, current_user.id, request.default_currency.upper())
        except DuplicateWalletError:
            pass  # Wallet already exists
        current_user.default_currency = request.default_currency.upper()

    if request.photo_url is not None:
        current_user.photo_url = request.photo_url

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        default_currency=current_user.default_currency,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/profile/upload", response_model=UserResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a profile photo."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # In production this would go to S3. Here we save locally to uploads/avatars/
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}.{ext}"
    file_path = f"uploads/avatars/{filename}"
    
    # Read the file contents
    contents = await file.read()
    
    # Write to local file
    with open(file_path, "wb") as f:  # noqa: ASYNC230
        f.write(contents)
        
    # Construct relative URL so frontend can prepend the backend URL
    photo_url = f"/uploads/avatars/{filename}"
    current_user.photo_url = photo_url
    
    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        default_currency=current_user.default_currency,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at.isoformat(),
    )
