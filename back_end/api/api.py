from fastapi import APIRouter, UploadFile, File,FastAPI,Response,Depends, Form, Request,HTTPException,Query

from controller.Users import Users
from fastapi.responses import StreamingResponse
from typing import List
from typing import Optional
from fastapi.responses import JSONResponse
from decimal import Decimal
import json
import time
import asyncio 

from fastapi.responses import FileResponse
import io  ,os


 
 
 
 
router = APIRouter()

user= Users()




#  ------------  LOGIN  -----------  


# --- SIGNUP ---
@router.post("/signup")
def signup(username: str = Form(...), password: str = Form(...), immatricule: str = Form(...)):
    return user.signup(username, password, immatricule)

# --- SIGNIN ---
@router.post("/signin")
def signin(username: str = Form(...), password: str = Form(...)):
    result = user.signin(username, password)

    # Si connexion réussie, on ajoute les colonnes manquantes
    try:
        if result.get("success"):
            print("[WARN] Échec de la vérification/ajout des colonnes ⚠️")
    except Exception as e:
        print(f"[ERREUR] lors de la vérification des colonnes : {e}")

    return result
# --- GET CURRENT USER ---
def get_user_from_request(request: Request):
    return user.get_current_user(request)

# --- ROUTE PROTÉGÉE ---
@router.get("/protected")
def protected(user_: str = Depends(get_user_from_request)):
    return user_

@router.post("/validate_user")
def validate_user(
    request: Request,
    username: str = Form(...),
    role: str = Form(...),
    admin_password: str = Form(...)
):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return user.validate_user(request, username,role,admin_password)


@router.post("/block_user")
def block_user(
    request: Request,
    username: str = Form(...),
    admin_password: str = Form(...)
):
    
    current_user = user.get_current_user(request)
    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return user.block_user(request, username, admin_password)


@router.post("/update_user_role")
def update_user_role(
    request: Request,
    username: str = Form(...),
    role: str = Form(...),
    admin_password: str = Form(...)
):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return user.update_user_role(request, username, role, admin_password)

@router.get("/users")
def get_users(request: Request):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return user.getListeUser()

@router.get("/users/pending_count")
def get_pending_count():
    return user.get_pending_validation_count()

@router.get("/user/{user_id}")
def get_users(request: Request, user_id: int):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return user.getUserById(user_id)


# --- LOGOUT ---

@router.post("/logout")
def logout(response: Response):
    return user.logout(response)


api_router = router