import pymysql
import pandas as pd
from datetime import datetime

class ChangeProcessor:
    def __init__(self, host='localhost', user='root', password='', database='dfe'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.GLOBALE_DATE = "202509"
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
    
    def create_temp_table_brutes(self, value_date):
        """
        Crée une table temporaire pour les données brutes (transaction_code IN 35, 38, 23, 26)
        """
        try:
            with self.connection.cursor() as cursor:
                # Création de la table temporaire
                create_table_query = f"""
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
                cursor.execute(create_table_query)
                print(f"[SUCCÈS] Table temporaire 'temp_change_brutes' créée pour {value_date}")
                return True
                
        except Exception as e:
            print(f"[ERREUR] create_temp_table_brutes: {e}")
            return False
    
    def create_temp_table_brutes_26(self, value_date):
        """
        Crée une table temporaire pour les données brutes (transaction_code = 26)
        """
        try:
            with self.connection.cursor() as cursor:
                # Création de la table temporaire
                create_table_query = f"""
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_change_brutes_26 AS
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
                cursor.execute(create_table_query)
                print(f"[SUCCÈS] Table temporaire 'temp_change_brutes_26' créée pour {value_date}")
                return True
                
        except Exception as e:
            print(f"[ERREUR] create_temp_table_brutes_26: {e}")
            return False
    
    def get_data_brutes(self):
        """
        Récupère les données brutes depuis la table temporaire
        """
        try:
            query = "SELECT * FROM temp_change_brutes;"
            df_brutes = pd.read_sql(query, self.connection)
            print(f"[SUCCÈS] {len(df_brutes)} enregistrements bruts récupérés")
            return df_brutes
        except Exception as e:
            print(f"[ERREUR] get_data_brutes: {e}")
            return pd.DataFrame()
    
    def get_data_brutes_26(self):
        """
        Récupère les données brutes (transaction_code = 26) depuis la table temporaire
        """
        try:
            query = "SELECT * FROM temp_change_brutes_26;"
            df_brutes_26 = pd.read_sql(query, self.connection)
            print(f"[SUCCÈS] {len(df_brutes_26)} enregistrements bruts (code 26) récupérés")
            return df_brutes_26
        except Exception as e:
            print(f"[ERREUR] get_data_brutes_26: {e}")
            return pd.DataFrame()
    
    def query_synthese(self, value_date):
        """
        Génère la synthèse des totaux ACHAT et VENTE avec paramètre value_date
        """
        try:
            query_synthese = f"""
            SELECT
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 23 THEN tel.amount_fcy_1 ELSE 0 END) AS 'ACHAT/MONTANT EUR',
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 23 THEN tel.amount_local_1 ELSE 0 END) AS 'ACHAT/MONTANT MGA EUR',
               
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 23 THEN tel.amount_fcy_1 ELSE 0 END) AS 'ACHAT/MONTANT USD',
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 23 THEN tel.amount_local_1 ELSE 0 END) AS 'ACHAT/MONTANT MGA USD',
               
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 26 THEN tel.amount_fcy_1 ELSE 0 END) AS 'VENTE/MONTANT USD',
                SUM(CASE WHEN tel.currency_1 = 'USD' AND tel.transaction_code = 26 THEN tel.amount_local_1 ELSE 0 END) AS 'VENTE/MONTANT MGA USD',
               
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 26 THEN tel.amount_fcy_1 ELSE 0 END) AS 'VENTE/MONTANT EUR',
                SUM(CASE WHEN tel.currency_1 = 'EUR' AND tel.transaction_code = 26 THEN tel.amount_local_1 ELSE 0 END) AS 'VENTE/MONTANT MGA EUR'
            FROM
                teller_mcbc_his_full AS tel
            WHERE
                tel.transaction_code IN (23, 26)
                AND tel.value_date_1 LIKE '{value_date}%';
            """
            
            df_synthese = pd.read_sql(query_synthese, self.connection)
            print(f"[SUCCÈS] Données de synthèse récupérées pour {value_date}")
            return df_synthese
            
        except Exception as e:
            print(f"[ERREUR] query_synthese: {e}")
            return pd.DataFrame()
    
    def process_synthese_data(self, df_synthese):
        """
        Traite les données de synthèse pour le format final
        """
        try:
            # Calcul des totaux ACHAT et VENTE en MGA
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
    
    def generate_excel_report(self, value_date, output_path='output/change.xlsx'):
        """
        Génère le rapport Excel complet
        """
        try:
            # Créer les tables temporaires
            if not self.create_temp_table_brutes(value_date):
                return False
            if not self.create_temp_table_brutes_26(value_date):
                return False
            
            # Récupérer les données
            df_brutes = self.get_data_brutes()
            df_brutes_26 = self.get_data_brutes_26()
            df_synthese_raw = self.query_synthese(value_date)
            resultat_synthese = self.process_synthese_data(df_synthese_raw)
            
            # Vérifier si nous avons des données
            if df_brutes.empty and df_brutes_26.empty and resultat_synthese.empty:
                print("[ATTENTION] Aucune donnée à exporter")
                return False
            
            # Créer le fichier Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Feuille ETAT
                if not df_brutes.empty:
                    df_brutes.to_excel(writer, sheet_name='ETAT', index=False)
                
                # Feuille Synthèse
                if not resultat_synthese.empty:
                    resultat_synthese.to_excel(writer, sheet_name='Synthèse', index=False, startrow=1)
                    worksheet = writer.sheets['Synthèse']
                    worksheet.insert_rows(0)
                    worksheet.cell(row=1, column=1).value = f"COMPTE RENDU : ACHAT ET VENTE DE DEVISES - {value_date}"
                
                # Feuille Allocation_devise
                if not df_brutes_26.empty:
                    df_brutes_26.to_excel(writer, sheet_name='Allocation_devise', index=False)
            
            print(f"[SUCCÈS] Rapport Excel généré: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] generate_excel_report: {e}")
            return False
    
    def cleanup_temp_tables(self):
        """
        Nettoie les tables temporaires (optionnel - elles sont automatiquement supprimées à la fin de la session)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_change_brutes;")
                cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_change_brutes_26;")
                print("[SUCCÈS] Tables temporaires nettoyées")
        except Exception as e:
            print(f"[ERREUR] cleanup_temp_tables: {e}")

# Exemple d'utilisation
def main():
    # Initialisation du processeur
    processor = ChangeProcessor()
    
    # Connexion à la base
    if not processor.connect():
        return
    
    try:
        # Génération du rapport pour une date spécifique
        value_date = "202508"  # Vous pouvez changer cette date
        success = processor.generate_excel_report(value_date)
        
        if success:
            print("✅ Rapport généré avec succès!")
        else:
            print("❌ Erreur lors de la génération du rapport")
            
    finally:
        # Nettoyage et déconnexion
        processor.cleanup_temp_tables()
        processor.disconnect()

if __name__ == "__main__":
    main()