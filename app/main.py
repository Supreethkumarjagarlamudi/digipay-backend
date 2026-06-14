from fastapi import FastAPI

from app.database import engine
from app.database import Base
from app.models.user_model import User
from app.models.otp_model import OTPVerification
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.merchant_routes import router as merchant_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DIGIPAY API",
    version="1.0.0"
)

from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "detail": exc.detail

        }

    )


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(
    merchant_router
)

@app.get("/")
def root():
    return {
        "message": "DIGIPAY Backend Running"
    }