# Route Optimization System - Backend

FastAPI backend pour le système de gestion logistique avec optimisation d'itinéraires.

## Installation

### 1. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration
```bash
cp .env.example .env
# Modifier .env avec vos paramètres de base de données
```

### 4. Initialiser la base de données
```bash
python scripts/init_database.py
```

### 5. Démarrer le serveur
```bash
uvicorn main:app --reload --port 8000
```

Le serveur sera disponible à : http://localhost:8000

## Documentation API

Une fois le serveur démarré, visitez :
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints principaux

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Créer un utilisateur

### Commandes
- `GET /api/commandes/` - Liste des commandes
- `POST /api/commandes/` - Créer une commande
- `POST /api/commandes/import_excel` - Importer depuis Excel
- `PUT /api/commandes/{id}` - Modifier une commande

### Livraisons
- `GET /api/livraisons/` - Liste des livraisons
- `POST /api/livraisons/` - Créer une livraison
- `PUT /api/livraisons/{id}` - Mettre à jour le statut

### Itinéraires
- `POST /api/itineraires/optimize` - Optimiser les itinéraires
- `GET /api/itineraires/` - Liste des itinéraires

### Incidents
- `POST /api/incidents/` - Signaler un incident
- `GET /api/incidents/` - Liste des incidents
- `PUT /api/incidents/{id}/resolve` - Résoudre un incident

### Rapports
- `GET /api/reports/dashboard-stats` - Statistiques du dashboard
- `GET /api/reports/performance` - Performance des livreurs

### Suivi Client
- `GET /api/clients/tracking/{code_tracking}` - Suivi de commande

## Utilisateurs de démonstration

Après l'initialisation :
- **Admin**: admin@example.com / admin123
- **Gestionnaire**: manager@example.com / manager123
- **Livreur**: driver@example.com / driver123

## Architecture

```
backend/
├── main.py              # Point d'entrée FastAPI
├── database.py          # Configuration SQLAlchemy
├── models.py            # Modèles de données
├── schemas.py           # Schémas Pydantic
├── security.py          # JWT et hachage de mots de passe
├── dependencies.py      # Dépendances FastAPI
├── routes/
│   ├── auth.py         # Authentification
│   ├── users.py        # Gestion utilisateurs
│   ├── commandes.py    # Gestion commandes
│   ├── livraisons.py   # Gestion livraisons
│   ├── itineraires.py  # Optimisation itinéraires
│   ├── incidents.py    # Gestion incidents
│   ├── reports.py      # Rapports et statistiques
│   └── clients.py      # Suivi client
├── scripts/
│   └── init_database.py # Initialisation demo
├── requirements.txt     # Dépendances Python
└── README.md           # Documentation
```

## Développement local avec Docker

```bash
docker-compose up
```

Cela démarrera PostgreSQL et le serveur FastAPI.
