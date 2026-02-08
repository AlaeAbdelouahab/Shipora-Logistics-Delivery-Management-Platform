from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Commande, Livraison, DeliveryStatus
from dependencies import get_current_user, check_role
from models import UserRole

router = APIRouter()

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    
    # Filter by depot
    commandes_total = db.query(Commande).filter(
        Commande.depot_id == current_user.depot_id
    ).count()
    
    commandes_livrees = db.query(Commande).filter(
        Commande.depot_id == current_user.depot_id,
        Commande.statut == DeliveryStatus.LIVREE
    ).count()
    
    commandes_en_attente = db.query(Commande).filter(
        Commande.depot_id == current_user.depot_id,
        Commande.statut == DeliveryStatus.EN_ATTENTE
    ).count()
    
    commandes_en_cours = db.query(Commande).filter(
        Commande.depot_id == current_user.depot_id,
        Commande.statut.in_([
            DeliveryStatus.PREPARATION
        ])
    ).count()
    
    livreurs_actifs = db.query(User).filter(
        User.depot_id == current_user.depot_id,
        User.role == UserRole.LIVREUR,
        User.actif == True
    ).count()
    
    return {
        "total_commandes": commandes_total,
        "commandes_livrees": commandes_livrees,
        "commandes_en_attente": commandes_en_attente,
        "commandes_en_cours": commandes_en_cours,  
        "livreurs_actifs": livreurs_actifs,
        "taux_livraison": (commandes_livrees / commandes_total * 100) if commandes_total > 0 else 0
    }

@router.get("/performance")
async def get_performance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance metrics by driver"""
    
    livreurs = db.query(User).filter(
        User.depot_id == current_user.depot_id,
        User.role == UserRole.LIVREUR
    ).all()
    
    performance = []
    for livreur in livreurs:
        total_livraisons = db.query(Livraison).filter(
            Livraison.livreur_id == livreur.id
        ).count()
        
        livraisons_completes = db.query(Livraison).filter(
            Livraison.livreur_id == livreur.id,
            Livraison.statut == DeliveryStatus.LIVREE
        ).count()
        
        performance.append({
            "livreur_id": livreur.id,
            "livreur_nom": f"{livreur.prenom} {livreur.nom}",
            "total": total_livraisons,
            "completees": livraisons_completes,
            "taux": (livraisons_completes / total_livraisons * 100) if total_livraisons > 0 else 0
        })
    
    return performance