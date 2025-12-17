from fastapi import APIRouter, HTTPException, Query,Request,Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
from controller.DatReport import DatReport 
from controller.DbGet import DbGet
from controller.Operation import Operation
from controller.OperationEsri import OperationEsri
from controller.DavReport import DavReport
from controller.EprReport import EprReport
from controller.ChangeMandy import ChangeMandy
from controller.DavUnique import DavUnique
from controller.decaissementReport import decaissementReport
from controller.decaissement import DecaissementOptimise
from controller.Users import Users
from controller.importController import  importController
from controller.AgenceController import AgenceController


router = APIRouter()
dat_report = DatReport()
db_get = DbGet()
operation = Operation()
dav_unique = DavUnique()
operation_esri = OperationEsri()
dav_report = DavReport()
epr_report = EprReport()
change_mandy = ChangeMandy()
decaissement = DecaissementOptimise()
decaissement_report = decaissementReport()
user= Users()
agence_controller = AgenceController()

#INITIALISATION COMPTE
def get_user_from_request(request: Request):
    return user.get_current_user(request)

# --- ROUTE PROTÉGEE ---
@router.get("/protected")
def protected(user_: str = Depends(get_user_from_request)):
    return user_

@router.post("/compte/compte_init/{name}")
def initialize(request: Request, 
               name:str):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        createStatus = dav_unique.add_status_columns()
        if not createStatus:
            raise Exception("Erreur lors de l'ajout des colonnes de statut")
        
        createIndexGeneral = db_get.create_indexes()
        if not createIndexGeneral:
            raise Exception("Erreur lors de la création des index généraux")
        
        createTempClients = dav_unique.create_temp_client()
        if not createTempClients:
            raise Exception("erreur Creation table temp client")
        
        createIndex = dav_unique.create_index()
        if not createIndex:
            raise Exception("Erreur lors de la création des index")
        
        
        
        createFunctions = dav_unique.create_funct()
        if not createFunctions:
            raise Exception("Erreur lors de la création des fonctions")
        
        if dav_unique.verifie_statu(name):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "info",
                    "message": f"Le compte {name} est déjà initialisé",
                    "already_initialized": True
                }
            )
        
        table_name_dat = db_get.create_tableDatPreCompute(name)
        table_name_dav = dav_unique.create_table_dav(name)
        table_name_epr = dav_unique.create_table_epr(name)
        # table_name_dec = decaissement.generate_decaissement_report(name)        

        
        if not table_name_dat or not table_name_dav or not table_name_epr :
            raise Exception("Erreur lors de la création des tables DAT, DAV et EPR et Decaissement")
        
        operation.calculeAmtCap(table_name_dat)
        db_get.traitement_dat(table_name_dat)
        dav_unique.update_status(name)

        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table créée et nettoyée et calculer : {table_name_dav} et {table_name_epr} et {table_name_dat}✅",
                    "table_name_dav": table_name_dav,
                    "table_name_epr": table_name_epr,
                    "table_name_dat": table_name_dat,
                    # "table_name_dec": table_name_dec.get("table_name") if isinstance(table_name_dec, dict) else table_name_dec,
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    

#teste decaissement
@router.post("/compte/decaissement/{name}")
def create_decaissement(date_limit:str):
    try:
        
        result = decaissement.generate_decaissement_report(date_limit)        
        
       
        if result:
            print(f"Table créée : {result['table_name']}")
            print(f"Enregistrements : {result['record_count']}")
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
# ESRI

@router.post("/esri/create_esri_precompute")
def create_esri_precompute( request: Request, date_debut: str = Query(...), date_fin: str = Query(...),    compare: bool = Query(False) , unique: bool = Query(False)
):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        limit = db_get.getHistoryDate()
        if limit and (date_debut > limit or date_fin > limit):
            raise Exception(f"Les données apres le {limit} ne sont pas encore disponible.")
       
        result_df,columns ,bilan= operation_esri.process_esri_data_fast(date_debut, date_fin, compare_mode=compare ,unique_mode=unique)

        if  result_df.empty :
            return JSONResponse(
                content={
                    "status": "warning",
                    "message": f"Aucune donnée trouvée entre {date_debut} - {date_fin}",
                   "columns": [],
                    "rows": [],
                    "bilan": [],
                    "count": 0
                },
                status_code=200
            )

        data_json = json.loads(result_df.to_json(orient="records", force_ascii=False))

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Données ESRI  entre {date_debut} - {date_fin} ",
                
                "columns": columns,
                "rows": data_json,
                "bilan": bilan.to_dict(orient="records"),
                "count": len(data_json)
            },
            status_code=200
        )

    except Exception as e:
        import traceback
        print(f"[ERREUR] create_esri_precompute : {e}")
        print(traceback.format_exc())
        return JSONResponse(
            content={
                "status": "error", 
                "message": str(e),
                "columns": [],
                "rows": [],
                "bilan": [],
                "count": 0
            }, 
            status_code=500
        )
