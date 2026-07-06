from fastapi import APIRouter, HTTPException, Query,Request,Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
 
from controller.DbGet import DbGet
from controller.Users import Users
from controller.importController import  importController
from controller.AgenceController import AgenceController


router = APIRouter()

db_get = DbGet()

user= Users()
agence_controller = AgenceController()

#INITIALISATION COMPTE
def get_user_from_request(request: Request):
    return user.get_current_user(request)

# --- ROUTE PROTÉGEE ---
@router.get("/protected")
def protected(user_: str = Depends(get_user_from_request)):
    return user_



from fastapi import UploadFile, File
import pandas as pd
import re
import_controller = importController()

@router.post("/import/multi")
async def import_multi(files: List[UploadFile] = File(...)):
    errors = []
    success = []
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="Aucun fichier fourni"
            )
        
        invalid_files = []
        for file in files:
            if not file.filename.lower().endswith('.csv'):
                invalid_files.append(file.filename)
        
        if invalid_files:
            raise HTTPException(
                status_code=400,
                detail=f"Fichiers non CSV détectés: {', '.join(invalid_files)}"
            )
        
        if len(files) > 50:
            raise HTTPException(
                status_code=400,
                detail="Trop de fichiers. Maximum 50 fichiers par import."
            )
        
        result = import_controller.process_multiple_files(files)
        success.append(f"Import réussi : {file.filename}")

        return {
            "success": success,
            "errors": errors,
            "summary": result["summary"],
            "details": result["results"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        errors.append(f"Erreur insertion ligne: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'import: {str(e)}"
        )
        

@router.get("/agences")
async def get_all_agences():

    try:
        result = agence_controller.get_all_agences()
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except Exception as e:
        print(f"[ERREUR route get_all_agences] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/agences/{code}")
async def get_agence(code: str):
    """Récupérer une agence par son code"""
    try:
        result = agence_controller.get_agence_by_code(code)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERREUR route get_agence] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
from pydantic import BaseModel
from typing import Optional

class AgenceCreate(BaseModel):
    code: str 
    souscode: str
    nom: str
    id_zone: Optional[int] = None

class AgenceUpdate(BaseModel):
    souscode: Optional[str] = None
    nom: Optional[str] = None
    id_zone: Optional[int] = None
    
class ZoneBase(BaseModel):
    nom: str

class ZoneCreate(ZoneBase):
    pass

class ZoneResponse(ZoneBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        
@router.get("/zones")
async def get_all_zones():
    """Récupérer toutes les zones"""
    try:
        result = agence_controller.get_all_zones()
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except Exception as e:
        print(f"[ERREUR route get_all_zones] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zones/{zone_id}")
async def get_zone(zone_id: int):
    """Récupérer une zone par son ID"""
    try:
        # Vous devez ajouter cette méthode dans le contrôleur
        result = agence_controller.get_zone_by_id(zone_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except Exception as e:
        print(f"[ERREUR route get_zone] {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
@router.post("/agences/create_agence")
async def create_agence(agence_data: AgenceCreate):
    """Créer une nouvelle agence"""
    try:
        # Validation simple
        if not agence_data.code or not agence_data.souscode or not agence_data.nom:
            raise HTTPException(status_code=400, detail="Tous les champs sont requis")
        
        result = agence_controller.create_agence(
            code=agence_data.code,
            souscode=agence_data.souscode,
            nom=agence_data.nom,
            id_zone=agence_data.id_zone
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERREUR route create_agence] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Modifier la route update_agence pour accepter id_zone
@router.put("/agences/{code}")
async def update_agence(code: str, agence_data: AgenceUpdate):
    """Mettre à jour une agence"""
    try:
        result = agence_controller.update_agence(
            code=code,
            souscode=agence_data.souscode,
            nom=agence_data.nom,
            id_zone=agence_data.id_zone
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Erreur inconnue")
            status_code = 404 if "non trouvée" in error_msg else 400
            raise HTTPException(status_code=status_code, detail=error_msg)
        
        return {
            "response": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERREUR route update_agence] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.delete("/delete_agence/{code}")
async def delete_agence(code: str):
    """Supprimer une agence"""
    try:
        result = agence_controller.delete_agence(code)
        
        if not result.get("success"):
            error_msg = result.get("error", "Erreur inconnue")
            status_code = 404 if "non trouvée" in error_msg else 400
            raise HTTPException(status_code=status_code, detail=error_msg)
        
        return {
            "response": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERREUR route delete_agence] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/search_agence/")
async def search_agences(search: str = Query(..., min_length=1, description="Terme de recherche")):
    """Rechercher des agences"""
    try:
        result = agence_controller.search_agences(search)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "response": result
        }
        
    except Exception as e:
        print(f"[ERREUR route search_agences] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/")
async def create_batch_agences(agences_data: List[AgenceCreate]):
    """Créer plusieurs agences en une seule requête"""
    try:
        conn = None
        results = []
        
        for agence in agences_data:
            result = agence_controller.create_agence(
                code=agence.code,
                souscode=agence.souscode,
                nom=agence.nom
            )
            results.append(result)
        
        # Vérifier si toutes les opérations ont réussi
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "response": {
                "success": True,
                "message": f"{success_count}/{len(results)} agences créées",
                "details": results
            }
        }
        
    except Exception as e:
        print(f"[ERREUR route create_batch_agences] {e}")
        raise HTTPException(status_code=500, detail=str(e))
api_router2 = router
