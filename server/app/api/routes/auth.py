from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_user_service
from app.core.security import create_access_token, get_current_user
from app.schemas.users import UserCreate, UserOut, Token
from app.services.user_service import UserService

router = APIRouter()

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Create a new user account.
    """
    print('payload ', payload)
    user = user_service.create_user(email=payload.email, password=payload.password)
     # Auto-login: create and return token immediately
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Authenticate user and return a JWT access token.
    """
    user = user_service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.post("/logout")
async def logout() -> dict:
    """
    Stateless JWT: logout is handled client-side by discarding the token.
    This endpoint exists for symmetry and future token blacklist support.
    """
    return {"message": "Logged out. Please discard the token on the client."}


@router.get("/me", response_model=UserOut)
async def read_me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """
    Get the currently authenticated user.
    """
    return current_user


