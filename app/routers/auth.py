# app/routers/auth.py
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

# Lazy imports - these will be imported inside functions
def get_db_dep():
    from app.database import get_db
    return get_db

def get_user_model():
    from app.models.user import User
    return User

def get_schemas():
    from app.schemas.auth import Token, UserCreate, User as UserSchema
    return Token, UserCreate, UserSchema

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_TO_A_SECURE_RANDOM_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    User = get_user_model()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/register", response_model=lambda: get_schemas()[2])
def register(user_data, db: Session = Depends(get_db_dep)):
    """Register a new user."""
    User = get_user_model()
    Token, UserCreate, UserSchema = get_schemas()
    
    # Convert user_data if it's a dict
    if hasattr(user_data, 'email'):
        email = user_data.email
        password = user_data.password
        full_name = user_data.full_name
    else:
        email = user_data.get('email')
        password = user_data.get('password')
        full_name = user_data.get('full_name')
    
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Auto-create a default personal calendar
    from app.models.calendar import Calendar
    default_calendar = Calendar(
        name="Personal",
        description="Default personal calendar",
        calendar_type="personal",
        owner_id=db_user.id
    )
    db.add(default_calendar)
    db.commit()

    return db_user


@router.post("/login", response_model=lambda: get_schemas()[0])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_dep)
):
    """Login and get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    Token, UserCreate, UserSchema = get_schemas()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_dep)
):
    """Dependency to get the current authenticated user from JWT token."""
    User = get_user_model()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user