@router.post("/change/generate_report")
def create_change_report(request: Request, date_debut: str, date_fin: str, unique: bool = Query(False)):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user", "admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        limit = db_get.getHistoryDate()
        if limit and (date_debut > limit or date_fin > limit):
            raise Exception(f"Les données après le {limit} ne sont pas encore disponibles.")
        
        # Appel du contrôleur
        result = change_mandy.generate_tables_report(date_debut, date_fin, unique_mode=unique)
        
        if result is False:
            message = f"Échec de la génération des tables pour la période du {date_debut}"
            if not unique and date_debut != date_fin:
                message = f"Échec de la génération des tables du {date_debut} au {date_fin}"
                
            return JSONResponse(
                status_code=200,
                content={
                    "status": "warning",
                    "message": message,
                    "periode": {"date_debut": date_debut, "date_fin": date_fin},
                    "etat": [],
                    "allocation": [],
                    "synthese": []
                }
            )
        
        if isinstance(result, dict):
            if result.get("status") == "warning" or result.get("status") == "error":
                return JSONResponse(
                    status_code=200 if result.get("status") == "warning" else 500,
                    content=result
                )
            elif result.get("status") == "success":
                response_data = {
                    "status": "success",
                    "message": result.get("message", ""),
                    "periode": {"date_debut": date_debut, "date_fin": date_fin},
                    "etat": result.get("etat", []),
                    "allocation": result.get("allocation", []),
                    "synthese": result.get("synthese", []),
                }
                return JSONResponse(status_code=200, content=response_data)
        
        # Ancienne logique pour compatibilité
        if not result:
            message = f"Aucune donnée disponible pour la période du {date_debut}"
            if not unique and date_debut != date_fin:
                message = f"Aucune donnée disponible pour la période du {date_debut} au {date_fin}"
                
            return JSONResponse(
                status_code=200,
                content={
                    "status": "warning",
                    "message": message,
                    "periode": {"date_debut": date_debut, "date_fin": date_fin},
                    "etat": [],
                    "allocation": [],
                    "synthese": []
                }
            )
        
        response_data = {
            "status": "success",
            "message": result.get("message", ""),
            "periode": {"date_debut": date_debut, "date_fin": date_fin},
            "etat": result.get("etat", []),
            "allocation": result.get("allocation", []),
            "synthese": result.get("synthese", []),
        }

        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

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
def get_dat_table(request: Request,table_name: str, agence: str = None):
   
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = dat_report.getDat(table_name, agence)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


@router.get("/dat/{table_name}/resume")
def get_dat_resume(request: Request,table_name: str):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

