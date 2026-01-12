from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import UserRole, DeliveryStatus, IncidentType

# ============= USER SCHEMAS =============
class UserBase(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    role: UserRole
    depot_id: int
    phone: Optional[str] = None

class UserCreate(UserBase):
    mot_de_passe: str

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    phone: Optional[str] = None
    actif: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    actif: bool
    date_creation: datetime
    
    class Config:
        from_attributes = True

# ============= DEPOT SCHEMAS =============
class DepotBase(BaseModel):
    nom: str
    adresse: str
    latitude: float
    longitude: float
    capacite_max: float

class DepotCreate(DepotBase):
    pass

class DepotResponse(DepotBase):
    id: int
    date_creation: datetime
    
    class Config:
        from_attributes = True

# ============= COMMANDE SCHEMAS =============
class CommandeBase(BaseModel):
    adresse: str
    latitude: float
    longitude: float
    poids: float
    notes: Optional[str] = None

class CommandeCreate(CommandeBase):
    id_commande: str

class CommandeUpdate(BaseModel):
    adresse: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

class CommandeResponse(CommandeBase):
    id: int
    id_commande: str
    statut: DeliveryStatus
    code_tracking: str
    date_creation: datetime
    
    class Config:
        from_attributes = True

# ============= LIVRAISON SCHEMAS =============
class LivraisonBase(BaseModel):
    commande_id: int
    livreur_id: int
    date_planifiee: datetime
    temps_service: int = 10

class LivraisonCreate(LivraisonBase):
    pass

class LivraisonUpdate(BaseModel):
    statut: Optional[DeliveryStatus] = None
    date_livraison: Optional[datetime] = None

class LivraisonResponse(LivraisonBase):
    id: int
    statut: DeliveryStatus
    ordre_visite: Optional[int]
    
    class Config:
        from_attributes = True

# ============= INCIDENT SCHEMAS =============
class IncidentBase(BaseModel):
    type_incident: IncidentType
    description: str

class IncidentCreate(IncidentBase):
    commande_id: int

class IncidentResponse(IncidentBase):
    id: int
    commande_id: int
    date_incident: datetime
    resolu: bool
    
    class Config:
        from_attributes = True

# ============= ITINERAIRE SCHEMAS =============
class ItineraireResponse(BaseModel):
    id: int
    date_planifiee: datetime
    livreur_id: int
    distance_totale: float
    temps_total: int
    commandes_count: int
    optimise: bool
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: UserRole
    depot_id: int
