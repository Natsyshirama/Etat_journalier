import pandas as pd
import re
from db.db import DB
from sqlalchemy import text

class OperationEsri:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
        # Tableau teller pour les indices des champs
        self.teller = [
            '151', '152', '171', '172', 'SIGNATORY', 'USREGS.TP.LEGAL.ID', 'EM.DRAW.CHQ.NO', 'EM.DRAW.CHQ.AMT',
            'EM.DRAW.ACCT.NO', 'EM.DRAW.BANK', 'EM.DRAW.BRANCH', 'EM.DRAW.BRCH.CODE', 'EM.DRAW.CUST.NAME',
            'EM.CLEARED.BAL', 'EM.MEMBER.NAME', 'EM.ACCT.WORK.BAL', 'EM.PAY.TO', 'EM.AMT.ARREARS', 'EM.ACCT.NUM',
            'EM.SAVGS.AMOUNT', 'EM.REPAYMENT', 'EM.INT.REPAYMENT', 'EM.INTEREST.DUE', 'EM.CONS.DISCLOSE',
            'EM.SAVING.TMP.BAL', 'EM.LOAN.TMP.BAL', 'EM.INT.TMP.BAL', 'EM.ACCT.TYPE', 'L.REFERENCE', 'L.ORD.CUST',
            'L.ORD.CUST.CTRY', 'L.ORD.CUST.RES', 'L.BEN.NAME', 'L.BEN.ADD', 'L.BEN.RES', 'L.PAY.DETAILS', 'L.INI.CTRY',
            'L.ECO.CODE', 'L.CCY.REC', 'L.MODE.TXN', 'L.MAT.AGEN', 'L.NOM.PRES', 'L.NIF.PRES', 'L.NUM.STATS', 'L.TYP.IDEN',
            'L.NUM.IDEN', 'L.NUM.BEN', 'L.NOM.TIER', 'L.ORD.ADD', 'L.NAME.REC', 'L.ADDR', 'L.CIN', 'L.VERSION.NAME'
        ]

        # Mapping des colonnes à extraire
        self.columns_mapping = {
            'Type': 'EM.ACCT.TYPE',
            'Référence': 'L.REFERENCE',
            'Donneur d\'ordre': 'L.ORD.CUST',
            'Adresse donneur d\'ordre': 'L.ORD.ADD',
            'Code pays donneur d\'ordre': 'L.ORD.CUST.CTRY',
            'Bénéficiaire': 'L.BEN.NAME',
            'Bénéficiaire résident': 'L.BEN.RES',
            'Adresse Bénéficiaire': 'L.BEN.ADD',
            'Nature': 'L.PAY.DETAILS',
            'Code économique': 'L.ECO.CODE',
            'Sens': 'L.MODE.TXN',
        }

        # Dictionnaires pour les pays
        self.country_addresses = {
            'AD': 'Andorre', 'AE': 'Émirats Arabes Unis', 'AF': 'Afghanistan', 'AG': 'Antigua et Barbuda',
            # ... (le reste de votre dictionnaire country_addresses)
        }

        self.countries_codes = [
            ("AF", "004"), ("ZA", "710"), ("AL", "008"), ("DZ", "12"), ("DE", "276"),
            # ... (le reste de votre liste countries_codes)
        ]

    def create_tableEsri(self, label: str):
        """
        Crée une table esri_<label> pré-calculée
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
            print(f"[ERREUR] create_tableEsri : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableEsri) : {close_err}")

    def extract_between_teller_and_mcbc(self, local_ref):
        """Extrait la valeur entre TELLER, et .MCBC"""
        match = re.search(r'TELLER,([^,]+)\.MCBC', local_ref)
        return match.group(1) if match else None

    def extract_value_from_local_ref(self, local_ref, field):
        """Extrait la valeur d'un champ donné depuis local_ref"""
        values = local_ref.split('|')
        if field in self.teller:
            index = self.teller.index(field)
            if index < len(values):
                return values[index]
        return None

    def update_address_based_on_country(self, country_code):
        """Met à jour l'adresse basée sur le code pays"""
        return self.country_addresses.get(country_code, 'Adresse inconnue')

    def update_country_code(self, country_code):
        """Convertit le code pays en code numérique"""
        codes_dict = {code: number for code, number in self.countries_codes if number != ""}
        return codes_dict.get(country_code.strip().upper() if country_code else None)

    def add_column_if_not_exists(self, conn, table_name, column_name, column_type="VARCHAR(255)"):
        """Ajoute une colonne si elle n'existe pas"""
        result = conn.execute(text(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table AND COLUMN_NAME = :column
        """), {"table": table_name, "column": column_name}).fetchone()

        if not result:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))

    def process_esri_data(self, table_name: str):
        """
        Traite les données ESRI : extraction, ajout de colonnes, insertion des valeurs
        """
        conn = None
        try:
            conn = self.db.connect()
            
            # Lire les données de la table
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            
            # Liste pour stocker les données extraites
            extracted_data = []
            
            # Extraire les données de local_ref
            for index, row in df.iterrows():
                local_ref = row['local_ref']
                row_data = {}
                
                # Extraire les données selon le mapping
                for col, field in self.columns_mapping.items():
                    if col == "Type":
                        row_data[col] = self.extract_between_teller_and_mcbc(local_ref)
                    else:
                        row_data[col] = self.extract_value_from_local_ref(local_ref, field)
                
                # Ajouter les colonnes existantes
                row_data["Agence"] = row["Agence"]
                row_data["Montant"] = row["Montant"]
                row_data["Banque"] = row["Banque"]
                row_data["Donneur resident"] = row["Donneur resident"]
                row_data["Date"] = row["Date"]
                
                # Mettre à jour l'adresse basée sur le code pays
                country_code = row_data.get('Code pays donneur d\'ordre')
                row_data["Adresse donneur d'ordre"] = self.update_address_based_on_country(country_code)
                
                # Ajouter le code pays numérique
                row_data["Code pays"] = self.update_country_code(country_code)
                
                extracted_data.append(row_data)
            
            # Convertir en DataFrame
            extracted_df = pd.DataFrame(extracted_data)
            
            # Ajouter les colonnes manquantes dans la table
            columns_to_add = [
                'Type', 'Référence', 'Donneur d\'ordre', 'Adresse donneur d\'ordre',
                'Bénéficiaire', 'Bénéficiaire résident', 'Adresse Bénéficiaire',
                'Nature', 'Code économique', 'Sens', 'Code pays'
            ]
            
            for column in columns_to_add:
                self.add_column_if_not_exists(conn, table_name, column)
            
            # Mettre à jour les données dans la table
            for idx, row in extracted_df.iterrows():
                update_query = f"""
                    UPDATE {table_name}
                    SET Type = :Type,
                        Référence = :Référence,
                        `Donneur d'ordre` = :Donneur_ordre,
                        `Adresse donneur d'ordre` = :Adresse_donneur,
                        `Code pays donneur d'ordre` = :Code_pays_donneur,
                        Bénéficiaire = :Bénéficiaire,
                        `Bénéficiaire résident` = :Beneficiaire_resident,
                        `Adresse Bénéficiaire` = :Adresse_beneficiaire,
                        Nature = :Nature,
                        `Code économique` = :Code_economique,
                        Sens = :Sens,
                        `Code pays` = :Code_pays
                    WHERE local_ref = :local_ref
                """
                conn.execute(text(update_query), {
                    "Type": row.get('Type'),
                    "Référence": row.get('Référence'),
                    "Donneur_ordre": row.get('Donneur d\'ordre'),
                    "Adresse_donneur": row.get('Adresse donneur d\'ordre'),
                    "Code_pays_donneur": row.get('Code pays donneur d\'ordre'),
                    "Bénéficiaire": row.get('Bénéficiaire'),
                    "Beneficiaire_resident": row.get('Bénéficiaire résident'),
                    "Adresse_beneficiaire": row.get('Adresse Bénéficiaire'),
                    "Nature": row.get('Nature'),
                    "Code_economique": row.get('Code économique'),
                    "Sens": row.get('Sens'),
                    "Code_pays": row.get('Code pays'),
                    "local_ref": df.iloc[idx]['local_ref']
                })
            
            conn.commit()
            print(f"[INFO] Données ESRI traitées et mises à jour pour {table_name} ✅")
            
        except Exception as e:
            print(f"[ERREUR] process_esri_data : {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (process_esri_data) : {close_err}")

    def generate_esri_report(self, label: str):
        """
        Méthode principale pour générer le rapport ESRI complet
        """
        # Créer la table
        table_name = self.create_tableEsri(label)
        
        if table_name:
            # Traiter les données
            self.process_esri_data(table_name)
            print(f"[SUCCÈS] Rapport ESRI généré pour {table_name} 🎉")
        else:
            print(f"[ERREUR] Impossible de créer la table pour {label}")