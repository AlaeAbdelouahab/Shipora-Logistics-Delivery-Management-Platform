"""
Script to initialize the database with demo data
Run: python scripts/init_database.py
"""

import sys
sys.path.insert(0, '/backend')

from database import SessionLocal, init_db
from models import User, Depot, Commande, UserRole, DeliveryStatus
from security import get_password_hash
from datetime import datetime, timedelta
import uuid

def init_database():
    """Initialize database with demo data"""
    init_db()
    db = SessionLocal()
    
    try:
        # Create depots
        depot_paris = Depot(
            nom="Dépôt Paris",
            adresse="123 Avenue des Champs, Paris",
            latitude=48.8697,
            longitude=2.3076,
            capacite_max=1000
        )
        depot_lyon = Depot(
            nom="Dépôt Lyon",
            adresse="456 Rue de la République, Lyon",
            latitude=45.7640,
            longitude=4.8357,
            capacite_max=800
        )
        db.add_all([depot_paris, depot_lyon])
        db.commit()
        
        # Create admin user
        admin = User(
            email="admin@example.com",
            nom="Admin",
            prenom="Système",
            mot_de_passe_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            depot_id=depot_paris.id,
            phone="01.00.00.00.00"
        )
        
        # Create manager users
        manager_paris = User(
            email="manager@example.com",
            nom="Martin",
            prenom="Gestionnaire",
            mot_de_passe_hash=get_password_hash("manager123"),
            role=UserRole.GESTIONNAIRE,
            depot_id=depot_paris.id,
            phone="01.23.45.67.89"
        )
        
        manager_lyon = User(
            email="manager_lyon@example.com",
            nom="Durand",
            prenom="Gestionnaire",
            mot_de_passe_hash=get_password_hash("manager123"),
            role=UserRole.GESTIONNAIRE,
            depot_id=depot_lyon.id,
            phone="04.23.45.67.89"
        )
        
        # Create driver users
        driver1 = User(
            email="driver@example.com",
            nom="Bernard",
            prenom="Livreur",
            mot_de_passe_hash=get_password_hash("driver123"),
            role=UserRole.LIVREUR,
            depot_id=depot_paris.id,
            phone="06.12.34.56.78"
        )
        
        driver2 = User(
            email="driver2@example.com",
            nom="Lefebvre",
            prenom="Jean",
            mot_de_passe_hash=get_password_hash("driver123"),
            role=UserRole.LIVREUR,
            depot_id=depot_paris.id,
            phone="06.98.76.54.32"
        )
        
        driver3 = User(
            email="driver3@example.com",
            nom="Gauthier",
            prenom="Pierre",
            mot_de_passe_hash=get_password_hash("driver123"),
            role=UserRole.LIVREUR,
            depot_id=depot_lyon.id,
            phone="06.11.22.33.44"
        )
        
        db.add_all([admin, manager_paris, manager_lyon, driver1, driver2, driver3])
        db.commit()
        
        # Create sample commandes
        commandes_data = [
            {
                "id_commande": "CMD001",
                "adresse": "10 Rue de Rivoli, 75001 Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "poids": 2.5,
                "depot_id": depot_paris.id
            },
            {
                "id_commande": "CMD002",
                "adresse": "25 Boulevard Saint-Germain, 75005 Paris",
                "latitude": 48.8553,
                "longitude": 2.3469,
                "poids": 1.8,
                "depot_id": depot_paris.id
            },
            {
                "id_commande": "CMD003",
                "adresse": "42 Avenue Montaigne, 75008 Paris",
                "latitude": 48.8697,
                "longitude": 2.3076,
                "poids": 3.2,
                "depot_id": depot_paris.id
            },
            {
                "id_commande": "CMD004",
                "adresse": "15 Rue Bellecour, 69002 Lyon",
                "latitude": 45.7579,
                "longitude": 4.8320,
                "poids": 2.0,
                "depot_id": depot_lyon.id
            },
            {
                "id_commande": "CMD005",
                "adresse": "88 Rue de la République, 69003 Lyon",
                "latitude": 45.7650,
                "longitude": 4.8400,
                "poids": 1.5,
                "depot_id": depot_lyon.id
            }
        ]
        
        for data in commandes_data:
            commande = Commande(
                **data,
                statut=DeliveryStatus.EN_ATTENTE,
                code_tracking=str(uuid.uuid4())[:8].upper()
            )
            db.add(commande)
        
        db.commit()
        print("Database initialized successfully!")
        print("\nDemo credentials:")
        print("- Admin: admin@example.com / admin123")
        print("- Manager: manager@example.com / manager123")
        print("- Driver: driver@example.com / driver123")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
