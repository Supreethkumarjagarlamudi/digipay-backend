from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.database import Base
from app.models.user_model import User
from app.models.otp_model import OTPVerification
from app.models.expense_model import Expense
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.merchant_routes import router as merchant_router
from app.routes.expense_routes import router as expense_router
from app.routes.admin_routes import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DIGIPAY API",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://harishbalaji826-ops.github.io",
    "https://supreethkumarjagarlamudi.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\.github\.io",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(merchant_router)
app.include_router(expense_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "DIGIPAY Backend Running"
    }