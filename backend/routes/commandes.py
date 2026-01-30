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
from notifications import notification_service

router = APIRouter()

geolocator = Nominatim(user_agent="logistics_app")

@router.post("/import_excel")
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE]))
):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        required_columns = ["id_commande", "adresse", "poids", "client_email"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

        imported = 0
        errors = []
        emails_to_send = []  # (email, subject, html)

        for index, row in df.iterrows():
            try:
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

                tracking_code = str(uuid.uuid4())[:8].upper()
                client_email = str(row["client_email"]).strip() if row["client_email"] else ""

                commande = Commande(
                    id_commande=str(row["id_commande"]),
                    adresse=row["adresse"],
                    latitude=latitude,
                    longitude=longitude,
                    poids=float(row["poids"]),
                    depot_id=current_user.depot_id,
                    code_tracking=tracking_code,
                    client_email=client_email if client_email else None
                )
                db.add(commande)
                imported += 1

                if client_email:
                    subject = f"Code de suivi - Commande {commande.id_commande}"
                    html_content = notification_service.get_tracking_code_template(
                        id_commande=commande.id_commande,
                        tracking_code=tracking_code
                    )
                    emails_to_send.append((client_email, subject, html_content))

            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")

        db.commit()

        # Send emails AFTER commit
        for to_email, subject, html_content in emails_to_send:
            await notification_service.send_email(to_email, subject, html_content)

        return {
            "success": True,
            "imported": imported,
            "emails_sent": len(emails_to_send),
            "errors": errors
        }

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


