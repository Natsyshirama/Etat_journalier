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
        
    def create_unified_temp_table(self, date_debut: str, date_fin: str):
        """Crée une seule table temporaire unifiée"""
        try:
            query = """
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_change_unified AS
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
                    tel.co_code as Agence,
                    tel.transaction_code
                FROM
                    teller_mcbc_his_full AS tel
                WHERE
                    transaction_code IN (35, 38, 23, 26)
                    AND tel.value_date_1 BETWEEN :date_debut AND :date_fin
            """
            
            with self.db.connect() as conn:
                drop_query = "DROP TEMPORARY TABLE IF EXISTS temp_change_unified"

                conn.execute(text(drop_query))

                conn.execute(text(query), {"date_debut": date_debut, "date_fin": date_fin})
                conn.commit()
            
            print("[INFO] Table temporaire unifiée créée avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_unified_temp_table : {e}")
            return False
       
    def get_all_data(self, date_debut: str, date_fin: str):
        """Récupère toutes les données en une seule connexion"""
        try:
            with self.db.connect() as conn:
                # Données brutes
                df_brutes = pd.read_sql(
                    "SELECT * FROM temp_change_unified ", 
                    conn
                )
                
                # Données code 26
                df_brutes_26 =pd.read_sql(
                    "SELECT * FROM temp_change_unified where transaction_code = 26", 
                    conn)
                
                query = text("""
                    SELECT
                    SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 23 THEN amount_fcy_1 ELSE 0 END) AS `ACHAT/MONTANT EUR`,
                    SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 23 THEN amount_local_1 ELSE 0 END) AS `ACHAT/MONTANT MGA EUR`,
                    SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 23 THEN amount_fcy_1 ELSE 0 END) AS `ACHAT/MONTANT USD`,
                    SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 23 THEN amount_local_1 ELSE 0 END) AS `ACHAT/MONTANT MGA USD`,
                    SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 26 THEN amount_fcy_1 ELSE 0 END) AS `VENTE/MONTANT USD`,
                    SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 26 THEN amount_local_1 ELSE 0 END) AS `VENTE/MONTANT MGA USD`,
                    SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 26 THEN amount_fcy_1 ELSE 0 END) AS `VENTE/MONTANT EUR`,
                    SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 26 THEN amount_local_1 ELSE 0 END) AS `VENTE/MONTANT MGA EUR`
                FROM teller_mcbc_his_full
                WHERE transaction_code IN (23, 26)
                AND value_date_1 BETWEEN :date_debut AND :date_fin
                             """)
                
                df_synthese_raw = pd.read_sql(query, conn, params={"date_debut": date_debut, "date_fin": date_fin})
                
                return df_brutes, df_brutes_26, df_synthese_raw
                
        except Exception as e:
            print(f"[ERREUR] get_all_data_single_connection : {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
       
    
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
    
    
    def generate_tables_report(self, date_debut: str, date_fin: str):
        """Version optimisée de la génération de rapport"""
        try:
            # Créer la table temporaire unifiée
            if not self.create_unified_temp_table(date_debut, date_fin):
                return False
            
            # Récupérer toutes les données
            df_brutes, df_brutes_26, df_synthese_raw = self.get_all_data(date_debut, date_fin)
            
            if df_brutes.empty and df_brutes_26.empty:
                print("[ATTENTION] Aucune donnée à traiter")
                return False
            
            # Traiter la synthèse
            resultat_synthese = self.process_synthese_data(df_synthese_raw)
            
            return {
                "status": "success",
                "etat": df_brutes,
                "allocation": df_brutes_26,
                "synthese": resultat_synthese
            }
            
        except Exception as e:
            print(f"[ERREUR] generate_tables_report_optimized: {e}")
            return False
        
        
    
    