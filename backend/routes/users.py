from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole
from schemas import UserResponse, UserCreate, UserUpdate
from dependencies import get_current_user, check_role

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN]))
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user
