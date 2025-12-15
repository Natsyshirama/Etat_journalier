import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet
from controller.AgenceController import AgenceController
db_get = DbGet()
agence_report = AgenceController()
class decaissementReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
    
    def getListeDecaissement(self):
        conn = None
        try:
            conn = self.db.connect()

            # Requête pour récupérer les noms des tables commençant par dav_
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'decaissement_%'
            """)

            result = conn.execute(query)
            # Transformer en liste Python
            tables = [row[0] for row in result.fetchall()]
            return tables

        except Exception as e:
            print(f"[ERREUR] getListeDecaissement : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeDecaissement) : {close_err}")
                    
    def getDecaissement(self, table_name: str, agence: str = None):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()
            if agence:
                query = text(f"SELECT * FROM `{table_name_vrai}` WHERE Agence = :agence")  
                result = conn.execute(query, {"agence": agence})
            else:

                query = text(f"SELECT * FROM `{table_name_vrai}`")  
                result = conn.execute(query)

            rows = result.fetchall()
            columns = list(result.keys())   # noms colonnes

            data = [dict(zip(columns, row)) for row in rows]
            return {
                "columns": columns,
                "data": data
            }

        except Exception as e:
            print(f"[ERREUR] getDecaissement : {e}")
            return {
                "columns": [],
                "data": []
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getDecaissement) : {close_err}")
                    
    def getDecAn(self, agence: str = None,
                       date_debut: str = None, date_fin: str = None,
                       single_date_if_all: str = "20251028" , compare: bool = False):
        agences_result = agence_report.get_code_Agence()
        if not agences_result.get("success"):
                return {
                    "status": "error",
                    "message": f"Impossible de récupérer les agences: {agences_result.get('error', 'Erreur inconnue')}",
                    "data": []
                }
        AGENCES_DISPO = [item["code"] for item in agences_result.get("data", [])]
        if not AGENCES_DISPO:
                return {
                    "status": "warning", 
                    "message": "Aucune agence disponible dans la base de données",
                    "data": []
                }

        conn = None
        try:
            conn = self.db.connect()

            tables_query = text("SHOW TABLES LIKE 'decaissement_%'")
            all_tables = [row[0] for row in conn.execute(tables_query).fetchall()]
            if not all_tables:
                return []

            results = []

           
            if agence and agence.lower() == "all":

                table_name = f"decaissement_{single_date_if_all}"
                if table_name not in all_tables:
                    return {"message": f"Aucune table trouvée pour la date {single_date_if_all}"}

                sql = f"""
                    SELECT 
                        COUNT(DISTINCT code_client) AS nb_clients,
                        SUM(montant_capital) AS total_montant_capital,
                        SUM(frais_de_dossier) AS total_frais_de_dossier
                    FROM `{table_name}`
                    WHERE Agence = :agence
                """

                for ag in AGENCES_DISPO:
                    result = conn.execute(text(sql), {"agence": ag}).fetchone()
                    if result:
                        results.append({
                            "date_agence": {"date": single_date_if_all, "agence": ag},
                            "data": {
                                "nb_clients": int(result[0] or 0),
                                "total_montant_capital": round(abs(float(result[1] or 0)), 2),
                                "total_frais_de_dossier": round(abs(float(result[2] or 0)), 2)
                            }
                        })

                return results

           
            if compare and date_debut and date_fin:
                    filtered_tables = [t for t in all_tables if t.replace(f"decaissement_", "") in [date_debut, date_fin]]
            elif date_debut and date_fin:
                filtered_tables = [t for t in all_tables if date_debut <= t.replace("decaissement_", "") <= date_fin]    
            elif date_debut or date_fin:
                filtered_tables = [t for t in all_tables if t.replace("decaissement_", "") == date_debut or t.replace("decaissement_", "") == date_fin]
            else:
                filtered_tables = all_tables

            if not filtered_tables:
                return []

            previous_data = None

            for table_name in sorted(filtered_tables):
                table_date = table_name.replace("decaissement_", "")

                where = []
                params = {}

                if agence:
                    where.append("Agence = :agence")
                    params["agence"] = agence

                where_clause = " AND ".join(where)
                if where_clause:
                    where_clause = "WHERE " + where_clause

                sql = f"""
                    SELECT 
                        COUNT(DISTINCT code_client) AS nb_clients,
                        SUM(montant_capital) AS total_montant_capital,
                        SUM(frais_de_dossier) AS total_frais_de_dossier
                    FROM `{table_name}`
                    {where_clause}
                """

                result = conn.execute(text(sql), params).fetchone()
                if not result:
                    continue

                current_data = {
                    "nb_clients": int(result[0] or 0),
                    "total_montant_capital": round(abs(float(result[1] or 0)), 2),
                    "total_frais_de_dossier": round(abs(float(result[2] or 0)), 2),
                }

                # --- Calcul des écarts ---
                ecart_data = {}
                if previous_data:
                    for key in current_data:
                        previous_value = previous_data.get(key, 0)
                        ecart_data[f"ecart_{key}"] = current_data[key] - previous_value
                else:
                    ecart_data = {f"ecart_{k}": 0 for k in current_data}

                results.append({
                    "date_agence": {"date": table_date, "agence": agence},
                    "data": current_data,
                    "ecart": ecart_data
                })

                previous_data = current_data

            return results
        except Exception as e:
            print(f"[ERREUR] getTotalParProduit : {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getTotalParProduit) : {close_err}")


    def getResumeDecaissement(self, table_name: str):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"""
                SELECT 
                   
                    COUNT(DISTINCT code_client) AS nb_clients,
                    SUM(montant_capital) AS total_montant_capital,
                    SUM(frais_de_dossier) AS total_frais_de_dossier
                FROM `{table_name_vrai}`
            """)
            result = conn.execute(query).fetchone()

            columns =  result.keys() if hasattr(result, "keys") else [
                
                 "nb_clients", "total_montant_capital", "total_frais_de_dossier"
            ]
            
            summary = {col: result[idx] for idx, col in enumerate(columns)} if result else {}

            return summary

        except Exception as e:
            print(f"[ERREUR] getResumeDav : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getResumeDecaissement) : {close_err}")
    
                    
    def get_grapheDec(self, x: str, y: str, table_name:str):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement"):
                raise ValueError("Nom de table invalide")
        conn = None
        try:
            conn = self.db.connect()
            
            colone_auto= [
                 "Agence", "Produits", "montant_capital", "frais_de_dossier", "taux_interet", "charge_rate","code_client"
            ]
            if x not in colone_auto or y not in colone_auto:
                raise ValueError("Colonnes non autorisées")
            
            numeric_columns = ["montant_capital", "frais_de_dossier", "Debit", "taux_interet", "charge_rate"]
            
            if (x == "Agence" and y == "code_client") or (x == "code_client" and y == "Agence"):
                select = "Agence, COUNT(DISTINCT code_client) AS value"
                group_by = "Agence"
                
            elif x in numeric_columns and y not in numeric_columns:
                select = f"{y}, SUM({x}) AS value"
                group_by = y
            elif y in numeric_columns and x not in numeric_columns:
                select = f"{x}, SUM({y}) AS value"
                group_by = x
            elif x in numeric_columns and y in numeric_columns:
                select = f"SUM({x}) AS value_x, SUM({y}) AS value_y"
                group_by = None 
            else: 
                select = f"{x}, {y}, COUNT(*) AS value"
                group_by = f"{x}, {y}"
                
            if group_by:
                query = f"SELECT {select} FROM {table_name_vrai} GROUP BY {group_by} ORDER BY value DESC;"
            else:
                query = f"SELECT {select} FROM {table_name_vrai} ORDER BY value_x DESC;"

            print("Requête SQL exécutée :", query)
            
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

            data = [dict(zip(columns, row)) for row in rows]
            return {"query": query, "columns": columns, "rows": data}
        
        except Exception as e:
            print(f"[ERREUR] get_graphe_data : {e}")
            return {"status": "error", "message": str(e)}

        finally:
            if conn:
                conn.close()
                
   