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
def login(
    user: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides"
        )

    if db_user.locked:
        raise HTTPException(
            status_code=403,
            detail="Compte verrouillé"
        )

    if not verify_password(user.password, db_user.password):

        db_user.failed_attempts += 1

        if db_user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            db_user.locked = True

        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )

    db_user.failed_attempts = 0
    db.commit()

    access_token = create_access_token(
        {"sub": db_user.username}
    )

    refresh_token = create_refresh_token(
        {"sub": db_user.username}
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

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
