from sqlalchemy import text
from db.db import DB
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
class TransactionController:
    def __init__(self):
        self.db = DB()

    def get_transactions_by_date(self, import_date: str ):
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
                
            """)

            conn = self.db.connect()
            result = conn.execute(query, {
                "import_date": import_date
                
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

    def get_transact_by_saisie(self, saisie_yyyymmdd: str):
        """
        Récupère transactions où `saisie_le` commence par yymmdd correspondant à `saisie_yyyymmdd` (format YYYYMMDD).
        Retour:
          {
            "success": True/False,
            "data": [rows],
            "count": n,
            "start_datetime": "YYYY-MM-DD HH:MM:SS" | None,
            "end_datetime": "YYYY-MM-DD HH:MM:SS" | None,
            "processing_dates": ["YYYY-MM-DD", ...]
          }
        """
        if not re.fullmatch(r"\d{8}", saisie_yyyymmdd):
            return {"success": False, "error": "date saisie invalide, format attendu YYYYMMDD", "data": []}

        processing_date = datetime.strptime(saisie_yyyymmdd, "%Y%m%d").strftime("%Y-%m-%d")
        

        conn = None
        try:
            query = text("""
                SELECT
                    id,
                    account_number,
                    credit_amount,
                    processing_date,
                    pan,
                    rrn,
                    compte_db_cions,
                    saisie_le,
                    import_date,
                    created_at
                FROM transact_t24
                WHERE processing_date = :processing_date
                ORDER BY saisie_le ASC
            """)
            conn = self.db.connect()
            result = conn.execute(query, {"processing_date": processing_date})
            rows = [dict(r) for r in result.mappings().all()]

            # parse saisie_le to datetimes, collect processing_date values
            parsed_datetimes = []
            proc_dates = set()
            for r in rows:
                dt = self._parse_saisie_le(r.get("saisie_le"))
                if dt:
                    parsed_datetimes.append(dt)
                # normalize processing_date to YYYY-MM-DD if present
                pd_raw = r.get("processing_date")
                if pd_raw:
                    try:
                        if isinstance(pd_raw, datetime):
                            pd_str = pd_raw.strftime("%Y-%m-%d")
                        else:
                            pd_str = str(pd_raw).strip()
                        proc_dates.add(pd_str)
                    except Exception:
                        pass

            start_dt = min(parsed_datetimes).strftime("%Y-%m-%d %H:%M:%S") if parsed_datetimes else None
            end_dt = max(parsed_datetimes).strftime("%Y-%m-%d %H:%M:%S") if parsed_datetimes else None

            return {
                "success": True,
                "data": rows,
                "count": len(rows),
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "processing_dates": sorted(list(proc_dates))
            }

        except Exception as e:
            print(f"[ERREUR] get_transact_by_saisie: {e}")
            return {"success": False, "error": str(e), "data": []}
        finally:
            if conn:
                conn.close()               

    def _normalize_pan(self, pan):
        if pan is None:
            return None
        normalized = str(pan).strip().replace(' ', '').replace('-', '').upper()
        return normalized or None

    def _normalize_reference(self, value):
        if value is None:
            return None
        normalized = str(value).strip().replace(' ', '').replace('-', '').upper()
        return normalized or None

    def _normalize_amount(self, value):
        if value is None:
            return None
        s = str(value).strip()
        if s == '':
            return None
        s = s.replace('MGA', '').replace(' ', '').replace(',', '')
        try:
            return str(Decimal(s))
        except InvalidOperation:
            cleaned = re.sub(r'[^0-9.-]', '', s)
            if cleaned == '':
                return None
            try:
                return str(Decimal(cleaned))
            except InvalidOperation:
                return None

    def get_diff(self, processing_date: str):
        """
        Compare les transactions PowerCard et T24 pour une date de traitement donnée.
        Retourne les transactions PowerCard WITHDRAWAL Approved qui n'ont pas de correspondance T24,
        ainsi que les transactions PowerCard WITHDRAWAL non approved qui existent en T24.
        """
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", processing_date):
            return {
                "success": False,
                "error": "Format de date invalide, utilisez YYYY-MM-DD",
                "data": []
            }

        conn = None
        try:
            conn = self.db.connect()
            self._ensure_powercard_processing_date_column(conn)

            query_pc = text("""
                SELECT
                    id,
                    external_stan,
                    reference,
                    processing_code,
                    action,
                    pan,
                    transaction_amount,
                    processing_date,
                    DATE_FORMAT(local_time, '%Y-%m-%d %H:%i:%s') AS local_time,
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM transact_power_card
                WHERE processing_date = :processing_date
                AND processing_code = 'WITHDRAWAL'
            """)

            query_t24 = text("""
                SELECT
                    id,
                    account_number,
                    credit_amount,
                    processing_date,
                    pan,
                    rrn,
                    compte_db_cions,
                    saisie_le,
                    DATE_FORMAT(import_date, '%Y-%m-%d') AS import_date,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at
                FROM transact_t24
                WHERE processing_date = :processing_date
            """)

            pc_rows = [dict(r) for r in conn.execute(query_pc, {"processing_date": processing_date}).mappings().all()]
            t24_rows = [dict(r) for r in conn.execute(query_t24, {"processing_date": processing_date}).mappings().all()]

            t24_index = {}
            t24_by_pan = {}
            t24_by_rrn = {}
            for row in t24_rows:
                rrn_key = self._normalize_reference(row.get('rrn'))
                if rrn_key is not None:
                    t24_by_rrn.setdefault(rrn_key, []).append(row)
                

            diff_rows = []
            for pc in pc_rows:
                action = str(pc.get('action') or '').strip().lower()
                pan_key = self._normalize_pan(pc.get('pan'))
                rrn_key = self._normalize_reference(pc.get('reference'))
                amount_key = self._normalize_amount(pc.get('transaction_amount'))

                # 1) Matching prioritaire par RRN
                matches = t24_by_rrn.get(rrn_key, []) if rrn_key is not None else []
                has_match = len(matches) > 0

                # 2) Verification de coherence du PAN sur les matches trouves
                pan_matches = [m for m in matches if self._normalize_pan(m.get('pan')) == pan_key]
                pan_coherent = len(pan_matches) > 0 if has_match else None

                if action == 'approved' and not has_match:
                    diff_rows.append({
                        'type': 'approved_missing_in_t24',
                        'powercard': pc,
                        't24_matches': []
                    })
                elif action == 'approved' and has_match and not pan_coherent:
                    diff_rows.append({
                        'type': 'pan_incoherent',
                        'powercard': pc,
                        't24_matches': matches
                    })
                elif action != 'approved' and has_match:
                    diff_rows.append({
                        'type': 'nonapproved_present_in_t24',
                        'powercard': pc,
                        't24_matches': matches
                    })

            return {
                'success': True,
                'count': len(diff_rows),
                'data': diff_rows,
                'powercard_count': len(pc_rows),
                't24_count': len(t24_rows)
            }

        except Exception as e:
            print(f"[ERREUR] get_diff: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

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

    def insert_processing_date_to_power(self, saisie_yyyymmdd: str):
        """
        Utilise get_transact_by_saisie() pour récupérer start/end et processing_dates,
        choisit le processing_date le plus fréquent parmi les lignes T24 retournées,
        puis met à jour transact_power_card.local_time entre ces bornes avec processing_date.
        """
        result = self.get_transact_by_saisie(saisie_yyyymmdd)
        if not result.get("success", False):
            return result

        start_dt = result.get("start_datetime")
        end_dt = result.get("end_datetime")
        if not start_dt or not end_dt:
            return {
                "success": False,
                "error": "Impossible de déterminer la plage start/end à partir de T24",
                "data": [],
            }

        # déterminer processing_date à partir des lignes T24 (valeur la plus fréquente)
        processing_date = None
        try:
            rows = result.get("data", []) or []
            counts = {}
            for r in rows:
                pd_raw = r.get("processing_date")
                if not pd_raw:
                    continue
                pd = str(pd_raw).strip()
                # normaliser YYYY-MM-DD si besoin
                if re.fullmatch(r"\d{8}", pd):  # ex 20260705
                    pd = f"{pd[0:4]}-{pd[4:6]}-{pd[6:8]}"
                counts[pd] = counts.get(pd, 0) + 1

            if not counts:
                return {
                    "success": False,
                    "error": "Aucune processing_date trouvée dans les transactions T24 pour la date saisie",
                    "data": [],
                }
            processing_date = max(counts.items(), key=lambda x: x[1])[0]
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la détermination de processing_date : {e}",
                "data": [],
            }
        conn = None
        try:
            conn = self.db.connect()
            self._ensure_powercard_processing_date_column(conn)

            update_sql = text("""
                UPDATE transact_power_card
                SET processing_date = :processing_date
                WHERE local_time BETWEEN :start_dt AND :end_dt
            """)

            result_update = conn.execute(update_sql, {
                "processing_date": processing_date,
                "start_dt": start_dt,
                "end_dt": end_dt
            })
            conn.commit()

            return {
                "success": True,
                "message": "processing_date inséré dans transact_power_card",
                "updated_rows": result_update.rowcount,
                "count": result["count"],
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "processing_dates": result["processing_dates"],
                "processing_date": processing_date
            }

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERREUR] insert_processing_date_to_power: {e}")
            return {"success": False, "error": str(e), "data": []}
        finally:
            if conn:
                conn.close()