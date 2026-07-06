import pandas as pd
import numpy as np
import re
from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from db.db import DB
from datetime import datetime

class PowerCardController:
    def __init__(self):
        self.db = DB()
        # Pattern: powercard_YYYYMMDD.csv
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
            print("[INFO] Table 'transact_power_card' créée ou déjà existante")
            return True
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table transact_power_card : {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def validate_filename(self, filename: str):
        """Valider le nom du fichier selon le pattern"""
        match = self.pattern.match(filename)
        if not match:
            raise ValueError(f"Nom de fichier invalide. Format attendu: powercard_YYYYMMDD.csv. Reçu: {filename}")
        return match.group(1)
    
    def read_csv_file(self, file: UploadFile):
        """Lire et parser les CSV mal formatés (champs =\"\"...\"\"), retourner DataFrame str."""
        try:
            file.file.seek(0)
            content = file.file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            import io, csv
            reader = csv.reader(io.StringIO(content), delimiter=',', quotechar='"', skipinitialspace=True)
            rows = []
            for row in reader:
                # supprimer préfixes '=' et guillemets résiduels sur chaque cellule
                cleaned = []
                for cell in row:
                    if not isinstance(cell, str):
                        cleaned.append(cell)
                        continue
                    c = cell.strip()
                    c = re.sub(r'^\=+','', c)        # supprime leading '=' si présent
                    c = re.sub(r'^"+|"+$','', c)     # supprime guillemets en bordure
                    cleaned.append(c)
                rows.append(cleaned)
            if not rows:
                return pd.DataFrame()
            header = [h.strip() for h in rows[0]]
            df = pd.DataFrame(rows[1:], columns=header)
            # forcer tout en str pour éviter conversion scientifique
            df = df.astype(object).where(pd.notnull(df), None)
            return df
        except Exception as e:
            raise ValueError(f"Erreur lecture CSV {getattr(file,'filename', '')} : {e}")
    
    def clean_dataframe(self, df: pd.DataFrame):
        """Nettoyer noms de colonnes et valeurs; conserver strings propres."""
        if df.empty:
            raise ValueError("DataFrame vide")

        # nettoyer noms de colonnes (enlever guillemets/espaces, accents)
        cols = []
        for col in df.columns:
            c = str(col).strip()
            c = re.sub(r'^"+|"+$','', c)
            c = c.lower().replace(" ", "_")
            c = c.replace("é", "e").replace("è", "e").replace("à", "a").replace("ç", "c").replace("ô", "o").replace("î", "i")
            cols.append(c)
        df.columns = cols

        # nettoyer toutes les cellules: enlever guillemets restants, '=' initial, trim
        def _clean_cell(x):
            if x is None:
                return None
            s = str(x).strip()
            s = re.sub(r'^\=+','', s)
            s = re.sub(r'^"+|"+$','', s)
            if s.lower() in ["nan", "null", "none", ""]:
                return None
            return s

        df = df.applymap(_clean_cell)

        return df
    
    def insert_data(self, conn, df: pd.DataFrame, import_date: str):
        """Insérer les données dans la table transact_power_card"""
        rows_inserted = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                clean_row = {
                    k: (None if v is None or str(v).lower() in ["nan", "null", ""] else str(v).strip())
                    for k, v in row.items()
                }
                
                # Convertir les dates du format MM/DD/YYYY HH:MM au format YYYY-MM-DD HH:MM:SS
                def convert_datetime(date_str):
                    if not date_str or date_str.lower() in ['none', 'nan', 'null', '']:
                        return None
                    try:
                        # Format CSV: 07/05/2026 15:28
                        from datetime import datetime
                        dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
                        # Convertir en format MySQL: 2026-07-05 15:28:00
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"[WARN] Format de date non reconnu: {date_str}, erreur: {e}")
                        return None
                
                # Renommer les colonnes pour correspondre à la table SQL
                mapped_row = {
                    "external_stan": clean_row.get("external_stan"),
                    "reference": clean_row.get("reference"),
                    "source": clean_row.get("source"),
                    "destination": clean_row.get("destination"),
                    "message": clean_row.get("message"),
                    "processing_code": clean_row.get("processing_code"),
                    "action": clean_row.get("action"),
                    "pan": clean_row.get("pan"),
                    "local_time": convert_datetime(clean_row.get("local_time")),
                    "internal_time": convert_datetime(clean_row.get("internal_time")),
                    "transaction_amount": clean_row.get("transaction_amount"),
                    "terminal_no": clean_row.get("terminal_no"),
                    "acceptor_point": clean_row.get("acceptor_point"),
                    "authorization_reference": clean_row.get("authorization_reference"),
                    "current_table_indicator": clean_row.get("current_table_indicator"),
                    "source_account_number": clean_row.get("source_account_number"),
                    "import_date": import_date
                }
                
                # après avoir construit mapped_row
                pc = mapped_row.get("processing_code") or ""
                if str(pc).strip().upper() != "WITHDRAWAL":
                    # ignorer la ligne si ce n'est pas une WITHDRAWAL
                    continue
                # puis exécuter l'INSERT comme avant
                insert_sql = text("""
                    INSERT INTO transact_power_card (
                        external_stan, reference, source, destination, message, 
                        processing_code, action, pan, local_time, internal_time,
                        transaction_amount, terminal_no, acceptor_point, 
                        authorization_reference, current_table_indicator, 
                        source_account_number, import_date
                    ) VALUES (
                        :external_stan, :reference, :source, :destination, :message,
                        :processing_code, :action, :pan, :local_time, :internal_time,
                        :transaction_amount, :terminal_no, :acceptor_point,
                        :authorization_reference, :current_table_indicator,
                        :source_account_number, :import_date
                    )
                """)
                
                conn.execute(insert_sql, mapped_row)
                rows_inserted += 1
                
            except Exception as e:
                error_msg = f"Ligne {idx + 2}: {str(e)}"
                errors.append(error_msg)
                print(f"[ERREUR] {error_msg}")
        
        return rows_inserted, errors
    
    def process_file(self, file: UploadFile, import_date: str):
        """Traiter un seul fichier d'import Power Card"""
        errors = []
        success = []
        rows_inserted = 0
        
        try:
            # Valider le nom du fichier
            date_str = self.validate_filename(file.filename)
            
            # Lire le CSV
            df = self.read_csv_file(file)
            
            # Nettoyer les données
            df = self.clean_dataframe(df)
            
            # Insérer dans la base de données
            conn = self.db.connect()
            
            try:
                # Initialiser la table si nécessaire
                self.init_table()
                
                # Insérer les données
                rows_inserted, insert_errors = self.insert_data(conn, df, import_date)
                
                if insert_errors:
                    errors.extend(insert_errors)
                
                # Commit
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
    
    def get_power_card_stats(self, import_date: str = None):
        """Récupérer les statistiques des transactions Power Card"""
        conn = None
        try:
            conn = self.db.connect()
            
            if import_date:
                # Statistiques pour une date spécifique
                sql = text("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        COUNT(DISTINCT DATE(local_time)) as transaction_days,
                        SUM(CAST(REPLACE(transaction_amount, ',', '.') AS DECIMAL(20,2))) as total_amount,
                        COUNT(CASE WHEN action = 'Approved' THEN 1 END) as approved_count,
                        COUNT(CASE WHEN action != 'Approved' THEN 1 END) as rejected_count
                    FROM transact_power_card
                    WHERE import_date = :import_date
                """)
                result = conn.execute(sql, {"import_date": import_date}).fetchone()
                
                if result:
                    return {
                        "import_date": import_date,
                        "total_transactions": result[0] or 0,
                        "transaction_days": result[1] or 0,
                        "total_amount": float(result[2]) if result[2] else 0,
                        "approved_count": result[3] or 0,
                        "rejected_count": result[4] or 0
                    }
            else:
                # Statistiques pour toutes les dates
                sql = text("""
                    SELECT 
                        import_date,
                        COUNT(*) as total_transactions,
                        COUNT(CASE WHEN action = 'Approved' THEN 1 END) as approved_count,
                        COUNT(CASE WHEN action != 'Approved' THEN 1 END) as rejected_count
                    FROM transact_power_card
                    GROUP BY import_date
                    ORDER BY import_date DESC
                """)
                results = conn.execute(sql).fetchall()
                
                return [
                    {
                        "import_date": str(row[0]),
                        "total_transactions": row[1],
                        "approved_count": row[2],
                        "rejected_count": row[3]
                    }
                    for row in results
                ]
            
            return None
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur récupération stats: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_transactions_by_date(self, import_date: str, limit: int = 100, offset: int = 0):
        """Récupérer les transactions pour une date donnée"""
        conn = None
        try:
            conn = self.db.connect()
            
            sql = text("""
                SELECT 
                    id, external_stan, reference, source, destination, message,
                    processing_code, action, pan, local_time, internal_time,
                    transaction_amount, terminal_no, acceptor_point,
                    authorization_reference, source_account_number, import_date
                FROM transact_power_card
                WHERE import_date = :import_date
                ORDER BY local_time DESC
                LIMIT :limit OFFSET :offset
            """)
            
            results = conn.execute(sql, {
                "import_date": import_date,
                "limit": limit,
                "offset": offset
            }).fetchall()
            
            return [
                {
                    "id": row[0],
                    "external_stan": row[1],
                    "reference": row[2],
                    "source": row[3],
                    "destination": row[4],
                    "message": row[5],
                    "processing_code": row[6],
                    "action": row[7],
                    "pan": row[8],
                    "local_time": str(row[9]) if row[9] else None,
                    "internal_time": str(row[10]) if row[10] else None,
                    "transaction_amount": row[11],
                    "terminal_no": row[12],
                    "acceptor_point": row[13],
                    "authorization_reference": row[14],
                    "source_account_number": row[15],
                    "import_date": str(row[16])
                }
                for row in results
            ]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
