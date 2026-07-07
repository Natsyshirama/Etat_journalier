from sqlalchemy import text
from db.db import DB

class TransactionController:
    def __init__(self):
        self.db = DB()

    def get_transactions_by_date(self, import_date: str, limit: int = 100, offset: int = 0):
        conn = None
        try:
            query = text("""
                SELECT
                    id,
                    account_number,
                    credit_amount,
                    DATE_FORMAT(processing_date, '%Y-%m-%d') AS processing_date,
                    pan,
                    rrn,
                    compte_db_cions,
                    saisie_le,
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM transact_t24
                WHERE import_date = :import_date
                ORDER BY processing_date DESC
                LIMIT :limit
                OFFSET :offset
            """)

            conn = self.db.connect()
            result = conn.execute(query, {
                "import_date": import_date,
                "limit": limit,
                "offset": offset
            })

            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]

            return {
                "success": True,
                "data": data,
                "count": len(data)
            }

        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les transactions T24 : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")