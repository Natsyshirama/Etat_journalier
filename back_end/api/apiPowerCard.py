from fastapi import APIRouter, HTTPException, UploadFile, File, Query,Request
from typing import Optional
from controller.PowerCardController import PowerCardController
from controller.importPowerCardController import ImportPowerCardController
from controller.importTransactT24Controller import ImportTransactT24Controller
from controller.Users import Users

router = APIRouter()
power_card_controller = PowerCardController()
import_power_card_controller = ImportPowerCardController()
import_t24 = ImportTransactT24Controller()

user = Users()

def require_admin(request: Request):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs"
        )

    return current_user


@router.get("/powercard/last_local_time")
async def get_powercard_last_local_time():
    try:
        result = import_power_card_controller.get_last_local_time()

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "last_local_time": result["data"]
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powercard/import")
async def import_power_card(
    request: Request,
    file: UploadFile = File(...),
    import_date: str = Query(..., description="Date d'import au format YYYY-MM-DD")
):
    require_admin(request)
    """
    Importer un fichier Power Card
    
    Format du fichier: powercard_YYYYMMDD.csv
    Paramètre import_date: YYYY-MM-DD
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Aucun fichier fourni")
        
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")
        
        # Valider le format de la date
        from datetime import datetime
        try:
            datetime.strptime(import_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        
        result = import_power_card_controller.process_file(file, import_date)
        
        return {
            "status": "success" if result["success"] else "error",
            "data": result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/t24/last_saisie_le")
async def get_t24_last_saisie_le():
    try:
        result = transaction_controller.get_last_saisie_le()
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result["data"]
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/t24/import")
async def import_transaction_t24(
    request: Request,
    file: UploadFile = File(...),
    import_date: str = Query(..., description="Date d'import au format YYYY-MM-DD")
):
    require_admin(request)

    """
    Importer un fichier T24
    
    Format du fichier: t24_YYYYMMDD.csv
    Paramètre import_date: YYYY-MM-DD
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Aucun fichier fourni")
        
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")
        
        # Valider le format de la date
        from datetime import datetime
        try:
            datetime.strptime(import_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        
        result = import_t24.process_file(file, import_date)
        
        return {
            "status": "success" if result["success"] else "error",
            "data": result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/powercard/transactions/by_reference")
async def get_powercard_transactions_by_reference(
    reference: str = Query(..., description="Référence de transaction Power Card")
):
    """
    Récupérer les transactions Power Card par référence.
    """
    try:
        result = power_card_controller.get_transact_by_reference(reference)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result["data"],
            "count": result.get("count", 0)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/powercard/stats")
async def get_power_card_stats(import_date: Optional[str] = Query(None, description="Date au format YYYY-MM-DD")):
    try:
        stats = power_card_controller.get_power_card_stats(import_date)

        if not stats.get("success", False):
            raise HTTPException(status_code=500, detail=stats.get("error", "Erreur lors de la récupération des stats"))

        return {
            "status": "success",
            "data": stats["data"]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/powercard/transactions")
async def get_transactions(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Récupérer les transactions Power Card pour une date donnée
    """
    try:
        from datetime import datetime
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        

        result = power_card_controller.get_transactions_by_date(
            start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result["data"],
            "count": result["count"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from controller.transactionController import TransactionController
transaction_controller = TransactionController()

@router.get("/t24/transactions")
async def get_t24_transactions(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD")
):
    try:
        from datetime import datetime
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

        result = transaction_controller.get_transactions_by_date(start_date, end_date=end_date)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result["data"],
            "count": result.get("count", 0),
            "start_datetime": result.get("start_datetime"),
            "end_datetime": result.get("end_datetime")
                }
        

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/t24/transactions/by_reference")
async def get_t24_transactions_by_reference(
    reference: str = Query(..., description="Référence T24 à rechercher (RRN)")
):
    """
    Récupérer les transactions T24 par référence.
    """
    try:
        result = transaction_controller.get_transactions_by_reference(reference)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result["data"],
            "count": result.get("count", 0)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/t24/by_saisie")
async def get_t24_by_saisie(
    saisie: str = Query(..., description="Date saisie au format YYYYMMDD (ex: 20260705)")
):
    """
    Récupérer les transactions T24 par préfixe `saisie_le` (format stocké: yymmddhhmm).
    Retourne les transactions, start_datetime, end_datetime et processing_dates.
    """
    try:
        # validation basique du format YYYYMMDD
        from datetime import datetime
        try:
            datetime.strptime(saisie, "%Y%m%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format invalide. Utilisez YYYYMMDD")

        result = transaction_controller.get_transact_by_saisie(saisie)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {
            "status": "success",
            "data": result
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/t24/insert_processing_date")
async def insert_t24_processing_date(
    saisie: str = Query(..., description="Date saisie au format YYYYMMDD")
):
    try:
        from datetime import datetime
        try:
            datetime.strptime(saisie, "%Y%m%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format invalide. Utilisez YYYYMMDD")

        result = transaction_controller.insert_processing_date_to_power(saisie)
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/t24/diff")
async def get_t24_diff(
    processing_date: str = Query(..., description="Date de traitement au format YYYY-MM-DD")
):
    try:
        from datetime import datetime
        try:
            datetime.strptime(processing_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format invalide. Utilisez YYYY-MM-DD")

        result = transaction_controller.get_diff(processing_date)
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur interne"))

        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

api_router_powercard = router
