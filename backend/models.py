from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    GESTIONNAIRE = "gestionnaire"
    LIVREUR = "livreur"
    CLIENT = "client"

class DeliveryStatus(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    PREPARATION = "preparation"
    EN_TRANSIT = "en_transit"
    LIVREE = "livree"
    ANNULEE = "annulee"

class IncidentType(str, enum.Enum):
    ADRESSE_INVALIDE = "adresse_invalide"
    CLIENT_ABSENT = "client_absent"
    REFUS_LIVRAISON = "refus_livraison"
    COLIS_ENDOMMAGE = "colis_endommage"
    ANNULATION_CLIENT = "annulation_client"
    AUTRE = "autre"

# ============= USERS =============
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    mot_de_passe_hash = Column(String)
    role = Column(Enum(UserRole))
    actif = Column(Boolean, default=True)
    depot_id = Column(Integer, ForeignKey("depots.id"))
    phone = Column(String, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    depot = relationship("Depot", back_populates="users")
    livraisons = relationship("Livraison", back_populates="livreur")

# ============= DEPOTS =============
class Depot(Base):
    __tablename__ = "depots"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    adresse = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    capacite_max = Column(Float)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="depot")
    commandes = relationship("Commande", back_populates="depot")

# ============= COMMANDES =============
class Commande(Base):
    __tablename__ = "commandes"
    
    id = Column(Integer, primary_key=True, index=True)
    id_commande = Column(String, unique=True, index=True)
    adresse = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    poids = Column(Float)
    statut = Column(Enum(DeliveryStatus), default=DeliveryStatus.EN_ATTENTE)
    depot_id = Column(Integer, ForeignKey("depots.id"))
    client_email = Column(String, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    code_tracking = Column(String, unique=True, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    depot = relationship("Depot", back_populates="commandes")
    livraison = relationship("Livraison", uselist=False, back_populates="commande")
    incidents = relationship("Incident", back_populates="commande")

# ============= LIVRAISONS =============
class Livraison(Base):
    __tablename__ = "livraisons"
    
    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id"))
    livreur_id = Column(Integer, ForeignKey("users.id"))
    date_planifiee = Column(DateTime)
    date_livraison = Column(DateTime, nullable=True)
    statut = Column(Enum(DeliveryStatus), default=DeliveryStatus.EN_ATTENTE)
    ordre_visite = Column(Integer, nullable=True)
    temps_service = Column(Integer, default=10)  # en minutes
    
    # Relationships
    commande = relationship("Commande", back_populates="livraison")
    livreur = relationship("User", back_populates="livraisons")

# ============= INCIDENTS =============
class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id"))
    type_incident = Column(Enum(IncidentType))
    description = Column(Text)
    date_incident = Column(DateTime, default=datetime.utcnow)
    resolu = Column(Boolean, default=False)
    date_resolution = Column(DateTime, nullable=True)
    
    # Relationships
    commande = relationship("Commande", back_populates="incidents")

# ============= ITINERAIRES =============
class Itineraire(Base):
    __tablename__ = "itineraires"
    
    id = Column(Integer, primary_key=True, index=True)
    date_planifiee = Column(DateTime)
    depot_id = Column(Integer, ForeignKey("depots.id"))
    livreur_id = Column(Integer, ForeignKey("users.id"))
    distance_totale = Column(Float)
    temps_total = Column(Integer)  # en minutes
    commandes_count = Column(Integer)
    optimise = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    metadonnees = Column(JSON, nullable=True)
