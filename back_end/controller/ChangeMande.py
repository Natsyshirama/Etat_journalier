import pandas as pd
from sqlalchemy import text ,String
from controller.DbGet import DbGet
import math
from db.db import DB

dbGet = DbGet()

class ChangeMande:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
    
    def create_temp_table_brute(self, value_date: str):
        conn = None
        try:
            query_brutes= f"""
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_change_brutes AS
                SELECT
                    LEFT(tel.id, LENGTH(tel.id) - 1) AS `CODE OPERATIONS`,
                    DATE_FORMAT(tel.value_date_1, '%Y/%m/%d') AS `Date Operation`,
                    tel.narrative_1 AS `Nom Beneficiaire`,
                    tel.narrative_2 AS `Adresse Beneficiaire`,
                    CASE
                        WHEN transaction_code = 26 THEN tel.narrative_1
                        ELSE NULL
                    END AS `N°REF TITRE DE TRANSPORT`,
                    CASE
                        WHEN transaction_code = 26 THEN ''
                        ELSE NULL
                    END AS `DESTINATION PRINCIPALE`,
                    CASE
                        WHEN transaction_code = 26 THEN 'FOR'
                        ELSE NULL
                    END AS `NATURE VOYAGE`,
                    tel.currency_1 AS `CODE DEVISE`,
                    tel.deal_rate AS `COURS`,
                    tel.amount_fcy_1 AS `MONTANT OPERATION DEVISE`,
                    tel.amount_local_1 AS `MONTANT C,V MGA`,
                    'BB' AS `MODE DE PAIEMENT`,
                    tel.narrative_1 AS `OBSERVATIONS`,
                    tel.co_code as Agence
                FROM
                    teller_mcbc_his_full AS tel
                WHERE
                    transaction_code IN (35, 38, 23, 26)
                    AND tel.value_date_1 LIKE '{value_date}%';
                    """
                    
            conn = self.db.connect()
            conn.execute(text(query_brutes))
            conn.commit()
            print("[INFO] Table temporaire temp_change_brutes créée avec succès ✅")
            return True
        except Exception as e:
            print(f"[ERREUR] create_temp_table_brute : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion  : {close_err}")
                    
    def create_temp_table_26(self, value_date: str):
        conn =  None
        try:
            query_brutes_26 = f"""
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_change_26 AS 
                SELECT
                    LEFT(tel.id, LENGTH(tel.id) - 1) AS `CODE OPERATIONS`,
                    DATE_FORMAT(tel.value_date_1, '%Y/%m/%d') AS `Date Operation`,
                    tel.narrative_1 AS `Nom Beneficiaire`,
                    tel.narrative_2 AS `Adresse Beneficiaire`,
                    CASE
                        WHEN transaction_code = 26 THEN tel.narrative_1
                        ELSE NULL
                    END AS `N°REF TITRE DE TRANSPORT`,
                    CASE
                        WHEN transaction_code = 26 THEN ''
                        ELSE NULL
                    END AS `DESTINATION PRINCIPALE`,
                    CASE
                        WHEN transaction_code = 26 THEN 'FOR'
                        ELSE NULL
                    END AS `NATURE VOYAGE`,
                    tel.currency_1 AS `CODE DEVISE`,
                    tel.deal_rate AS `COURS`,
                    tel.amount_fcy_1 AS `MONTANT OPERATION DEVISE`,
                    tel.amount_local_1 AS `MONTANT C,V MGA`,
                    'BB' AS `MODE DE PAIEMENT`,
                    tel.narrative_1 AS `OBSERVATIONS`
                FROM
                    teller_mcbc_his_full AS tel
                WHERE
                    transaction_code = 26
                    AND tel.value_date_1 LIKE '{value_date}%';
                """
            conn = self.db.connect()
            conn.execute(text(query_brutes_26))
            conn.commit()
            print("[INFO] Table temporaire temp_change_26 créée avec succès ✅")
            return True
        except Exception as e:
            print(f"[ERREUR] create_temp_table_26 : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion  : {close_err}")  
                    
    def get_data_brute(self):
        conn = None
        try:
            conn = self.db.connect()
            query = "SELECT * FROM temp_change_brutes; "
            df_brute = pd.read_sql(query, conn)
            return df_brute
        except Exception as e:
            print(f"[ERREUR] get_data_brute : {e}")
            return pd.DataFrame()
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (get_data_brute) : {close_err}")
    
    def get_data_brute_26(self):
        conn = None
        try:
            conn = self.db.connect()
            query = "SELECT * FROM temp_change_26; "
            df_brute_26 = pd.read_sql(query, conn)
            return df_brute_26
        except Exception as e:
            print(f"[ERREUR] get_data_brute_26 : {e}")
            return pd.DataFrame()
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (get_data_brute_26) : {close_err}")
                    
    
    def query_synthese(self, value_date: str):
        conn = None
        try:
            conn = self.db.connect()
            
            query = text("""
            SELECT
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 23 THEN tel.amount_fcy_1 ELSE 0 END) AS `ACHAT/MONTANT EUR`,
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 23 THEN tel.amount_local_1 ELSE 0 END) AS `ACHAT/MONTANT MGA EUR`,
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 23 THEN tel.amount_fcy_1 ELSE 0 END) AS `ACHAT/MONTANT USD`,
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 23 THEN tel.amount_local_1 ELSE 0 END) AS `ACHAT/MONTANT MGA USD`,
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 26 THEN tel.amount_fcy_1 ELSE 0 END) AS `VENTE/MONTANT USD`,
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 26 THEN tel.amount_local_1 ELSE 0 END) AS `VENTE/MONTANT MGA USD`,
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 26 THEN tel.amount_fcy_1 ELSE 0 END) AS `VENTE/MONTANT EUR`,
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 26 THEN tel.amount_local_1 ELSE 0 END) AS `VENTE/MONTANT MGA EUR`
            FROM
                teller_mcbc_his_full AS tel
            WHERE
                tel.transaction_code IN (23, 26)
                AND tel.value_date_1 LIKE :value_date
            """)

            df_synthese = pd.read_sql(query, conn, params={"value_date": f"{value_date}%"})
            
            print(f"[INFO] Synthèse des opérations de change récupérée avec succès pour la date {value_date} ✅")
            return df_synthese

        except Exception as e:
            print(f"[ERREUR] query_synthese : {e}")
            return pd.DataFrame()
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (query_synthese) : {close_err}")

    def process_synthese_data(self, df_synthese: str):
        try:
            if df_synthese.empty:
                print("[ATTENTION] Aucune donnée de synthèse à traiter.")
                return pd.DataFrame()
        
            achat_total_mga = df_synthese['ACHAT/MONTANT MGA EUR'].iloc[0] + df_synthese['ACHAT/MONTANT MGA USD'].iloc[0]
            vente_total_mga = df_synthese['VENTE/MONTANT MGA USD'].iloc[0] + df_synthese['VENTE/MONTANT MGA EUR'].iloc[0]
            
            # Organiser les données de synthèse
            resultat_synthese = pd.DataFrame({
                'Type de transaction': ['ACHAT', 'VENTE'],
                'EUR (Montant)': [df_synthese['ACHAT/MONTANT EUR'].iloc[0], df_synthese['VENTE/MONTANT EUR'].iloc[0]],
                'EUR (Montant C,V en MGA)': [df_synthese['ACHAT/MONTANT MGA EUR'].iloc[0], df_synthese['VENTE/MONTANT MGA EUR'].iloc[0]],
                'USD (Montant)': [df_synthese['ACHAT/MONTANT USD'].iloc[0], df_synthese['VENTE/MONTANT USD'].iloc[0]],
                'USD (Montant C,V en MGA)': [df_synthese['ACHAT/MONTANT MGA USD'].iloc[0], df_synthese['VENTE/MONTANT MGA USD'].iloc[0]],
                'TOTAL EN MGA': [achat_total_mga, vente_total_mga]
            })
            
            return resultat_synthese
            
        except Exception as e:
            print(f"[ERREUR] process_synthese_data: {e}")
            return pd.DataFrame()
    
    def create_table_from_dataframe(self, df, table_name, success_message):
        
        try:
            
            # Créer la table dans la base de données
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='replace',  # Remplace si la table existe déjà
                index=False
            )
            print(f"[SUCCÈS] {success_message}: {table_name} ({len(df)} enregistrements)")
            return True
            
        except Exception as e:
            print(f"[ERREUR] _create_table_from_dataframe pour {table_name}: {e}")
            return False
    
    def clean_temp_tables(self):
        conn = None
        try:
            conn = self.db.connect()
            
            conn.execute("DROP TEMPORARY TABLE IF EXISTS temp_change_brutes;")
            conn.execute("DROP TEMPORARY TABLE IF EXISTS temp_change_brutes_26;")
            print("[SUCCÈS] Tables temporaires nettoyées")
            
            return True
        except Exception as e:
            print(f"[ERREUR] cleanup_temp_tables: {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (cleanup_temp_tables) : {close_err}")
        
    def generate_tables_report(self, value_date):
        
        try:
            # Créer les tables temporaires pour les données brutes
            if not self.create_temp_table_brute(value_date):
                return False
            if not self.create_temp_table_26(value_date):
                return False
            
            # Récupérer les données
            df_brutes = self.get_data_brute()
            df_brutes_26 = self.get_data_brute_26()
            df_synthese_raw = self.query_synthese(value_date)
            resultat_synthese = self.process_synthese_data(df_synthese_raw)
            
            # Vérifier si nous avons des données
            if df_brutes.empty and df_brutes_26.empty and resultat_synthese.empty:
                print("[ATTENTION] Aucune donnée à traiter")
                return False
            
            # Noms des tables à créer
            table_etat = f"ETAT_{value_date}"
            table_synthese = f"Synthese_{value_date}"
            table_allocation = f"Allocation_devise_{value_date}"
            
            # Créer la table ETAT
            if not df_brutes.empty:
                self.create_table_from_dataframe(df_brutes, table_etat, "Table ETAT créée avec succès")
            
            # Créer la table Synthèse
            if not resultat_synthese.empty:
                self.create_table_from_dataframe(resultat_synthese, table_synthese, "Table Synthèse créée avec succès")
            
            # Créer la table Allocation_devise
            if not df_brutes_26.empty:
                self.create_table_from_dataframe(df_brutes_26, table_allocation, "Table Allocation_devise créée avec succès")
            
            print(f"[SUCCÈS] Tables créées: {table_etat}, {table_synthese}, {table_allocation}")
            return {
                "status": "success",
                "table_etat": table_etat,
                "table_synthese": table_synthese,
                "table_allocation": table_allocation
            }
            
        except Exception as e:
            print(f"[ERREUR] generate_tables_report: {e}")
            return False
        finally:
            self.clean_temp_tables()
        

        
        
    
    