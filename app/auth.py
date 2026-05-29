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
@router.post("/inscription")
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
@router.post("/connexion")
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
@router.post("/rafraichir_token")
def rafraichir_token(
    request: Request,
    response: Response
):

    # Récupération du refresh token dans les cookies
    token_rafraichissement = request.cookies.get(
        "refresh_token"
    )

    # Vérifie si le token existe
    if not token_rafraichissement :
        raise HTTPException(
            status_code=401,
            detail="Refresh token absent"
        )

    try:
         # Décodage du token
        payload = decode_token( token_rafraichissement)

        # Récupération du nom utilisateur
        nom_utilisateur = payload.get("sub")

         # Création d'un nouveau token d'accès
         nouveau_token_acce = create_access_token(
            {"sub": nom_utilisateur}
        )
        
           # Création d'un nouveau refresh token
         nouveau_token_rafraichissement = create_refresh_token(
            {"sub": nom_utilisateur}
        )

         # Mise à jour du cookie access token
        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=True,
            samesite="strict"
        )

        # Mise à jour du cookie refresh token
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

     # Gestion des erreurs
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Refresh token invalide"
        )
