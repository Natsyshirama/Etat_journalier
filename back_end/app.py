from fastapi import FastAPI
from controller.AgenceController import AgenceController
from api.apiCompte import api_router2   
from api.api import api_router
from api.apiPowerCard import api_router_powercard
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # ton frontend en local
        "http://127.0.0.1:5173",  # si tu y accèdes depuis un autre PC
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
# Initialiser la classe agence_controller
agence_controller = AgenceController()


# Enregistrer les routes de l'API
app.include_router(api_router, prefix="/api")

app.include_router(api_router2, prefix="/api")

app.include_router(api_router_powercard, prefix="/api")

