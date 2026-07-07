import pandas as pd
import re
import io
from fastapi import UploadFile
from sqlalchemy import text
from db.db import DB
from datetime import datetime

class ImportPowerCardController:
    def __init__(self):
        self.db = DB()
        self.pattern = re.compile(r"^powercard_(\d{8})\.csv$")

    def init_table(self):
        """Créer la table transact_power_card si elle n'existe pas"""
        conn = None
        try:
            conn = self.db.connect()
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS transact_power_card (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    external_stan VARCHAR(50),
                    reference VARCHAR(100),
                    source VARCHAR(100),
                    destination VARCHAR(100),
                    message VARCHAR(255),
                    processing_code VARCHAR(50),
                    action VARCHAR(50),
                    pan VARCHAR(100),
                    local_time DATETIME,
                    internal_time DATETIME,
                    transaction_amount VARCHAR(50),
                    terminal_no VARCHAR(50),
                    acceptor_point VARCHAR(50),
                    authorization_reference VARCHAR(100),
                    current_table_indicator VARCHAR(50),
                    source_account_number VARCHAR(100),
                    import_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_import_date (import_date),
                    INDEX idx_reference (reference),
                    INDEX idx_pan (pan)
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

    def _normalize_powercard_csv(self, content: str) -> str:
        """Normaliser le contenu d'un fichier CSV PowerCard"""
        lines = []
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]

            line = line.replace('""', '"')
            lines.append(line)

        return "\n".join(lines)

    def _clean_cell(self, value):
        """Nettoyer une cellule individuelle"""
        if value is None or pd.isna(value) or value == '':
            return None
        s = str(value).strip()
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        if s.startswith('='):
            s = s[1:]
        s = s.replace('"', '')
        if s == '' or s.lower() in ['nan', 'null', 'none']:
            return None
        return s

    def read_csv_file(self, file: UploadFile):
        """Lire le fichier CSV avec pd.read_csv adapté au format PowerCard"""
        try:
            file.file.seek(0)
            content = file.file.read().decode('utf-8', errors='replace')
            content = self._normalize_powercard_csv(content)

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
                .replace('.', '')
                .replace('é', 'e')
                .replace('è', 'e')
                .replace('à', 'a')
                .replace('ô', 'o')
                .replace('î', 'i')
                for col in df.columns
            ]

            for col in df.columns:
                df[col] = df[col].apply(self._clean_cell)

            print(f"[DEBUG] Colonnes trouvées: {list(df.columns)}")
            if not df.empty:
                print(f"[DEBUG] Première ligne: {df.iloc[0].to_dict()}")
                print(f"[DEBUG] Nombre total de lignes: {len(df)}")

            return df

        except Exception as e:
            print(f"[ERREUR] Lecture CSV: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def convert_datetime(self, date_str):
        """Convertir une date du format MM/DD/YYYY HH:MM:SS vers YYYY-MM-DD HH:MM:SS"""
        if not date_str or date_str in ['None', 'null', '']:
            return None
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                print(f"[WARN] Format de date non reconnu: {date_str}")
                return None

    def insert_data(self, conn, df: pd.DataFrame, import_date: str):
        """Insérer les données dans la table transact_power_card"""
        rows_inserted = 0
        errors = []

        print(f"[DEBUG] Colonnes disponibles: {list(df.columns)}")

        for idx, row in df.iterrows():
            try:

                params = {
                    "external_stan": row.get("external_stan"),
                    "reference": row.get("reference"),
                    "source": row.get("source"),
                    "destination": row.get("destination"),
                    "message": row.get("message"),
                    "processing_code": row.get("processing_code"),
                    "action": row.get("action"),
                    "pan": row.get("pan"),
                    "local_time": self.convert_datetime(row.get("local_time")),
                    "internal_time": self.convert_datetime(row.get("internal_time")),
                    "transaction_amount": row.get("transaction_amount"),
                    "terminal_no": row.get("terminal_no"),
                    "acceptor_point": row.get("acceptor_point"),
                    "authorization_reference": row.get("authorization_reference"),
                    "current_table_indicator": row.get("current_table_indicator"),
                    "source_account_number": row.get("source_account_number"),
                    "import_date": import_date
                }

                # ======================================================
                # Nettoyage COMPLET des valeurs avant insertion
                # ======================================================

                for key, value in params.items():

                    if value is None:
                        params[key] = None
                        continue

                    # Cas numpy.nan
                    try:
                        if pd.isna(value):
                            params[key] = None
                            continue
                    except Exception:
                        pass

                    # Cas float nan
                    if isinstance(value, float):
                        if math.isnan(value):
                            params[key] = None
                            continue

                    # Cas chaîne
                    if isinstance(value, str):

                        value = value.strip()

                        if value == "":
                            params[key] = None
                            continue

                        if value.lower() in ("nan", "none", "null"):
                            params[key] = None
                            continue

                        params[key] = value

                insert_sql = text("""
                    INSERT INTO transact_power_card (
                        external_stan,
                        reference,
                        source,
                        destination,
                        message,
                        processing_code,
                        action,
                        pan,
                        local_time,
                        internal_time,
                        transaction_amount,
                        terminal_no,
                        acceptor_point,
                        authorization_reference,
                        current_table_indicator,
                        source_account_number,
                        import_date
                    )
                    VALUES (
                        :external_stan,
                        :reference,
                        :source,
                        :destination,
                        :message,
                        :processing_code,
                        :action,
                        :pan,
                        :local_time,
                        :internal_time,
                        :transaction_amount,
                        :terminal_no,
                        :acceptor_point,
                        :authorization_reference,
                        :current_table_indicator,
                        :source_account_number,
                        :import_date
                    )
                """)

                conn.execute(insert_sql, params)

                rows_inserted += 1

            except Exception as e:

                errors.append(f"Ligne {idx+2}: {e}")

                print(f"\n==============================")
                print(f"ERREUR Ligne {idx+2}")
                print("==============================")

                for k, v in params.items():
                    print(f"{k} = {repr(v)}")

                print(e)
                print("==============================\n")

        return rows_inserted, errors

    def validate_filename(self, filename: str):
        """Valider le nom du fichier selon le pattern"""
        match = self.pattern.match(filename)
        if not match:
            raise ValueError(f"Nom de fichier invalide. Format attendu: powercard_YYYYMMDD.csv. Reçu: {filename}")
        return match.group(1)

    def process_file(self, file: UploadFile, import_date: str):
        """Traiter un seul fichier d'import Power Card"""
        errors = []
        success = []
        rows_inserted = 0

        try:
            date_str = self.validate_filename(file.filename)
            df = self.read_csv_file(file)

            if df.empty:
                return {
                    "filename": file.filename,
                    "success": False,
                    "messages": ["Le fichier est vide"],
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

        except ValueError as ve:
            errors.append(str(ve))
        except Exception as e:
            errors.append(f"Erreur import {file.filename} : {e}")

        return {
            "filename": file.filename,
            "success": len(success) > 0,
            "messages": success + errors,
            "rows_inserted": rows_inserted,
            "error_count": len(errors)
        }
