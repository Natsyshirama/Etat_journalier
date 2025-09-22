from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
from controller.DatReport import DATReport 
from controller.DbGet import DbGet
from controller.Operation import Operation
from controller.OperatioDav import OperatioDav
from controller.Esri import Esri
from controller.OperationEsri import OperationEsri

from controller.DavUnique import DavUnique

router = APIRouter()
dat_report = DATReport()
db_get = DbGet()
operation = Operation()
operation_dav = OperatioDav()
dav_unique = DavUnique()
esri = Esri()
operation_esri = OperationEsri()


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


@router.post("/dat/create_dat_precompute")
def create_dat_precompute():
    """
    Crée une table DAT pré-calculée (DAT_<label>)
    """
    try:
        table_name = db_get.create_tableDatPreCompute()
        
        if not table_name:
            raise Exception("Erreur lors de la création de la table DAT")
        
       
        operation.calculeAmtCap(table_name)
        db_get.traitement_dat(table_name)
        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table créée et nettoyée et calculer : {table_name} ✅",
                    "table_name": table_name
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.post("/dat/create_dav_precompute")
def create_dav_precompute():
    """
    Crée une table DAV pré-calculée (DAV_<label>)
    """
    try:
        table_name = dav_unique.create_table_dav()
        
        if not table_name:
            raise Exception("Erreur lors de la création de la table DAV")
        operation_dav.calcule_dav(table_name)
        dav_unique.traitement_dav(table_name)

        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table créée et nettoyée et calculer : {table_name} ✅",
                    "table_name": table_name
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.post("/esri/create_esri_precompute")
def create_esri_precompute(label: str):
    try:
        table_name = esri.create_tableEsri(label)
        if not table_name:
            raise Exception("Erreur lors de la création de la table ESRI")
        
        operation_esri.calcule_esri(table_name)
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Table ESRI créée et pré-traitée : {table_name} ✅",
            "table_name": table_name
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.post("/dav/traitement_dav")
def traitement_dav(table_name: str):
    """
    Nettoie les données dans la table dav_<label>
    - Remplace NULL par 0 pour debit_mvmt, credit_mvmt, open_balance
    - Gère les duplicatas en gardant la première occurrence
    - Traite le code_client pour ne garder que la première valeur avant '|'
    """
    try:
        dav_unique.traitement_dav(table_name)
        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table nettoyée : {table_name} ✅"
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
    
    
    
    
    
    
#creation table et insertion de table arrangement_customer
@router.post("/dav/create_table_arrCust")
def create_table_arrCust():
    """
    Crée une table arrangement_customer
    """
    try:
        result = dav_unique.create_table_arrCust()
        
        if not result:
            raise Exception("Erreur lors de la création de la table arrangement_customer")
        
        
        dav_unique.insert_data_arrCust()
        dav_unique.create_index()
        
        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table arrangement_customer créée et donnee inserer avec les index ✅"
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


    
@router.get("/dat/export_excel")
def export_excel(table_name: str):
    """
    Exporte une table dat_<label> en fichier Excel et permet le téléchargement.
    """
    try:
        # Appel de ta fonction exportExcel()
        file_path = operation.exportExcel(table_name)

        if not file_path:
            raise Exception("Erreur lors de l'export Excel")

        # Retourne le fichier Excel au client
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file_path
        )

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

api_router = router