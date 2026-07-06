from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import Optional
from controller.PowerCardController import PowerCardController
from controller.importPowerCardController import ImportPowerCardController

router = APIRouter()
power_card_controller = PowerCardController()
import_power_card_controller = ImportPowerCardController()

@router.post("/powercard/import")
async def import_power_card(
    file: UploadFile = File(...),
    import_date: str = Query(..., description="Date d'import au format YYYY-MM-DD")
):
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
    import_date: str = Query(..., description="Date au format YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Récupérer les transactions Power Card pour une date donnée
    """
    try:
        transactions = power_card_controller.get_transactions_by_date(
            import_date, 
            limit=limit, 
            offset=offset
        )
        
        return {
            "status": "success",
            "data": transactions["data"],
            "count": transactions["count"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


api_router_powercard = router