#controller/DatReport.py
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
    request: Request,
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: kill, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")
        #controller/DatReport.py
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
def get_dav_table(request: Request,table_name: str, agence: str = None):
    """ tablea de dav selectionner
    """
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = dav_report.getDav(table_name, agence)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/dav/{table_name}/resume")
def get_dav_resume(request: Request,table_name: str):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        summary = dav_report.getResumeDav(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        safe_summary = {
            
            "table_name": table_name,
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
    

@router.get("/resume/all/{type_table}")
def get_all_resume(request:Request,type_table: str):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        summaries = dav_report.getAllResumeDav(type_table)
        if not summaries:
            return JSONResponse(status_code=404, content={"error": f"Aucune table trouvée pour le type {type_table}"})
        return summaries
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
    
@router.get("/resume/global/{type_table}")
def getTotalResumer(type_table: str):
    try:
        summary = dav_report.getTotalResumer(type_table)
        if not summary:
            return JSONResponse(status_code=404, content={"error": f"Aucune donnée trouvée pour le type '{type_table}'"})
        return summary
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/resume/total-produit/{type_table}")
def get_total_par_produit(
    request: Request,
    type_table: str,
    agence: str = None,
    date_debut: str = None,
    date_fin: str = None,
    single_date_if_all = None,
    compare: bool = Query(False, description="Comparer uniquement date_debut et date_fin")
):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        total = dav_report.getTotalParProduit(
            type_table=type_table,
            agence=agence,
            date_debut=date_debut,
            date_fin=date_fin,
            single_date_if_all=single_date_if_all,
            compare=compare

        )

        if not total:
            return JSONResponse(
                status_code=404,
                content={"info": f"Aucune donnée trouvée pour cette Periode"}
            )

        return total

    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"error": str(ve)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur serveur: {e}"}
        )
        
@router.get("/resume/decaissement")
def get_total_par_produit(
    request: Request,
    agence: str = None,
    date_debut: str = None,
    date_fin: str = None,
    single_date_if_all: str = None,
    compare: bool = Query(False, description="Comparer uniquement date_debut et date_fin")

):
    try:
        # current_user = user.get_current_user(request)
        # if current_user.get("privillege") not in ["user", "admin", "superadmin"]:
        #     raise HTTPException(
        #         status_code=403,
        #         detail="Accès refusé : privilège insuffisant"
        #     )

        total = decaissement_report.getDecAn(
            agence=agence,
            date_debut=date_debut,
            date_fin=date_fin,
            single_date_if_all=single_date_if_all,
            compare=compare
        )

        if not total:
            return JSONResponse(
                status_code=404,
                content={"error": "Aucune donnée trouvée pour décaissement"}
            )

        return total

    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"error": str(ve)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur serveur: {e}"}
        )


