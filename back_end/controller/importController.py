import pandas as pd
import numpy as np
import re
from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from db.db import DB
from datetime import datetime

class importController:
    def __init__(self):
        self.db = DB()
        self.pattern = re.compile(r"^(dav|dat|epr|decaissement)_(\d{8})\.csv$")
    
    def check_and_insert_history(self, conn, date_str: str, table_type: str):
        
        try:
            check_sql = text("SELECT label FROM history_insert WHERE label = :label")
            result = conn.execute(check_sql, {"label": date_str}).fetchone()
            
            if result:
                print(f"Date {date_str} existe déjà dans history_insert")
                
                if table_type == "dav":
                    update_sql = text("""
                        UPDATE history_insert 
                        SET dav_status = 1
                        WHERE label = :label
                    """)
                elif table_type == "dat":
                    update_sql = text("""
                        UPDATE history_insert 
                        SET dat_status = 1
                        WHERE label = :label
                    """)
                elif table_type == "epr":
                    update_sql = text("""
                        UPDATE history_insert 
                        SET epr_status = 1 
                        WHERE label = :label
                    """)
                elif table_type == "decaissement":
                    update_sql = text("""
                        UPDATE history_insert 
                        SET dec_status = 1 
                        WHERE label = :label
                    """)
                
                conn.execute(update_sql, {"label": date_str})
                print(f"Statut {table_type}_status mis à jour pour {date_str}")
                
            else:
                dav_status = 1 if table_type == "dav" else 0
                dat_status = 1 if table_type == "dat" else 0
                epr_status = 1 if table_type == "epr" else 0
                dec_status = 1 if table_type == "decaissement" else 0
                
                insert_sql = text("""
                    INSERT INTO history_insert 
                    (label, stat_of, used, created_at, dav_status, dat_status, epr_status, stat_compte, dec_status)
                    VALUES (:label, :stat_of, :used, :created_at, :dav_status, :dat_status, :epr_status, :stat_compte, :dec_status)
                """)
                
                params = {
                    "label": date_str,
                    "stat_of": None,
                    "used": 0,
                    "created_at": datetime.now(),
                    "dav_status": dav_status,
                    "dat_status": dat_status,
                    "epr_status": epr_status,
                    "stat_compte": 1,
                    "dec_status": dec_status
                }
                
                conn.execute(insert_sql, params)
                print(f"Nouvelle date {date_str} ajoutée à history_insert avec {table_type}_status = 1")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la gestion de history_insert pour {date_str}: {e}")
            raise
    
    def validate_filename(self, filename: str):
        """Valider le nom du fichier selon le pattern"""
        match = self.pattern.match(filename)
        if not match:
            raise ValueError(f"Nom de fichier invalide : {filename}")
        return match.groups()
    
    def read_csv_file(self, file: UploadFile):
        """Lire le fichier CSV avec gestion d'erreurs"""
        try:
            file.file.seek(0)
            df = pd.read_csv(file.file, encoding='utf-8')
            file.file.seek(0)
            return df
        except Exception as e:
            raise ValueError(f"Erreur lecture CSV {file.filename} : {e}")
    
    
    def clean_dataframe(self, df: pd.DataFrame):
        """Nettoyer les colonnes et données du DataFrame"""
        if df.empty:
            raise ValueError("DataFrame vide")
        
        df.columns = [
            col.strip()
            .replace(" ", "_")
            .replace("é", "e")
            .replace("è", "e")
            .replace("à", "a")
            .replace("ç", "c")
            .replace("ô", "o")
            .replace("î", "i")
            for col in df.columns
        ]
        
        df = df.replace({np.nan: None, pd.NaT: None})
        
        for col in df.columns:
            df[col] = df[col].apply(lambda x: None if pd.isna(x) or x == "" else x)
        
        return df
    
    def create_table(self, conn, table_name: str, df: pd.DataFrame):
        """Créer la table si elle n'existe pas"""
        columns = ", ".join([f"`{col}` TEXT" for col in df.columns])
        create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
        conn.execute(text(create_sql))
    
    def insert_data(self, conn, table_name: str, df: pd.DataFrame):
        """Insérer les données dans la table"""
        rows_inserted = 0
        
        for row in df.to_dict(orient="records"):
            try:
                clean_row = {
                    k: (None if pd.isna(v) else v)
                    for k, v in row.items()
                }
                
                cols = ", ".join([f"`{col}`" for col in clean_row.keys()])
                placeholders = ", ".join([f":{col}" for col in clean_row.keys()])
                
                insert_sql = text(f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})")
                
                conn.execute(insert_sql, clean_row)
                rows_inserted += 1
                
            except Exception as e:
                print(f"Erreur insertion ligne: {clean_row}\nErreur: {e}")
                raise ValueError(f"Erreur insertion ligne: {e}")
        
        return rows_inserted
    
    def process_single_file(self, file: UploadFile):
        """Traiter un seul fichier d'import"""
        errors = []
        success = []
        rows_inserted = 0
        
        try:
            type_table, date_str = self.validate_filename(file.filename)
            table_name = f"{type_table}_{date_str}"
            
            df = self.read_csv_file(file)
            
            df = self.clean_dataframe(df)
            
            conn = self.db.connect()
            
            try:
                self.check_and_insert_history(conn, date_str, type_table)
                
                # Étape 2: Créer la table principale
                self.create_table(conn, table_name, df)
                
                # Étape 3: Insérer les données
                rows_inserted = self.insert_data(conn, table_name, df)
                
                # Commit final des changements
                conn.commit()
                
                success.append(f"Import réussi : {file.filename} ({rows_inserted} lignes)")
                
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
            "success": success,
            "errors": errors,
            "rows_inserted": rows_inserted,
            "date_imported": date_str if 'date_str' in locals() else None,
            "table_type": type_table if 'type_table' in locals() else None
        }
    
    def process_multiple_files(self, files: list[UploadFile]):
        """Traiter plusieurs fichiers d'import"""
        results = []
        total_success = []
        total_errors = []
        total_rows = 0
        
        files_sorted = sorted(files, key=lambda x: x.filename)
        
        for file in files_sorted:
            result = self.process_single_file(file)
            results.append(result)
            
            total_success.extend(result["success"])
            total_errors.extend(result["errors"])
            total_rows += result["rows_inserted"]
        
        return {
            "results": results,
            "summary": {
                "total_files": len(files),
                "success": total_success,
                "errors": total_errors,
                "total_rows_inserted": total_rows,
                "success_count": len(total_success),
                "error_count": len(total_errors),
                "dates_imported": list(set([r.get("date_imported") for r in results if r.get("date_imported")]))
            }
        }
    
    def get_history_status(self, date_str: str = None):
        
        conn = self.db.connect()
        try:
            if date_str:
                sql = text("""
                    SELECT label, dav_status, dat_status, epr_status, dec_status, stat_compte, used, created_at
                    FROM history_insert 
                    WHERE label = :label
                """)
                result = conn.execute(sql, {"label": date_str}).fetchone()
                
                if result:
                    return {
                        "label": result[0],
                        "dav_status": bool(result[1]),
                        "dat_status": bool(result[2]),
                        "epr_status": bool(result[3]),
                        "dec_status": bool(result[4]),
                        "stat_compte": bool(result[5]),
                        "used": bool(result[6]),
                        "created_at": result[7]
                    }
                return None
            else:
                sql = text("""
                    SELECT label, dav_status, dat_status, epr_status, dec_status, stat_compte, used, created_at
                    FROM history_insert 
                    ORDER BY label DESC
                """)
                results = conn.execute(sql).fetchall()
                
                return [
                    {
                        "label": row[0],
                        "dav_status": bool(row[1]),
                        "dat_status": bool(row[2]),
                        "epr_status": bool(row[3]),
                        "dec_status": bool(row[4]),
                        "stat_compte": bool(row[5]),
                        "used": bool(row[6]),
                        "created_at": row[7]
                    }
                    for row in results
                ]
        finally:
            conn.close()