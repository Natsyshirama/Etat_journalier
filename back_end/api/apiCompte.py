from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
from controller.DatReport import DATReport 
from controller.DbGet import DbGet

router = APIRouter()
dat_report = DATReport()
db_get = DbGet()


@router.get("/dat/all")
def get_all_dat(limit: int = Query(1000, description="Nombre de lignes à retourner")):
    """
    Récupère les premières lignes de la table DAT pré-calculée
    """
    try:
        data = dat_report.get_all(limit=limit)
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.get("/dat/client/{code_client}")
def get_dat_by_client(code_client: str):
    """
    Récupère les données DAT pour un code client spécifique
    """
    try:
        data = dat_report.get_by_client(code_client)
        if not data:
            return JSONResponse(content={"status": "warning", "message": f"Aucune donnée trouvée pour le client {code_client}"})
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.get("/dat/history")
def get_dat_history():
    """
    Récupère le dernier label actif dans history_mcbd
    """
    try:
        label = db_get.getHistory()
        if not label:
            return JSONResponse(content={"status": "warning", "message": "Aucun label actif trouvé"})
        return JSONResponse(content={"status": "success", "label": label})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.post("/dat/create_precompute")
def create_dat_precompute():
    """
    Crée une table DAT pré-calculée (DAT_<label>)
    """
    try:
        table_name = db_get.create_tableDatPreCompute()
        return JSONResponse(content={"status": "success", "message": f"Table créée : {table_name}", "table_name": table_name})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


api_router = router