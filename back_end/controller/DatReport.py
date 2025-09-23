import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

db_get = DbGet()

class DATReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine


  #liste des tables dat disponibles
    def getListeDat(self):
        conn = None
        try:
            conn = self.db.connect()

            # Requête pour récupérer les noms des tables commençant par dat_
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'dat_%'
            """)

            result = conn.execute(query)
            # Transformer en liste Python
            tables = [row[0] for row in result.fetchall()]
            return tables

        except Exception as e:
            print(f"[ERREUR] getListeDat : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getHistory) : {close_err}")
                

    def getDat(self, table_name: str):
        """
        Récupère les données d'une table commençant par dat_.
        Retourne colonnes + rows
        """
        if not table_name or not table_name.startswith("dat_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"SELECT * FROM `{table_name}` LIMIT 100")  
            result = conn.execute(query)

            rows = result.fetchall()
            columns = list(result.keys())   # noms colonnes

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "rows": data
            }

        except Exception as e:
            print(f"[ERREUR] getDat : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getDat) : {close_err}")

    def getResumeDat(self, table_name: str):
        if not table_name or not table_name.startswith("dat_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()
            query = text(f"""
                SELECT 
                    COUNT(*) AS nb_lignes,
                    COUNT(DISTINCT code_client) AS nb_clients,
                    SUM(montant_capital) AS total_montant_capital,
                    SUM(montant_pay_total) AS total_montant_pay_total
                FROM `{table_name}`
            """)

            result = conn.execute(query).fetchone()  # tuple
            columns = result.keys() if hasattr(result, "keys") else ["nb_lignes","nb_clients","total_montant_capital","total_montant_pay_total"]

            # Convertir en dict
            summary = {col: result[i] for i, col in enumerate(columns)}

            return summary

        except Exception as e:
            print(f"[ERREUR] getResumeDat : {e}")
            return {}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

