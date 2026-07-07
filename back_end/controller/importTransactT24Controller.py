import pandas as pd
import re
import io
import math
from fastapi import UploadFile
from sqlalchemy import text
from db.db import DB
from datetime import datetime

class ImportTransactT24Controller:
    def __init__(self):
        self.db = DB()
        self.pattern = re.compile(r"^transact_t24_(\d{8})\.csv$")

    def init_table(self):
        conn = None
        try:
            conn = self.db.connect()
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS transact_t24 (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_number VARCHAR(100),
                    credit_amount VARCHAR(50),
                    processing_date DATE,
                    pan VARCHAR(100),
                    rrn VARCHAR(100),
                    compte_db_cions VARCHAR(100),
                    saisie_le VARCHAR(100),
                    import_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_processing_date (processing_date),
                    INDEX idx_account_number (account_number)
                )
            """)
            conn.execute(create_table_sql)
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _clean_cell(self, value):
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
        except Exception:
            pass
        s = str(value).strip()
        if s == "" or s.lower() in ["nan", "none", "null"]:
            return None
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        if s.startswith('='):
            s = s[1:]
        return s.replace('"', '')

    def read_csv_file(self, file: UploadFile):
        try:
            file.file.seek(0)
            content = file.file.read().decode('utf-8', errors='replace')

            df = pd.read_csv(
                io.StringIO(content),
                sep=',',
                quotechar='"',
                dtype=str,
                keep_default_na=False,
                na_values=[''],
                skipinitialspace=True
            )

            if df.empty:
                return pd.DataFrame()

            df.columns = [
                str(col).strip()
                .replace('"', '')
                .lower()
                .replace(' ', '_')
                .replace('.', '_')
                for col in df.columns
            ]

            for col in df.columns:
                df[col] = df[col].apply(self._clean_cell)

            print(f"[DEBUG] Colonnes trouvées: {list(df.columns)}")
            return df

        except Exception as e:
            print(f"[ERREUR] Lecture CSV: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def convert_processing_date(self, s):
        if not s:
            return None
        s = str(s).strip()
        # expected YYYYMMDD
        if re.fullmatch(r"\d{8}", s):
            try:
                return datetime.strptime(s, "%Y%m%d").strftime("%Y-%m-%d")
            except Exception:
                return None
        # fallback parsing
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        return None

    def _sanitize_val(self, v):
        if v is None:
            return None
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        if isinstance(v, float):
            if math.isnan(v):
                return None
        s = str(v).strip()
        if s == "" or s.lower() in ("nan", "none", "null"):
            return None
        return s

    def insert_data(self, conn, df: pd.DataFrame, import_date: str):
        rows_inserted = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                account_number = row.get("num_compte_credit") or row.get("num_compte") or row.get("num_compte_credit")
                credit_amount = row.get("creditamount") or row.get("credit_amount") or row.get("creditAmount")
                processing_date_raw = row.get("processingdate") or row.get("processing_date")
                pan = row.get("l_at_pan_no")
                rrn = row.get("l_at_rrn")
                compte_db_cions = row.get("compte_db_cions")
                saisie_le = row.get("saisi_le") 

                processing_date = self.convert_processing_date(processing_date_raw)

                params = {
                    "account_number": self._sanitize_val(account_number),
                    "credit_amount": self._sanitize_val(credit_amount),
                    "processing_date": processing_date,
                    "pan": self._sanitize_val(pan),
                    "rrn": self._sanitize_val(rrn),
                    "compte_db_cions": self._sanitize_val(compte_db_cions),
                    "saisie_le": self._sanitize_val(saisie_le),
                    "import_date": import_date
                }

                insert_sql = text("""
                    INSERT INTO transact_t24 (
                        account_number, credit_amount, processing_date,
                        pan, rrn, compte_db_cions, saisie_le, import_date
                    ) VALUES (
                        :account_number, :credit_amount, :processing_date,
                        :pan, :rrn, :compte_db_cions, :saisie_le, :import_date
                    )
                """)
                conn.execute(insert_sql, params)
                rows_inserted += 1

            except Exception as e:
                errors.append(f"Ligne {idx+2}: {e}")
                print(f"[ERREUR] Ligne {idx+2}: {e}")
                try:
                    print({k: repr(v) for k, v in params.items()})
                except Exception:
                    pass

        return rows_inserted, errors

    def validate_filename(self, filename: str):
        match = self.pattern.match(filename)
        if not match:
            # accept any filename if you prefer; keep strict name optional
            return None
        return match.group(1)

    def process_file(self, file: UploadFile, import_date: str):
        errors = []
        success = []
        rows_inserted = 0

        try:
            df = self.read_csv_file(file)

            if df.empty:
                return {
                    "filename": file.filename,
                    "success": False,
                    "messages": ["Le fichier est vide ou illisible"],
                    "rows_inserted": 0,
                    "error_count": 1
                }

            conn = self.db.connect()
            try:
                self.init_table()
                rows_inserted, insert_errors = self.insert_data(conn, df, import_date)
                if insert_errors:
                    errors.extend(insert_errors)
                conn.commit()
                success.append(f"Import réussi : {file.filename} ({rows_inserted} transactions importées)")
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

        except Exception as e:
            errors.append(f"Erreur import {file.filename} : {e}")

        return {
            "filename": file.filename,
            "success": len(success) > 0,
            "messages": success + errors,
            "rows_inserted": rows_inserted,
            "error_count": len(errors)
        }