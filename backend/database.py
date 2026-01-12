from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupère l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie ! Vérifie ton fichier .env")

# Création du moteur SQLAlchemy avec les options souhaitées
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
    )

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Fonction utilitaire pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer toutes les tables dans la base
def init_db():
    Base.metadata.create_all(bind=engine)
