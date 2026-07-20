from sqlalchemy import text
from db.db import DB
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from controller.transactionController import TransactionController

class TransactionManyController:
    def __init__(self):
        self.db = DB()
    
    def _parse_saisie_le(self, s):
        """Parse saisie_le format yymmddhhmm (ex: 2607050833 -> 2026-07-05 08:33)."""
        if not s:
            return None
        s = str(s).strip()
        # accept 10 digits; if longer, take leftmost 10
        if not re.fullmatch(r"\d{10,}", s):
            return None
        s = s[:10]
        try:
            yy = int(s[0:2])
            year = 2000 + yy
            month = int(s[2:4])
            day = int(s[4:6])
            hour = int(s[6:8])
            minute = int(s[8:10])
            return datetime(year, month, day, hour, minute)
        except Exception:
            return None

    def get_transact_by_saisie_many(self, start_yyyymmdd: str, end_yyyymmdd: str):
        if not re.fullmatch(r"\d{8}", start_yyyymmdd) or not re.fullmatch(r"\d{8}", end_yyyymmdd):
            return {"success": False, "error": "Format date invalide, utilisez YYYYMMDD", "data": []}

        start_date = datetime.strptime(start_yyyymmdd, "%Y%m%d").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_yyyymmdd, "%Y%m%d").strftime("%Y-%m-%d")

        conn = None
        try:
            query = text("""
                SELECT
                    processing_date,
                    saisie_le
                FROM transact_t24
                WHERE processing_date BETWEEN :start_date AND :end_date
                ORDER BY processing_date ASC, saisie_le ASC
            """)

            conn = self.db.connect()
            rows = [dict(r) for r in conn.execute(query, {"start_date": start_date, "end_date": end_date}).mappings().all()]

            groups = {}
            for row in rows:
                pd_raw = row.get("processing_date")
                if not pd_raw:
                    continue

                if isinstance(pd_raw, datetime):
                    pd = pd_raw.strftime("%Y-%m-%d")
                else:
                    pd = str(pd_raw).strip()

                dt = self._parse_saisie_le(row.get("saisie_le"))
                if dt is None:
                    continue

                dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                item = groups.setdefault(pd, {
                    "processing_date": pd,
                    "count": 0,
                    "start_datetime": None,
                    "end_datetime": None
                })

                item["count"] += 1
                if item["start_datetime"] is None or dt_str < item["start_datetime"]:
                    item["start_datetime"] = dt_str
                if item["end_datetime"] is None or dt_str > item["end_datetime"]:
                    item["end_datetime"] = dt_str

            return {"success": True, "data": list(groups.values()), "count": len(groups)}
        except Exception as e:
            print(f"[ERREUR] get_transact_by_saisie_many: {e}")
            return {"success": False, "error": str(e), "data": []}
        finally:
            if conn:
                conn.close()

    def _ensure_powercard_processing_date_column(self, conn):
        exists = conn.execute(
            text("SHOW COLUMNS FROM transact_power_card LIKE 'processing_date'")
        ).fetchone()
        if not exists:
            conn.execute(
                text("ALTER TABLE transact_power_card ADD COLUMN processing_date DATE")
            )

    def insert_processing_date_to_power_many(self, start_yyyymmdd: str, end_yyyymmdd: str):
        result = self.get_transact_by_saisie_many(start_yyyymmdd, end_yyyymmdd)
        if not result.get("success", False):
            return result

        periods = result.get("data", [])
        if not periods:
            return {"success": True, "message": "Aucune période T24 trouvée", "processed": []}

        conn = None
        processed = []
        try:
            conn = self.db.connect()
            self._ensure_powercard_processing_date_column(conn)

            previous_end = None
            for period in periods:
                processing_date = period["processing_date"]
                start_dt = period["start_datetime"]
                end_dt = period["end_datetime"]

                if not start_dt or not end_dt:
                    continue

                count_sql = text("""
                    SELECT COUNT(*) AS cnt
                    FROM transact_power_card
                    WHERE local_time BETWEEN :start_dt AND :end_dt
                """)
                count_row = conn.execute(count_sql, {
                    "start_dt": start_dt,
                    "end_dt": end_dt
                }).fetchone()
                total_in_range = int(count_row[0]) if count_row and count_row[0] is not None else 0

                warning = None
                if total_in_range == 0:
                    warning = f"Aucune transaction PowerCard trouvée entre {start_dt} et {end_dt}"

                exact_sql = text("""
                    UPDATE transact_power_card
                    SET processing_date = :processing_date
                    WHERE local_time BETWEEN :start_dt AND :end_dt
                    AND processing_date IS NULL
                """)
                exact_result = conn.execute(exact_sql, {
                    "processing_date": processing_date,
                    "start_dt": start_dt,
                    "end_dt": end_dt
                })
                exact_count = exact_result.rowcount

                auto_count = 0
                if previous_end is not None:
                    auto_sql = text("""
                        UPDATE transact_power_card
                        SET processing_date = :processing_date
                        WHERE local_time > :previous_end
                          AND local_time <= :end_dt
                          AND processing_date IS NULL
                    """)
                    auto_result = conn.execute(auto_sql, {
                        "processing_date": processing_date,
                        "previous_end": previous_end,
                        "end_dt": end_dt
                    })
                    auto_count = auto_result.rowcount

                processed.append({
                    "processing_date": processing_date,
                    "start_datetime": start_dt,
                    "end_datetime": end_dt,
                    "rows_in_range": total_in_range,
                    "warning": warning,
                    "exact_updated_rows": exact_count,
                    "auto_updated_rows": auto_count,
                    "total_updated_rows": exact_count + auto_count
                })

                previous_end = end_dt

            conn.commit()
            return {"success": True, "processed": processed}

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERREUR] insert_processing_date_to_power_many: {e}")
            return {"success": False, "error": str(e), "processed": []}
        finally:
            if conn:
                conn.close()

    def get_liste_processing_date(self, start_yyyymmdd: str, end_yyyymmdd: str):
        # wrapper réutilisant la fonction existante
        return self.get_transact_by_saisie_many(start_yyyymmdd, end_yyyymmdd)
    
    def get_diff_many(self, start_yyyymmdd: str, end_yyyymmdd: str):
        
        liste = self.get_liste_processing_date(start_yyyymmdd, end_yyyymmdd)
        if not liste.get("success", False):
            return {"success": False, "error": liste.get("error", "Erreur obtention périodes"), "periods": []}

        periods = liste.get("data", [])
        if not periods:
            return {
                "success": True,
                "periods": [],
                "message": "Aucune période T24 trouvée pour cet intervalle"
            }
        tc = TransactionController()
        out = []

        for p in periods:
            pd = p.get("processing_date")
            if not pd:
                continue
            # reuse existing get_diff which expects 'YYYY-MM-DD'
            diff_result = tc.get_diff(pd)
            # always attach processing_date to the returned block
            out.append({
                "processing_date": pd,
                "t24_period": {
                    "start_datetime": p.get("start_datetime"),
                    "end_datetime": p.get("end_datetime"),
                    "count": p.get("count")
                },
                "diff": diff_result
            })

        return {"success": True, "periods": out}