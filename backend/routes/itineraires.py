from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Livraison, Commande, Itineraire, DeliveryStatus, UserRole, Depot
from schemas import ItineraireResponse
from dependencies import get_current_user, check_role
from datetime import datetime, timedelta
from optimization import RouteOptimizer
import requests
import json
from notifications import notification_service

router = APIRouter()

# Placeholder for OSRM API
OSRM_URL = "http://router.project-osrm.org"

def get_distance_matrix(coordinates: list) -> list:
    """Get distance matrix from OSRM"""
    # Format: lon,lat;lon,lat;...
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    url = f"{OSRM_URL}/table/v1/driving/{coords_str}"
    
    try:
        response = requests.get(url, params={"annotations": "distance,duration"})
        data = response.json()
        if data.get("code") == "Ok":
            return data.get("distances", [])
    except Exception as e:
        print(f"OSRM error: {e}")
    
    return None

@router.post("/optimize")
async def optimize_routes(
    depot_id: int = Query(...),
    date_planifiee: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE]))
):
    """Optimize routes for deliveries using OR-Tools"""
    
    # Verify depot ownership
    if current_user.role == UserRole.GESTIONNAIRE and current_user.depot_id != depot_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get depot
    depot = db.query(Depot).filter(Depot.id == depot_id).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")
    
    # Get pending commandes for depot
    commandes = db.query(Commande).filter(
        Commande.depot_id == depot_id,
        Commande.statut == DeliveryStatus.EN_ATTENTE
    ).all()
    
    if not commandes:
        raise HTTPException(status_code=400, detail="No pending commandes")
    
    # Get available drivers
    livreurs = db.query(User).filter(
        User.depot_id == depot_id,
        User.role == UserRole.LIVREUR,
        User.actif == True
    ).all()
    
    if not livreurs:
        raise HTTPException(status_code=400, detail="No available drivers")
    
    try:
        # Prepare data for optimizer
        commandes_data = [
            {
                "id": c.id,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "poids": c.poids,
                "service_time_minutes": 10
            }
            for c in commandes
        ]
        
        drivers_data = [
            {
                "id": l.id,
                "capacity_kg": 100  # Default capacity
            }
            for l in livreurs
        ]
        
        # Run optimizer
        optimizer = RouteOptimizer()
        result = optimizer.optimize(
            commandes=commandes_data,
            drivers=drivers_data,
            depot_coords=(depot.latitude, depot.longitude),
            planning_date=date_planifiee
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Save optimized routes to database
        from datetime import datetime as dt
        planning_dt = dt.fromisoformat(date_planifiee)
        
        for route in result["routes"]:
            # Create itinerary record
            itineraire = Itineraire(
                date_planifiee=planning_dt,
                depot_id=depot_id,
                livreur_id=route["driver_id"],
                distance_totale=route["distance_m"] / 1000,  # Convert to km
                temps_total=route["time_s"],
                commandes_count=route["commandes_count"],
                optimise=True,
                metadonnees=json.dumps(route)
            )
            db.add(itineraire)
            
            # Update livraisons with optimized sequence
            for commande_info in route["commandes"]:
                livraison = db.query(Livraison).join(Commande).filter(
                    Commande.id == commande_info["commande_id"],
                    Livraison.livreur_id == route["driver_id"]
                ).first()
                
                if livraison:
                    livraison.ordre_visite = commande_info["order"]
                else:
                    # Create new livraison if not exists
                    commande = db.query(Commande).filter(
                        Commande.id == commande_info["commande_id"]
                    ).first()
                    
                    livraison = Livraison(
                        commande_id=commande_info["commande_id"],
                        livreur_id=route["driver_id"],
                        date_planifiee=planning_dt,
                        ordre_visite=commande_info["order"],
                        statut=DeliveryStatus.PREPARATION
                    )
                    db.add(livraison)
                    commande.statut = DeliveryStatus.PREPARATION
        
        db.commit()
        
        # After saving routes, send notifications
        for route in result["routes"]:
            driver = db.query(User).filter(User.id == route["driver_id"]).first()
            if driver and driver.email:
                subject = f"Nouvel itinéraire - {date_planifiee}"
                html_content = notification_service.get_route_assigned_template(
                    driver.prenom,
                    route["commandes_count"],
                    date_planifiee
                )
                await notification_service.send_email(driver.email, subject, html_content)
        
        return {
            "success": True,
            "routes": result["routes"],
            "total_distance_km": result["total_distance_m"] / 1000,
            "total_time_hours": result["total_time_s"] / 3600,
            "total_vehicles_used": result["total_vehicles_used"],
            "message": f"Routes optimized for {result['total_vehicles_used']} drivers"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@router.get("/", response_model=list[ItineraireResponse])
async def list_itineraires(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_filter: str = Query(None)
):
    """List itineraires for depot (optionally filtered by date)"""
    
    query = db.query(Itineraire).filter(Itineraire.depot_id == current_user.depot_id)
    
    if date_filter:
        from datetime import datetime as dt
        date = dt.fromisoformat(date_filter)
        query = query.filter(
            Itineraire.date_planifiee >= date,
            Itineraire.date_planifiee < dt(date.year, date.month, date.day) + timedelta(days=1)
        )
    
    itineraires = query.all()
    return itineraires

@router.get("/{itineraire_id}", response_model=ItineraireResponse)
async def get_itineraire(
    itineraire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get itineraire details"""
    
    itineraire = db.query(Itineraire).filter(Itineraire.id == itineraire_id).first()
    if not itineraire:
        raise HTTPException(status_code=404, detail="Itineraire not found")
    
    if itineraire.depot_id != current_user.depot_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return itineraire
