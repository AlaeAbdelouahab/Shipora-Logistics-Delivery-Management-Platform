# routes/itineraires.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Commande, Itineraire, DeliveryStatus, UserRole, Depot, Livraison
from schemas import ItineraireResponse
from dependencies import get_current_user, check_role
from datetime import datetime, timedelta, date as date_cls
from typing import Any, Dict, List, Optional
import json
from scheduler import optimization_scheduler


router = APIRouter()

from optimization import RouteOptimizer

@router.post("/debug-optimization")
async def debug_optimization(
    depot_id: int,
    db: Session = Depends(get_db),
):
    depot = db.query(Depot).filter(Depot.id == depot_id).first()
    if not depot:
        return {"ok": False, "error": f"Depot {depot_id} not found"}

    commandes = db.query(Commande).filter(
        Commande.depot_id == depot.id,
        Commande.statut == DeliveryStatus.EN_ATTENTE
    ).all()

    drivers = db.query(User).filter(
        User.depot_id == depot.id,
        User.role == UserRole.LIVREUR,
        User.actif == True
    ).all()

    commandes_data = [
        {
            "id": c.id,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "poids": c.poids,
            "service_time_minutes": 10,
            "created_at": c.date_creation.isoformat()
        }
        for c in commandes
    ]

    drivers_data = [
        {
            "id": d.id,
            "email": d.email,
            "name": f"{d.prenom} {d.nom}",
            "capacity_kg": 100
        }
        for d in drivers
    ]

    optimizer = RouteOptimizer()
    result = optimizer.optimize(
        commandes=commandes_data,
        drivers=drivers_data,
        depot_coords=(depot.latitude, depot.longitude),
        planning_date=datetime.now().date().isoformat(),
    )
    total_poids = sum(float(c.poids or 0) for c in commandes)
    total_capacity = len(drivers) * 100

    return {
        "ok": True,
        "depot": {"id": depot.id, "nom": depot.nom, "lat": depot.latitude, "lon": depot.longitude},
        "counts": {
            "commandes_en_attente": len(commandes),
            "drivers_actifs": len(drivers),
        },
        "debug_stats": {
            "total_poids": total_poids,
            "total_capacity_assumed": total_capacity,
            "units_hint": "poids and capacity are assumed in KG here"
        },
        "optimizer_result": result,
    }

@router.post("/run-optimization-now")
async def run_optimization_now():
    try:
        await optimization_scheduler.daily_optimization()
        return {"ok": True, "message": "Optimization finished (check logs for details)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
def parse_date_filter(date_filter: str) -> datetime:
    """Parse ISO date or datetime string into naive datetime."""
    s = (date_filter or "").strip()
    if not s:
        raise ValueError("date_filter is required")

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            dt = dt.astimezone(tz=None).replace(tzinfo=None)
        return dt
    except Exception:
        d = date_cls.fromisoformat(s[:10])
        return datetime(d.year, d.month, d.day)


def operational_target_date(now: datetime) -> date_cls:
    """
    Fenêtre opérationnelle:
    - si maintenant >= 21:00 -> target = demain
    - sinon -> target = aujourd'hui
    """
    return (now + timedelta(days=1)).date() if now.hour >= 21 else now.date()


@router.get("/")
async def list_itineraires(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now()
    target = operational_target_date(now)

    start = datetime(target.year, target.month, target.day, 0, 0, 0)
    end = start + timedelta(days=1)

    itineraires = (
        db.query(Itineraire)
        .filter(Itineraire.depot_id == current_user.depot_id)
        .filter(Itineraire.date_planifiee >= start, Itineraire.date_planifiee < end)
        .all()
    )

    depots = (db.query(Depot).filter(Depot.id == current_user.depot_id).all())

    routes: List[Dict[str, Any]] = []
    itineraires_payload: List[Dict[str, Any]] = []

    for it in itineraires:
        meta = it.metadonnees or {}

        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}

        meta_commandes = meta.get("commandes") or []

        commande_ids = [
            c.get("commande_id") for c in meta_commandes
            if isinstance(c, dict) and c.get("commande_id") is not None
        ]

        commandes_db: Dict[int, Commande] = {}
        if commande_ids:
            rows = db.query(Commande).filter(Commande.id.in_(commande_ids)).all()
            commandes_db = {c.id: c for c in rows}

        commandes_for_route: List[Dict[str, Any]] = []
        for c in sorted(meta_commandes, key=lambda x: (x.get("order", 999999) if isinstance(x, dict) else 999999)):
            if not isinstance(c, dict):
                continue

            cid = c.get("commande_id")
            cdb = commandes_db.get(cid)

            lat = cdb.latitude if (cdb and cdb.latitude is not None) else c.get("lat")
            lon = cdb.longitude if (cdb and cdb.longitude is not None) else c.get("lon")

            commandes_for_route.append({
                "commande_id": cid,
                "order": c.get("order"),
                "lat": lat,
                "lon": lon,

                # extras (pour UI)
                "id_commande": (cdb.id_commande if cdb else None),
                "adresse": (cdb.adresse if cdb else None),
                "statut": (cdb.statut.value if cdb and cdb.statut else None),
                "poids": (cdb.poids if cdb else None),
                "client_email": (cdb.client_email if cdb else None),
                "code_tracking": (cdb.code_tracking if cdb else None),
            })
        

        route_obj = {
            "itineraire_id": it.id,
            "driver_id": it.livreur_id,
            "commandes": commandes_for_route,
            "distance_m": int((it.distance_totale or 0) * 1000),  # km -> m
            "time_s": int((it.temps_total or 0) * 60),            # minutes -> seconds
            "commandes_count": it.commandes_count or len(commandes_for_route),
            "date_planifiee": it.date_planifiee.isoformat() if it.date_planifiee else None,
            "optimise": it.optimise,
            "created_at": it.date_creation.isoformat() if it.date_creation else None,
        }
        routes.append(route_obj)

        itineraires_payload.append({
            "id": it.id,
            "date_planifiee": it.date_planifiee.isoformat() if it.date_planifiee else None,
            "depot_id": it.depot_id,
            "livreur_id": it.livreur_id,
            "distance_totale": it.distance_totale,
            "temps_total": it.temps_total,
            "commandes_count": it.commandes_count,
            "optimise": it.optimise,
            "date_creation": it.date_creation.isoformat() if it.date_creation else None,
        })

    return {
        "target_day": target.isoformat(),
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "routes": routes,
        "itineraires": itineraires_payload,
        "depot": {
            "id": depots[0].id,
            "nom": depots[0].nom,
            "adresse": depots[0].adresse,
            "lat": depots[0].latitude,
            "lon": depots[0].longitude,
        } if depots else None,
    }


@router.get("/unscheduled", response_model=list)
async def get_unscheduled_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(check_role([UserRole.ADMIN, UserRole.GESTIONNAIRE])),
):
    depot_id = current_user.depot_id if current_user.role == UserRole.GESTIONNAIRE else None

    query = db.query(Commande).filter(Commande.statut == DeliveryStatus.EN_ATTENTE)
    if depot_id:
        query = query.filter(Commande.depot_id == depot_id)

    unscheduled = query.all()

    return [
        {
            "id": c.id,
            "id_commande": c.id_commande,
            "adresse": c.adresse,
            "poids": c.poids,
            "code_tracking": c.code_tracking,
            "date_creation": c.date_creation.isoformat(),
        }
        for c in unscheduled
    ]

