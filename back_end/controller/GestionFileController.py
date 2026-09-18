from datetime import datetime
from sqlalchemy import text
from db.db import DB


class GestionFileController:
    def __init__(self):
        self.db = DB()

    def deleteByimportDate(self, source: str, date: str):
        conn = None

        tables = {
            "t24": "transact_t24",
            "powercard": "transact_power_card",
            "pc": "transact_power_card"
        }

        normalized_source = source.strip().lower()

        if normalized_source not in tables:
            return {
                "success": False,
                "error": "Source invalide. Utilisez 't24' ou 'powercard'",
                "deleted_count": 0
            }

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "Format de date invalide. Utilisez YYYY-MM-DD",
                "deleted_count": 0
            }

        conn = self.db.connect()

        try:
            table_name = tables[normalized_source]

            query = text(f"""
                DELETE FROM {table_name}
                WHERE import_date = :import_date
            """)

            result = conn.execute(query, {"import_date": date})
            conn.commit()

            return {
                "success": True,
                "source": normalized_source,
                "import_date": date,
                "deleted_count": result.rowcount
            }

        except Exception as error:
            conn.rollback()

            print(
                f"[ERREUR] Suppression import {normalized_source} "
                f"du {date}: {error}"
            )

            return {
                "success": False,
                "error": str(error),
                "deleted_count": 0
            }

        finally:
            conn.close()

    def getTransactByImportDateT24(self):
        conn = None

        try:
            conn = self.db.connect()

            query = text("""
                SELECT
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(
                        MIN(created_at),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS created_at,
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
                    "created_at": row["created_at"],
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
                        MIN(created_at),
                        '%Y-%m-%d %H:%i:%s'
                    ) AS created_at,
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
                    "created_at": row["created_at"],
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