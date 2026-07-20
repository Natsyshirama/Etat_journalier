from sqlalchemy import text
from db.db import DB

class PowerCardController:
    def __init__(self):
        self.db = DB()

        

    def get_transact_by_reference(self, reference: str):
        if not reference or not str(reference).strip():
            return {"success": False, "error": "Reference vide", "data": []}

        ref = str(reference).strip()

        conn = None
        try:
            query = text("""
                SELECT
                    id,
                    external_stan,
                    reference,
                    source,
                    destination,
                    message,
                    processing_code,
                    action,
                    pan,
                    DATE_FORMAT(local_time, '%Y-%m-%d %H:%i:%s') AS local_time,
                    DATE_FORMAT(internal_time, '%Y-%m-%d %H:%i:%s') AS internal_time,
                    transaction_amount,
                    terminal_no,
                    acceptor_point,
                    authorization_reference,
                    current_table_indicator,
                    source_account_number,
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM transact_power_card
                WHERE reference = :reference
                ORDER BY local_time DESC
            """)

            conn = self.db.connect()
            result = conn.execute(query, {"reference": ref})

            rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]

            return {
                "success": True,
                "data": rows,
                "count": len(rows)
            }

        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer la transaction Power Card par référence : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
        finally:
            if conn:
                conn.close()


    def get_transactions_by_date(self, local_time: str, limit: int = 100, offset: int = 0):
        """
        Récupérer les transactions Power Card pour une date donnée
        """
        conn = None
        try:
            query = text("""
                SELECT
                    id,
                    external_stan,
                    reference,
                    source,
                    destination,
                    message,
                    processing_code,
                    action,
                    pan,
                    DATE_FORMAT(local_time, '%Y-%m-%d %H:%i:%s') AS local_time,
                    DATE_FORMAT(internal_time, '%Y-%m-%d %H:%i:%s') AS internal_time,
                    transaction_amount,
                    terminal_no,
                    acceptor_point,
                    authorization_reference,
                    current_table_indicator,
                    source_account_number,
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM transact_power_card
                WHERE local_time LIKE :local_time
                ORDER BY local_time DESC
                LIMIT :limit
                OFFSET :offset
            """)

            conn = self.db.connect()
            result = conn.execute(query, {
                "local_time": f"{local_time}%",
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
            print(f"[ERREUR] Impossible de récupérer les transactions Power Card : {e}")
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

    
    _AMOUNT_EXPR = """
        CAST(
            REPLACE(REPLACE(transaction_amount, ',', ''), ' MGA', '')
            AS DECIMAL(18,2)
        )
    """
    def get_power_card_stats(self, import_date: str = None):
        conn = None

        try:
            conn = self.db.connect()

            if import_date:
                return self._get_stats_for_date(conn, import_date)
            else:
                return self._get_stats_all_dates(conn)

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

        finally:
            if conn:
                conn.close()

    def _get_stats_for_date(self, conn, local_date):
        global_query = text(f"""
            SELECT
                COUNT(*) AS withdrawal_total_transactions,
                SUM({self._AMOUNT_EXPR}) AS withdrawal_total_amount
            FROM transact_power_card
            WHERE processing_code='WITHDRAWAL'
            AND DATE(local_time) LIKE :local_date
        """)

        stats = dict(conn.execute(global_query, {"local_date": local_date}).mappings().first() or {})

        action_query = text(f"""
            SELECT
                action,
                COUNT(*) AS count,
                SUM({self._AMOUNT_EXPR}) AS amount
            FROM transact_power_card
            WHERE processing_code='WITHDRAWAL'
            AND DATE(local_time) LIKE :local_date
            AND action IN (
                'Approved',
                'non approuved',
                'Canceled',
                'Exceeds withdrawal limit',
                'Issuer not available',
                'No sufficient funds',
                'Rejected',
                'Reversal accepted'
            )
            GROUP BY action
            ORDER BY count DESC
        """)

        stats["actions"] = [dict(r) for r in conn.execute(action_query, {"local_date": local_date}).mappings().all()]

        return {
            "success": True,
            "data": stats
        }

    def _get_stats_all_dates(self, conn):
        
        global_query = text(f"""
            SELECT
                COUNT(*) AS withdrawal_total_transactions,
                SUM({self._AMOUNT_EXPR}) AS withdrawal_total_amount
            FROM transact_power_card
            WHERE processing_code='WITHDRAWAL'
        """)

        stats = dict(conn.execute(global_query).mappings().first() or {})

        action_query = text(f"""
            SELECT
                action,
                COUNT(*) AS count,
                SUM({self._AMOUNT_EXPR}) AS amount
            FROM transact_power_card
            WHERE processing_code='WITHDRAWAL'
                AND action IN (
                'Approved',
                'non approuved',
                'Canceled',
                'Exceeds withdrawal limit',
                'Issuer not available',
                'No sufficient funds',
                'Rejected',
                'Reversal accepted'
                )
            GROUP BY action
            ORDER BY count DESC
        """)

        stats["actions"] = [dict(r) for r in conn.execute(action_query).mappings().all()]

        return {
            "success": True,
            "data": stats
        }
 