from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Incident, Commande, IncidentType, DeliveryStatus, UserRole
from schemas import IncidentCreate, IncidentResponse
from dependencies import get_current_user, check_role
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new incident"""
    
    # Verify commande exists
    commande = db.query(Commande).filter(Commande.id == incident_data.commande_id).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")
    
    # Check if user has access to this commande
    if current_user.role == UserRole.LIVREUR:
        livraison = commande.livraison
        if not livraison or livraison.livreur_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role in [UserRole.GESTIONNAIRE, UserRole.ADMIN]:
        if commande.depot_id != current_user.depot_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    incident = Incident(**incident_data.dict())
    db.add(incident)
    
    # Update commande status based on incident type
    if incident_data.type_incident == IncidentType.ANNULATION_CLIENT:
        commande.statut = DeliveryStatus.ANNULEE
    
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List incidents for user's depot"""
    
    if current_user.role == UserRole.LIVREUR:
        # Livreurs see incidents related to their deliveries
        incidents = db.query(Incident).join(Commande).join(
            Livraison, Commande.id == Livraison.commande_id
        ).filter(Livraison.livreur_id == current_user.id).all()
    else:
        # Gestionnaires and Admins see incidents for their depot
        incidents = db.query(Incident).join(Commande).filter(
            Commande.depot_id == current_user.depot_id
        ).all()
    
    return incidents

@router.put("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE]))
):
    """Mark incident as resolved"""
    
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Verify access
    commande = incident.commande
    if commande.depot_id != current_user.depot_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    incident.resolu = True
    incident.date_resolution = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident
