import pandas as pd
from sqlalchemy import text
from db.db import DB

class DATReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine

    def get_all(self, limit: int = 1000):
       
        conn = None
        try:
            conn = self.db.connect() 
            query = text(f"""
                SELECT * 
                FROM dat_precompute
                LIMIT {limit};
            """)
            result = conn.execute(query)

            columns = result.keys()
            rows = result.fetchall()

            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)

            return data

        except Exception as e:
            print(f"[ERREUR] get_all : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (get_all) : {close_err}")


    def get_by_client(self, code_client: str):
       
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT * 
                FROM dat_precompute
                WHERE code_client = :code_client
            """)
            result = conn.execute(query, {"code_client": code_client})

            columns = result.keys()
            rows = result.fetchall()

            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)

            return data

        except Exception as e:
            print(f"[ERREUR] get_by_client : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (get_by_client) : {close_err}")
