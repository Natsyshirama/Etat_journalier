import pandas as pd
from sqlalchemy import text ,String
from controller.DbGet import DbGet
import math
from db.db import DB

dbGet = DbGet()


class Esri:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine  
    
    def create_tableEsri(self, label: str):
        """
        Crée une table esri_<label> pré-calculée à partir de teller_mcbc_his_full
        - label : format 'yyyyMM', utilisé pour filtrer value_date_1
        """
        conn = None
        try:
            table_name = f"esri_{label}"
            
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT 
                co_code AS Agence,
                'EUR' AS Devise,
                'SIPEM' AS Banque,
                '0' AS `Donneur resident`,
                '' AS `Code pays donneur d'ordre`,
                DATE_FORMAT(value_date_1, '%Y/%m/%d') AS Date,
                amount_local_1 AS Montant,
                local_ref
            FROM teller_mcbc_his_full
            WHERE transaction_code IN (40,53)
              AND value_date_1 LIKE '{label}%';
            """
            
            conn = self.db.connect()
            conn.execute(text(query))
            conn.commit()
            print(f"[INFO] Table {table_name} créée avec succès ✅")
            
            return table_name
            
        except Exception as e:
            print(f"[ERREUR] create_tableEsriPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableEsriPreCompute) : {close_err}")  
                    
                    
      