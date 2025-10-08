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
from controller.DavReport import DavReport
from controller.ChangeMande import ChangeMande
from controller.EsriReport import EsriReport
from controller.DavUnique import DavUnique

router = APIRouter()
dat_report = DatReport()
db_get = DbGet()
operation = Operation()
operation_dav = OperatioDav()
dav_unique = DavUnique()
esri = Esri()
operation_esri = OperationEsri()
dav_report = DavReport()
change_mande = ChangeMande()
esri_report = EsriReport()

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
def create_dav_precompute(name:str):

    try:
        table_name = dav_unique.create_table_dav(name)
        dav_unique.update_statusHistoryInsert(name)
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
    
#******************* INITIALISATION DAT ET DAV***********************
@router.post("/dat/initialise/{name}")
def initialize(name: str):
    try:
        table_name_dat = db_get.create_tableDatPreCompute(name)
        table_name_dav = dav_unique.create_table_dav(name)
        
        dav_unique.update_statusHistoryInsert(name)
        db_get.update_statusHistoryInsert(name)
        if not table_name_dat or not table_name_dav:
            raise Exception("Erreur lors de la création de la table DAT et DAV")
        
        operation.calculeAmtCap(table_name_dat)
        db_get.traitement_dat(table_name_dat)
        operation_dav.calcule_dav(table_name_dav)
        dav_unique.traitement_dav(table_name_dav)
        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table créée et nettoyée et calculer : {table_name_dat} et {table_name_dav} ✅",
                    "table_name_dat": table_name_dat,
                    "table_name_dav": table_name_dav
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
        
#INITIALISATION ESRI
#create tables esri_precompute

@router.post("/esri/create_esri_precompute")
def create_esri_precompute( date_debut: str = Query(...), date_fin: str = Query(...)):
    try:
        # --- Exécuter le traitement ESRI ---
        result_df,columns = operation_esri.process_esri_data_fast(date_debut, date_fin)

        if result_df.empty:
            return JSONResponse(
                content={
                    "status": "warning",
                    "message": f"Aucune donnée trouvée entre {date_debut} et {date_fin}",
                   
                },
                status_code=200
            )

        # --- Convertir le DataFrame en liste de dictionnaires ---
        data_json = json.loads(result_df.to_json(orient="records", force_ascii=False))

        # --- Réponse finale ---
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Données ESRI pré-calculées entre {date_debut} et {date_fin} ✅",
                
                "columns": columns,
                "rows": data_json,
                "count": len(data_json)
            },
            status_code=200
        )

    except Exception as e:
        import traceback
        print(f"[ERREUR] create_esri_precompute : {e}")
        print(traceback.format_exc())
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)








###########INITIALISATION CHANGE#############
@router.post("/change/generate_tables")
def create_change_precompute(value_date: str):
    try:
        result = change_mande.generate_tables_report(value_date)
       
        if result and result.get("status") == "success":
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            raise Exception("Erreur lors de la création des tables Change Mande")
        
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



###EXPORT EXCEL###
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




##"""""""""""""DAT REPORT""""""""""""""##
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







##"""""""""""HISTORY INSERT""""""""""##
 
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









#""""""""""""""""""""""DAV REPORT""""""""""""""""""##
@router.get("/dav/liste_dav")
def listeDav():
    """
        liste table dav
    """ 
    try:
        listeDav = dav_report.getListeDav()
        if not listeDav:
            raise Exception("Aucune table DAV trouvée")
        
        return {"tables": listeDav}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/dav/{table_name}")
def get_dav_table(table_name: str):
    """ tablea de dav selectionner
    """
    try:
        data = dav_report.getDav(table_name)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/dav/{table_name}/resume")
def get_dav_resume(table_name: str):

    try:
        summary = dav_report.getResumeDav(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        # Conversion sécurisée en types JSON (int / float)
        safe_summary = {
            
            "table_name": table_name,
            "nb_lignes": int(summary.get("nb_lignes") or 0),
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_dav": float(summary.get("total_montant_dav") or 0),
            "total_debit_dav": float(summary.get("total_debit_dav") or 0),
            "total_credit_dav": float(summary.get("total_credit_dav") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    


@router.get("/davGraphe/{table_name}")
def get_graphe_dav(
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        data = dav_report.get_graphe_dataDav(x, y, table_name)
        print(data)
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


api_router = router