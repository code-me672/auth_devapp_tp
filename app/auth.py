from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session


from .database import get_db
from .models import User
from .schemas import UserCreate, UserLogin
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

# Création du routeur API
router = APIRouter()

MAX_TENTATIVES = 5

# Route d'inscription
@router.post("/register")
def inscription(utilisateur: UserCreate, db: Session = Depends(get_db)):

     # Recherche de l'utilisateur
     utilisateur_existant = db.query(User).filter(
        utilisateur.username == user.username
    ).first()
    
# Vérifie si l'utilisateur existe déjà
    if utilisateur_existant:
        raise HTTPException(
            status_code=400,
            detail="Utilisateur existe déjà"
        )

 # Chiffrement du mot de passe
    mot_de_passe_hache = hash_password(utilisateur.password)

# Création du nouvel utilisateur
    nouvel_utilisateur = User(
        username=utilisateur.username,
        password=mot_de_passe_hache
    )

 # Ajout dans la base
    db.add(nouvel_utilisateur)
    db.commit()

    return {"message": "Utilisateur créé"}

# Route de connexion utilisateur
@router.post("/login")
def connexion(
    utilisateur: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
 # Recherche de l'utilisateur dans la base
    utilisateur_db  = db.query(User).filter(
        User.username == utilisateur.username
    ).first()

      # Vérifie si l'utilisateur existe
    if not utilisateur_db :
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides"
        )

    # Vérifie si le compte est verrouillé
    if utilisateur_db .locked:
        raise HTTPException(
            status_code=403,
            detail="Compte verrouillé"
        )

     # Vérification du mot de passe
    if not verify_password( utilisateur.password, utilisateur_db.password):

          # Ajoute une tentative échouée
        db_user.failed_attempts += 1

         # Verrouille le compte après plusieurs échecs
        if utilisateur_db.failed_attempts >= MAX_FAILED_ATTEMPTS:
            utilisateur_db.locked = True

        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )
         # Réinitialise les tentatives échouée
    utilisateur_db.failed_attempts = 0
    db.commit()

        # Création du token d'accès
    access_token = create_access_token(
        {"sub": utilisateur_db.username}
    )

    # Création du refresh token
    refresh_token = create_refresh_token(
        {"sub": db_user.username}
    )

      # Enregistrement du token d'accès dans les cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    # Enregistrement du refresh token dans les cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {
        "message": "Connexion réussie"
    }

# Route permettant de renouveler les tokens
@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response
):

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token absent"
        )

    try:
        payload = decode_token(refresh_token)

        username = payload.get("sub")

        new_access = create_access_token(
            {"sub": username}
        )

        new_refresh = create_refresh_token(
            {"sub": username}
        )

        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=True,
            samesite="strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="strict"
        )

        return {
            "message": "Tokens rafraîchis"
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Refresh token invalide"
        )
