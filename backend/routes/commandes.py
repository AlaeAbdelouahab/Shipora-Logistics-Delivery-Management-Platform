from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User, Commande, DeliveryStatus, UserRole
from schemas import CommandeResponse, CommandeCreate, CommandeUpdate
from dependencies import get_current_user, check_role
import pandas as pd
import uuid
from geopy.geocoders import Nominatim
import io

router = APIRouter()

geolocator = Nominatim(user_agent="logistics_app")

@router.post("/import_excel")
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE]))
):
    """Import commandes from Excel file"""
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ["id_commande", "adresse", "poids"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")
        
        imported = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if already exists
                existing = db.query(Commande).filter(Commande.id_commande == row["id_commande"]).first()
                if existing:
                    errors.append(f"Row {index}: Commande {row['id_commande']} already exists")
                    continue
                
                # Geocode address
                try:
                    location = geolocator.geocode(row["adresse"], timeout=10)
                    if not location:
                        errors.append(f"Row {index}: Address not found: {row['adresse']}")
                        continue
                    latitude, longitude = location.latitude, location.longitude
                except Exception as e:
                    errors.append(f"Row {index}: Geocoding error: {str(e)}")
                    continue
                
                # Create commande
                commande = Commande(
                    id_commande=str(row["id_commande"]),
                    adresse=row["adresse"],
                    latitude=latitude,
                    longitude=longitude,
                    poids=float(row["poids"]),
                    depot_id=current_user.depot_id,
                    code_tracking=str(uuid.uuid4())[:8].upper()
                )
                db.add(commande)
                imported += 1
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
        
        db.commit()
        return {"success": True, "imported": imported, "errors": errors}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[CommandeResponse])
async def list_commandes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List commandes for user's depot"""
    commandes = db.query(Commande).filter(Commande.depot_id == current_user.depot_id).all()
    return commandes


@router.post("/", response_model=CommandeResponse)
async def create_commande(
    commande_data: CommandeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.GESTIONNAIRE, UserRole.ADMIN]))
):
    """Create a new commande"""
    commande = Commande(
        id_commande=commande_data.id_commande,
        adresse=commande_data.adresse,
        latitude=commande_data.latitude,
        longitude=commande_data.longitude,
        poids=commande_data.poids,
        depot_id=current_user.depot_id,
        code_tracking=str(uuid.uuid4())[:8].upper()
    )
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande

@router.put("/{commande_id}", response_model=CommandeResponse)
async def update_commande(
    commande_id: int,
    commande_data: CommandeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.GESTIONNAIRE, UserRole.ADMIN]))
):
    """Update commande (only if not delivered)"""
    commande = db.query(Commande).filter(Commande.id == commande_id).first()
    if not commande:
        raise HTTPException(status_code=404, detail="Commande not found")
    
    if commande.statut in [DeliveryStatus.LIVREE, DeliveryStatus.ANNULEE]:
        raise HTTPException(status_code=400, detail="Cannot modify delivered or cancelled orders")
    
    for field, value in commande_data.dict(exclude_unset=True).items():
        setattr(commande, field, value)
    
    db.commit()
    db.refresh(commande)
    return commande


