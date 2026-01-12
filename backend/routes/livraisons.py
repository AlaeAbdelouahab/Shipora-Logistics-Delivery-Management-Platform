from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Livraison, Commande, DeliveryStatus, UserRole
from schemas import LivraisonResponse, LivraisonCreate, LivraisonUpdate
from dependencies import get_current_user, check_role
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[LivraisonResponse])
async def list_livraisons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List livraisons (filtered by depot for gestionnaire, own for livreur)"""
    if current_user.role == UserRole.LIVREUR:
        livraisons = db.query(Livraison).filter(Livraison.livreur_id == current_user.id).all()
    else:
        livraisons = db.query(Livraison).join(Commande).filter(
            Commande.depot_id == current_user.depot_id
        ).all()
    return livraisons

@router.post("/", response_model=LivraisonResponse)
async def create_livraison(
    livraison_data: LivraisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE]))
):
    """Create a new livraison"""
    livraison = Livraison(**livraison_data.dict())
    db.add(livraison)
    db.commit()
    db.refresh(livraison)
    return livraison

@router.put("/{livraison_id}", response_model=LivraisonResponse)
async def update_livraison(
    livraison_id: int,
    livraison_data: LivraisonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update livraison status (livreur can update own deliveries)"""
    livraison = db.query(Livraison).filter(Livraison.id == livraison_id).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")
    
    if current_user.role == UserRole.LIVREUR and livraison.livreur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for field, value in livraison_data.dict(exclude_unset=True).items():
        setattr(livraison, field, value)
    
    # Update associated commande status
    if livraison_data.statut:
        commande = db.query(Commande).filter(Commande.id == livraison.commande_id).first()
        if commande:
            commande.statut = livraison_data.statut
    
    db.commit()
    db.refresh(livraison)
    return livraison
