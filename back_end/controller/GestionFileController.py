from sqlalchemy import text
from db.db import DB


class GestionFileController:
    def __init__(self):
        self.db = DB()

    def getTransactByImportDateT24(self):
        conn = None

        try:
            conn = self.db.connect()

            query = text("""
                SELECT
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    COUNT(*) AS row_count,
                    DATE_FORMAT(
                        MIN(
                            STR_TO_DATE(
                                LEFT(saisie_le, 10),
                                '%y%m%d%H%i'
                            )
                        ),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS start_datetime,
                    DATE_FORMAT(
                        MAX(
                            STR_TO_DATE(
                                LEFT(saisie_le, 10),
                                '%y%m%d%H%i'
                            )
                        ),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS end_datetime
                FROM transact_t24
                GROUP BY import_date
                ORDER BY import_date DESC
            """)

            rows = conn.execute(query).mappings().all()

            data = [
                {
                    "import_date": row["import_date"],
                    "row_count": int(row["row_count"] or 0),
                    "start_datetime": row["start_datetime"],
                    "end_datetime": row["end_datetime"]
                }
                for row in rows
            ]

            return {
                "success": True,
                "data": data,
                "count": len(data)
            }

        except Exception as error:
            print(f"[ERREUR] Statistiques import T24: {error}")
            return {
                "success": False,
                "error": str(error),
                "data": []
            }

        finally:
            if conn:
                conn.close()

    def getTransactByImportDatePc(self):
        conn = None

        try:
            conn = self.db.connect()

            query = text("""
                SELECT
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    COUNT(*) AS row_count,
                    DATE_FORMAT(
                        MIN(local_time),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS start_datetime,
                    DATE_FORMAT(
                        MAX(local_time),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS end_datetime
                FROM transact_power_card
                GROUP BY import_date
                ORDER BY import_date DESC
            """)

            rows = conn.execute(query).mappings().all()

            data = [
                {
                    "import_date": row["import_date"],
                    "row_count": int(row["row_count"] or 0),
                    "start_datetime": row["start_datetime"],
                    "end_datetime": row["end_datetime"]
                }
                for row in rows
            ]

            return {
                "success": True,
                "data": data,
                "count": len(data)
            }

        except Exception as error:
            print(f"[ERREUR] Statistiques import PowerCard: {error}")
            return {
                "success": False,
                "error": str(error),
                "data": []
            }

        finally:
            if conn:
                conn.close()