@router.get("/livreur-itineraire")
async def get_livreur_itineraire(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now()
    target = operational_target_date(now)

    start = datetime(target.year, target.month, target.day)
    end = start + timedelta(days=1)

    # 🔒 UN SEUL itinéraire (le plus récent)
    it = (
        db.query(Itineraire)
        .filter(Itineraire.depot_id == current_user.depot_id)
        .filter(Itineraire.livreur_id == current_user.id)
        .filter(Itineraire.date_planifiee >= start, Itineraire.date_planifiee < end)
        .order_by(Itineraire.date_creation.desc())
        .first()
    )

    if not it:
        return {
            "itineraire": None,
            "route": None,
            "depot": None,
        }

    # 🔹 depot
    depot = db.query(Depot).filter(Depot.id == current_user.depot_id).first()

    # 🔹 meta
    meta = it.metadonnees or {}
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}

    meta_commandes = meta.get("commandes", [])

    commande_ids = [
        c["commande_id"]
        for c in meta_commandes
        if isinstance(c, dict) and "commande_id" in c
    ]

    commandes_db = {}
    if commande_ids:
        rows = db.query(Commande).filter(Commande.id.in_(commande_ids)).all()
        commandes_db = {c.id: c for c in rows}

    commandes = []
    for c in sorted(meta_commandes, key=lambda x: x.get("order", 999999)):
        cdb = commandes_db.get(c["commande_id"])
        
        # ✅ Récupérer la livraison pour avoir son ID
        livraison = db.query(Livraison).filter(
            Livraison.commande_id == c["commande_id"],
            Livraison.livreur_id == current_user.id
        ).first()

        commandes.append({
            "commande_id": c["commande_id"],
            "livraison_id": livraison.id if livraison else None,  # ✅ AJOUT
            "order": c.get("order"),
            "lat": cdb.latitude if cdb and cdb.latitude else c.get("lat"),
            "lon": cdb.longitude if cdb and cdb.longitude else c.get("lon"),
            "adresse": cdb.adresse if cdb else None,
            "statut": cdb.statut.value if cdb and cdb.statut else None,
            "poids": cdb.poids if cdb else None,
            "code_tracking": cdb.code_tracking if cdb else None,
        })

    return {
        "itineraire": {
            "id": it.id,
            "date_planifiee": it.date_planifiee.isoformat(),
            "distance_m": int((it.distance_totale or 0) * 1000),
            "time_s": int((it.temps_total or 0) * 60),
            "commandes_count": it.commandes_count,
            "optimise": it.optimise,
            "created_at": it.date_creation.isoformat(),
        },
        "route": {
            "driver_id": it.livreur_id,
            "commandes": commandes,
        },
        "depot": {
            "id": depot.id,
            "nom": depot.nom,
            "adresse": depot.adresse,
            "lat": depot.latitude,
            "lon": depot.longitude,
        } if depot else None,
    }

@router.get("/{itineraire_id}", response_model=ItineraireResponse)
async def get_itineraire(
    itineraire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("🔥 DÉBUT ENDPOINT") 
    print(f"🔥 DÉBUT ENDPOINT - User: {current_user.id}, Role: {current_user.role}")
    itineraire = db.query(Itineraire).filter(Itineraire.id == itineraire_id).first()
    if not itineraire:
        raise HTTPException(status_code=404, detail="Itineraire not found")

    if itineraire.depot_id != current_user.depot_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return itineraire


