import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet


class EsriReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
       
       
    def getEsri(self, date_value: str):
        table_name_vrai = date_value
        if not table_name_vrai or not table_name_vrai.startswith("esri_"):
            raise ValueError("Nom de table invalide")
        conn = None
        try:
            conn = self.db.connect()
            
            query = text(f"SELECT * FROM `{table_name_vrai}`")
            result = conn.execute(query)
            
            rows = conn.execute(query).fetchall()
            columns = list(result.keys())   
            
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                
                "columns": columns,
                "rows": data
            }
        except Exception as e:
            print(f"[ERREUR] getEsri : {e}")
            return {"columns": [], "rows": []}
        finally:    
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getEsri) : {close_err}")
                    
    def getResumer(self, table_name: str):
        table_name_vrai = table_name
        if not table_name_vrai or not table_name_vrai.startswith("esri_"):
            raise ValueError("Nom de table invalide")
        
        conn = None
        try: 
            conn = self.db.connect()
            
            query = text(f"""
                SELECT 
                    COUNT(*) AS nb_lignes,
                    SUM(Montant) AS total_montant,
                FROM `{table_name_vrai}`
            """)
            result = conn.execute(query)
            columns = result.keys() if hasattr(result, 'keys') else [
                "nb_lignes",
                "total_montant"
            ]
            
            summary = {col: result[i] for i, col in enumerate(columns)}
            
            return summary
        except Exception as e:
            print(f"[ERREUR] getResumer : {e}")
            return {}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getResumer) : {close_err}")
        
            