@router.get("/resume/total-produit/decaissement")
def get_total_decaissement(
    request: Request,
    agence: str = None,
    date_debut: str = None,
    date_fin: str = None,
    single_date_if_all: str = None
):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé")
        total = decaissement_report.getTotalParProduit(
            agence=agence,
            date_debut=date_debut,
            date_fin=date_fin,
            single_date_if_all=single_date_if_all or "20251028"
        )
        if not total:
            return JSONResponse(status_code=404, content={"error": "Aucune donnée decaissement"})
        return total
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    
@router.get("/resume/total-produit/global")
def get_total_global(request: Request, agence: str = None, date_debut: str = None, date_fin: str = None):
    try:
        dav = dav_report.getTotalParProduit("dav", agence, date_debut, date_fin)
        dat = dav_report.getTotalParProduit("dat", agence, date_debut, date_fin)
        epr = dav_report.getTotalParProduit("epr", agence, date_debut, date_fin)

        # Indexation par date
        dict_dav = { row["date_agence"]["date"]: row for row in dav }
        dict_dat = { row["date_agence"]["date"]: row for row in dat }
        dict_epr = { row["date_agence"]["date"]: row for row in epr }

        # Fusion des dates disponibles
        all_dates = sorted(set(dict_dav.keys()) | set(dict_dat.keys()) | set(dict_epr.keys()))

        result = []

        for d in all_dates:
            dav_row = dict_dav.get(d, {"data": {}})
            dat_row = dict_dat.get(d, {"data": {}})
            epr_row = dict_epr.get(d, {"data": {}})

            encours = (
                dav_row["data"].get("total_debit", 0) +
                dat_row["data"].get("total_montant", 0) +
                epr_row["data"].get("total_debit", 0)
            )

            result.append({
                "date": d,
                "agence": agence,
                "dav": dav_row,
                "dat": dat_row,
                "epr": epr_row,
                "encours_depot": encours
            })

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/davGraphe/{table_name}")
def get_graphe_dav(
    request: Request,
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = dav_report.get_graphe_dataDav(x, y, table_name)
       
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


#***********EPR**********#
@router.get("/epr/liste_epr")
def listeEpr():
   
    try:
        listeEpr = epr_report.getListeEpr()
        if not listeEpr:
            raise Exception("Aucune table EPR trouvée")
        
        return {"tables": listeEpr}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/epr/{table_name}")
def get_epr_table(
    request: Request,
    table_name: str,
    agence: str = None):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = epr_report.getEpr(table_name,agence)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/epr/{table_name}/resume")
def get_epr_resume(
    request: Request,
    table_name: str):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        summary = epr_report.getResumeEpr(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        safe_summary = {
            
            "table_name": table_name,
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_epr": float(summary.get("total_montant_epr") or 0),
            "total_debit_epr": float(summary.get("total_debit_epr") or 0),
            "total_credit_epr": float(summary.get("total_credit_epr") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/eprGraphe/{table_name}")
def get_graphe_epr(
    request: Request,
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = epr_report.get_graphe_dataEpr(x, y, table_name)
        
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

#***************decaissement//***********
@router.get("/decaissement/liste_decaissement")
def listeDecaissement():
   
    try:
        listeDecaissement = decaissement_report.getListeDecaissement()
        if not listeDecaissement:
            raise Exception("Aucune table Decaissement trouvée")
        
        return {"tables": listeDecaissement}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/decaissement/{table_name}")
def get_decaissement_table(
    request: Request,
    table_name: str,
     agence: str = None):
    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = decaissement_report.getDecaissement(table_name, agence)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/decaissement/{table_name}/resume")
def get_decaissement_resume(
    request: Request,
    table_name: str):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        summary = decaissement_report.getResumeDecaissement(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        safe_summary = {
            
            "table_name": table_name,
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_capital": float(summary.get("total_montant_capital") or 0),
            "total_frais_de_dossier": float(summary.get("total_frais_de_dossier") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
    
@router.get("/decaissementGraphe/{table_name}")   
def get_graphe_decaissement(
    request: Request,  
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        current_user = user.get_current_user(request)
        if current_user.get("privillege") not in ["user","admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

        data = decaissement_report.get_grapheDec(x, y, table_name)
        
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


import pandas as pd
from fastapi import APIRouter, Query, Response
import io
import zipfile
@router.get("/export/multi")
def export_multi(
    type: str = Query(..., description="Type de données (dav, dat, epr, decaissement, all)"),
    date_debut: str = Query(..., description="Date de début (YYYYMMDD)"),
    date_fin: str = Query(..., description="Date de fin (YYYYMMDD)"),
    format: str = Query("csv", description="Format d'export (csv, excel)")
):
    db = DB()
    conn = db.connect()
    try:
        result = conn.execute(text("SELECT MIN(label), MAX(label) FROM history_insert")).fetchone()
        min_date, max_date = result[0], result[1]
    finally:
        conn.close()

    if date_debut < min_date:
        raise HTTPException(
            status_code=400,
            detail=f"La date de début ({date_debut}) est antérieure à la date la plus ancienne disponible ({min_date})."
        )
    if date_fin > max_date:
        raise HTTPException(
            status_code=400,
            detail=f"La date de fin ({date_fin}) est postérieure à la date la plus récente disponible ({max_date})."
        )

    types = ['dav', 'dat', 'epr', 'decaissement'] if type == "all" else [type]
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for t in types:
            if t == "dav":
                report = DavReport()
            elif t == "dat":
                report = DatReport()
            elif t == "epr":
                report = EprReport()
            elif t == "decaissement":
                report = decaissementReport()
            else:
                continue

            tables = report.getListeDav() if t == "dav" else \
                     report.getListeDat() if t == "dat" else \
                     report.getListeEpr() if t == "epr" else \
                     report.getListeDecaissement() if t == "decaissement" else []

            filtered_tables = [
                table for table in tables
                if len(table) > len(t) + 1 and date_debut <= table.replace(f"{t}_", "") <= date_fin
            ]

            for table_name in filtered_tables:
                data = report.getDav(table_name.replace("dav_", ""))["data"] if t == "dav" else \
                       report.getDat(table_name.replace("dat_", ""))["data"] if t == "dat" else \
                       report.getEpr(table_name.replace("epr_", ""))["data"] if t == "epr" else \
                       report.getDecaissement(table_name.replace("decaissement_", ""))["data"] if t == "decaissement" else []

                if not data:
                    continue

                df = pd.DataFrame(data) 
                file_name = f"{table_name}.{format if format == 'csv' else 'xlsx'}"
                buffer = io.BytesIO() if format == "excel" else io.StringIO()
                if format == "excel":
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    buffer.seek(0)
                    zip_file.writestr(file_name, buffer.read())
                else:
                    df.to_csv(buffer, index=False)
                    zip_file.writestr(file_name, buffer.getvalue())
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=EM_{date_debut}_{date_fin}.zip"}
    )


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
            nom=agence_data.nom
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
