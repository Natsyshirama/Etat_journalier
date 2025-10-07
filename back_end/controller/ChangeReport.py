import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

class ChangeReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
    def getEtat(self,date_value: str):
        table_name_vrai = f"etat_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("change_"):
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
            print(f"[ERREUR] getEtat : {e}")
            return {"columns": [], "rows": []}
        finally:    
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getEtat) : {close_err}")
                    
    def getAllocation(self, date_value:str):
        table_name_vrai = f"allocation_devise_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("allocation_devise_"):
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
            print(f"[ERREUR] getAllocation : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getAllocation) : {close_err}")
    
    def getSynthes(self, date_value:str):
        table_name_vrai = f"synthese_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("synthese_"):
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
            print(f"[ERREUR] getSynthes : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getSynthes) : {close_err}")