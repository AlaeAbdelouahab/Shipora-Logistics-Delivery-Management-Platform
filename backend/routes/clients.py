from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Commande

router = APIRouter()

@router.get("/tracking/{code_tracking}")
async def track_order(code_tracking: str, db: Session = Depends(get_db)):
    """Track order by code (public endpoint)"""
    commande = db.query(Commande).filter(
        Commande.code_tracking == code_tracking
    ).first()
    
    if not commande:
        raise HTTPException(status_code=404, detail="Order not found")
    
    livraison = commande.livraison if commande.livraison else None
    
    return {
        "id": commande.id,
        "code_tracking": commande.code_tracking,
        "adresse": commande.adresse,
        "statut": commande.statut,
        "date_creation": commande.date_creation,
        "livraison": {
            "date_planifiee": livraison.date_planifiee if livraison else None,
            "statut": livraison.statut if livraison else None
        } if livraison else None
    }
