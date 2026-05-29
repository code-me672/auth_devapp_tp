# Importation des outils FastAPI
from fastapi import Depends, HTTPException, Request
# Importation de l'erreur JWT
from jose import JWTError
# Importation de la fonction de décodage du token
from .security import decode_token

# Fonction permettant de récupérer l'utilisateur connecté
def get_current_user(request: Request):
    
 # Récupération du token d'accès dans les cookies
    token = request.cookies.get(
        "access_token"
    )

     # Vérifie si le token existe
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token absent"
        )

    try:
         # Décodage du token
        payload = decode_token(token)
        return payload

     # Gestion des erreurs de token
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )
