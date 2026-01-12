from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role, "depot_id": user.depot_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "depot_id": user.depot_id
    }

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Admin registration endpoint for new users"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.mot_de_passe)
    db_user = User(
        email=user_data.email,
        nom=user_data.nom,
        prenom=user_data.prenom,
        mot_de_passe_hash=hashed_password,
        role=user_data.role,
        depot_id=user_data.depot_id,
        phone=user_data.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
