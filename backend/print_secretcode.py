from dotenv import load_dotenv
import os

load_dotenv()  # ça va lire .env dans le dossier courant

print("SECRET_KEY:", os.getenv("SECRET_KEY"))  # juste pour vérifier