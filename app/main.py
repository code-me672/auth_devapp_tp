from fastapi import FastAPI, Depends, Request
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

from .database import Base, engine
from .auth import router
from .middleware import limiter
from .dependencies import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)

app.include_router(router)


@app.get("/protected")
@limiter.limit("5/minute")
def protected_route(
    request: Request,
    current_user=Depends(get_current_user)
):
    return {
        "message": "Zone protégée",
        "user": current_user
    }