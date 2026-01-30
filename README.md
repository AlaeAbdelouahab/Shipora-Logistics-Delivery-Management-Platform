# GL-PROJECT — Setup & Run Guide (Windows)

Ce projet contient :
- **Backend** : FastAPI (Python)
- **Frontend** : React + Vite
- **DB** : PostgreSQL

---

## 0\ Prérequis

### Installer :
- **Python 3.10+** (recommandé : 3.11) (ana 3ndi Python 3.13.5)
- **Node.js 18+** (ana 3ndi v22.15.0)
- **PostgreSQL 14+**
- **Git**

1\ Cloner le projet 

git clone <URL_DU_REPO>
cd GL-PROJECT

2\ Backend -- installation & lancement
2-1\ creer et activer un environnement virtuel

cd backend
python -m venv venv
.\venv\Scripts\activate

2-2\ installer les dependances

pip install -r requirements.txt

2-3\ Créer un fichier backend/.env :

# Remplacer USER, PASSWORD, DB_NAME selon ta config postgres
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/DB_NAME

SECRET_KEY= (Commande pour la générer: python -c "import secrets; print(secrets.token_hex(32))")

ALGORITHM=HS256

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=shipora.team@gmail.com
SMTP_PASSWORD=ucdkajniyjpltcwi

(email bach dkhlih 3ndk:
email : shipora.team@gmail.com
password : alaeshipora123)

OSRM_URL=http://router.project-osrm.org


2-4\ demarrer le backend

uvicorn main:app --reload

Le backend sera sur :

API : http://127.0.0.1:8000
Swagger : http://127.0.0.1:8000/docs

3\ Base de donnees PostgreSQL -- Setup

3-1\ Creer la base 

CREATE DATABASE logistics_db;

3-2\Appliquer les tables

4\Frontend -- Installation & lancement

cd frontend
npm install
npm run dev

Le frontend sera sur :

http://localhost:5173 (ou parfois 3000 selon config)

5\ CORS / Ports

Le backend autorise généralement :

http://localhost:3000

http://localhost:5173

Si votre frontend tourne sur un autre port, il faut l’ajouter dans backend/main.py (CORS).

6\ Test rapide (Checklist)

✅ Backend en marche :

http://127.0.0.1:8000/health → doit renvoyer { "status": "healthy" }

✅ Swagger en marche :

http://127.0.0.1:8000/docs

✅ Frontend en marche :

page accessible sur http://localhost:5173

✅ DB ok :

le backend ne doit pas afficher d’erreur DB au démarrage

7\ Scheduler (optimisation automatique)

Le scheduler démarre avec le backend.
Il lance l’optimisation à l’heure configurée dans backend/scheduler.py.

Pour tester manuellement :

Utiliser l’endpoint prévu (ex: POST /api/itineraires/run-optimization-now) si présent dans le projet.

