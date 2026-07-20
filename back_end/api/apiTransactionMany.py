from fastapi import APIRouter, HTTPException, Query
from controller.transactionManyController import TransactionManyController

router = APIRouter()
transaction_many_controller = TransactionManyController()

@router.get("/t24/transactions/by_saisie_range")
async def get_t24_by_saisie_range(
    start_date: str = Query(..., description="Date de début YYYYMMDD"),
    end_date: str = Query(..., description="Date de fin YYYYMMDD")
):
    try:
        result = transaction_many_controller.get_transact_by_saisie_many(start_date, end_date)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur interne"))
        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/t24/insert_processing_date_to_power_many")
async def insert_processing_date_to_power_many(
    start_date: str = Query(..., description="Date de début YYYYMMDD"),
    end_date: str = Query(..., description="Date de fin YYYYMMDD")
):
    try:
        result = transaction_many_controller.insert_processing_date_to_power_many(start_date, end_date)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur interne"))
        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/t24/diff_many")
async def get_t24_diff_many(
    start_date: str = Query(..., description="Date de début YYYYMMDD"),
    end_date: str = Query(..., description="Date de fin YYYYMMDD")
):
    try:
        result = transaction_many_controller.get_diff_many(start_date, end_date)
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur interne"))
        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

api_router_transaction_many = router