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
                    print(f"[ERREUR] Fermeture connexion (getListeDat) : {close_err}")
                

    def getDat(self, table_name: str):
        if not table_name or not table_name.startswith("dat_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"SELECT * FROM `{table_name}`")  
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
            columns = result.keys() if hasattr(result, "keys") else [
                "nb_lignes",
                "nb_clients",
                "total_montant_capital",
                "total_montant_pay_total"
                ]

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

    def getListeHistoryInsert(self):
       
        conn = None
        try:
            conn = self.db.connect()

            query = text("""
                SELECT label, used, dat_status, dav_status
                FROM history_insert
                ORDER BY used DESC
            """)

            result = conn.execute(query)
            rows = result.fetchall()
            columns = list(result.keys())

            # Transformer en liste de dictionnaires
            data = [dict(zip(columns, row)) for row in rows]

            return data

        except Exception as e:
            print(f"[ERREUR] getListeHistoryInsert : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeHistoryInsert) : {close_err}")


    def get_graphe_data(self, x: str, y: str, table_name: str = "dat_20250915"):
        conn = None
        try:
            conn = self.db.connect()

            # Colonnes autorisées
            allowed_columns = [
                "code_client", "Agence", "Produits", "Numero_compte",
                "montant_capital", "montant_pay_total"
            ]
            if x not in allowed_columns or y not in allowed_columns:
                raise ValueError("Colonnes non autorisées")

            numeric_columns = ["montant_capital", "montant_pay_total"]

            # Déterminer l'agrégation
            if x in numeric_columns and y not in numeric_columns:
                agg = f"SUM({x}) AS value"
                select = f"{y}, {agg}"
                group_by = y
            elif y in numeric_columns and x not in numeric_columns:
                agg = f"SUM({y}) AS value"
                select = f"{x}, {agg}"
                group_by = x
            elif x in numeric_columns and y in numeric_columns:
                agg = f"SUM({x}) AS value_x, SUM({y}) AS value_y"
                select = agg
                group_by = None
            else:  # deux catégorielles
                agg = "COUNT(DISTINCT code_client) AS value" if x == "code_client" else "COUNT(*) AS value"
                select = f"{x}, {y}, {agg}"
                group_by = f"{x}, {y}"

            # Construction de la requête
            if group_by:
                query = f"SELECT {select} FROM {table_name} GROUP BY {group_by} ORDER BY value DESC;"
            else:
                query = f"SELECT {select} FROM {table_name} ORDER BY value_x DESC;"

            print("Requête SQL exécutée :", query)

            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

            data = [dict(zip(columns, row)) for row in rows]
            return {"query": query,"columns": columns, "rows": data}

        except Exception as e:
            print(f"[ERREUR] get_graphe_data : {e}")
            return {"status": "error", "message": str(e)}

        finally:
            if conn:
                conn.close()


