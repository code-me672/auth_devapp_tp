from fastapi import Depends, HTTPException, Request
from jose import JWTError

from .security import decode_token

def get_current_user(request: Request):

    token = request.cookies.get(
        "access_token"
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token absent"
        )

    try:
        payload = decode_token(token)
        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )