from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from notifications import notification_service
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserBase, UserResponse
from security import verify_password, get_password_hash, create_access_token, generate_temp_password
import random
import string
import asyncio



router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role, "depot_id": user.depot_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "depot_id": user.depot_id
    }

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserBase, db: Session = Depends(get_db)):
    """Admin registration endpoint for new users"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    temp_password = generate_temp_password()
    hashed_password = get_password_hash(temp_password)

    db_user = User(
        email=user_data.email,
        nom=user_data.nom,
        prenom=user_data.prenom,
        mot_de_passe_hash=hashed_password,
        role=user_data.role,
        depot_id=user_data.depot_id,
        phone=user_data.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    #--- ENVOIE DU EMAIL ---
    if db_user.email:
        subject = "Votre compte Shipora a été créé"
        login_url = "http://localhost:3000/login"  # Update with actual frontend URL
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Bienvenue {db_user.prenom} {db_user.nom} !</h2>
                <p>Votre compte a été créé par l'administrateur.</p>
                <p><strong>Identifiants :</strong></p>
                <ul>
                    <li>Email: {db_user.email}</li>
                    <li>Mot de passe temporaire: {temp_password}</li>
                </ul>
                <p>Pour activer votre compte et vous connecter, cliquez ici :</p>
                <p><a href="{login_url}">Se connecter / Activer le compte</a></p>
                <p>Merci pour votre engagement !</p>
            </body>
        </html>
        """
        await notification_service.send_email(
            db_user.email,
            subject,
            html_content
        )
    return db_user


# --- from email.mime.text import MIMEText
#---      import aiosmtplib

  #      subject = "Votre compte Shipora a été créé"
   #     body = f"""
    #    Bonjour {db_user.prenom},
#
 #       Votre compte Shipora a été créé avec succès.
#
 #       Voici vos informations de connexion temporaires :
  #      Email: {db_user.email}
   #     Mot de passe temporaire: {temp_password}
#
 #       Veuillez vous connecter et changer votre mot de passe dès que possible.
#
 #       Cordialement,
  #      L'équipe Shipora
   #     """
#
 #       message = MIMEText(body)
  #      message["Subject"] = subject
   #     message["From"] = "<EMAIL>" 
