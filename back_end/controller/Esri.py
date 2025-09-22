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
                    
                    
                    
    def traitement_esri(self, table_name: str):
        """
        Nettoie les données dans la table esri_<label>
        - Remplace NULL par 0 pour Montant
        - Normalise code_client si applicable
        - Supprime doublons sur Agence / Référence / Donneur d'ordre / Bénéficiaire / Montant
        - Supprime colonnes temporaires ou inutiles
        """
        conn = None
        try:
            conn = self.db.connect()

            # Remplacer NULL par 0 pour la colonne Montant
            query_nulls = f"""
            UPDATE {table_name}
            SET Montant = COALESCE(Montant, 0);
            """
            conn.execute(text(query_nulls))

            # Nettoyer colonne Agence et Référence si elles contiennent des séparateurs
            query_clean = f"""
            UPDATE {table_name}
            SET Agence = SUBSTRING_INDEX(Agence, '|', 1),
                Référence = SUBSTRING_INDEX(Référence, '|', 1);
            """
            conn.execute(text(query_clean))

            # Supprimer doublons sur les colonnes clés principales
            query_dedup = f"""
            DELETE t1 FROM {table_name} t1
            INNER JOIN {table_name} t2
            ON t1.Agence = t2.Agence
            AND t1.Référence = t2.Référence
            AND t1['Donneur d\'ordre'] = t2['Donneur d\'ordre']
            AND t1.Bénéficiaire = t2.Bénéficiaire
            AND t1.Montant = t2.Montant
            AND t1.rowid < t2.rowid;
            """
            conn.execute(text(query_dedup))

            # Supprimer colonnes temporaires inutiles si elles existent
            drop_cols = ['Adresse donneur d\'ordre', 'Adresse Bénéficiaire']  # si tu veux supprimer certaines colonnes
            existing_cols = conn.execute(text(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table
            """), {"table": table_name}).fetchall()
            existing_cols = [c[0] for c in existing_cols]

            cols_to_drop = [c for c in drop_cols if c in existing_cols]
            if cols_to_drop:
                conn.execute(text(f"ALTER TABLE {table_name} DROP COLUMN {', DROP COLUMN '.join(cols_to_drop)}"))

            conn.commit()
            print(f"[INFO] Nettoyage terminé pour {table_name} ✅")

        except Exception as e:
            print(f"[ERREUR] traitement_esri : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (traitement_esri) : {close_err}")
