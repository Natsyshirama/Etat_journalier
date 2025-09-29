from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
from controller.DatReport import DatReport 
from controller.DbGet import DbGet
from controller.Operation import Operation
from controller.OperatioDav import OperatioDav
from controller.Esri import Esri
from controller.OperationEsri import OperationEsri

from controller.DavUnique import DavUnique

router = APIRouter()
dat_report = DatReport()
db_get = DbGet()
operation = Operation()
operation_dav = OperatioDav()
dav_unique = DavUnique()
esri = Esri()
operation_esri = OperationEsri()


@router.post("/dat/create_dat_precompute/{name}")
def create_dat_precompute(name: str):
    """
    Crée une table DAT pré-calculée (DAT_<label>)
    """
    try:
        table_name = db_get.create_tableDatPreCompute(name)
        db_get.update_statusHistoryInsert(name)
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


#exportation des tables
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

@router.get("/dat/liste_dat")
def listeDta():
    """
        liste table dat
    """ 
    try:
        listeDta = dat_report.getListeDat()
        if not listeDta:
            raise Exception("Aucune table DAT trouvée")
        
        return {"tables": listeDta}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/dat/{table_name}")
def get_dat_table(table_name: str):
    """ tablea de dat selectionner
    """
    try:
        data = dat_report.getDat(table_name)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

#returner le resumer

@router.get("/dat/{table_name}/resume")
def get_dat_resume(table_name: str):

    try:
        summary = dat_report.getResumeDat(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        # Conversion sécurisée en types JSON (int / float)
        safe_summary = {
            "table_name": table_name,
            "nb_lignes": int(summary.get("nb_lignes") or 0),
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_capital": float(summary.get("total_montant_capital") or 0),
            "total_montant_pay_total": float(summary.get("total_montant_pay_total") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
    
@router.get("/history/liste")
def liste_history():

    try:
        history_list = dat_report.getListeHistoryInsert()
        if not history_list:
            return JSONResponse(
                content={"status": "error", "message": "Aucun enregistrement trouvé"},
                status_code=404
            )
        return {"history": history_list}

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})



@router.get("/datGraphe/{table_name}")
def get_graphe_dat(
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: kill, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        data = dat_report.get_graphe_data(x, y, table_name)
        print(data)
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
        
api_router = router