import pandas as pd
from db.db import DB
from sqlalchemy import text
from controller.DbGet import DbGet
import pymysql


dbGet = DbGet()

class OperatioDav:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
        
    def calcule_dav(self, table_name: str):
       
        conn = None
        try:
            conn = self.db.connect()    

            # Lire la table entière dans un DataFrame
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            # Fonction pour calculer montant_dav
            def extract_dav(row):
                montant_dav = 0.0
                date_limite = dbGet.getHistoryDate()
                if not all(k in row for k in ['type_sysdate', 'debit_mvmt', 'credit_mvmt', 'open_balance']):
                    return montant_dav

                if isinstance(row['type_sysdate'], str):
                    type_sysdate_values = row['type_sysdate'].split('|')
                    debit_values = row['debit_mvmt'].split('|')
                    credit_values = row['credit_mvmt'].split('|')
                    balance_values = row['open_balance'].split('|')

                    for index, entry in enumerate(type_sysdate_values):
                        if entry == "CURACCOUNT":
                            is_valid = True
                        elif entry.startswith("CURACCOUNT-"):
                            date_part = entry.replace("CURACCOUNT-", "")
                            is_valid = date_part <= date_limite
                        else:
                            is_valid = False

                        if is_valid:
                            debit = float(debit_values[index].strip() or '0') if index < len(debit_values) else 0.0
                            credit = float(credit_values[index].strip() or '0') if index < len(credit_values) else 0.0
                            balance = float(balance_values[index].strip() or '0') if index < len(balance_values) else 0.0
                            montant_dav += debit + credit + balance

                return montant_dav

            # Calcul du montant_dav
            df['montant_dav'] = df.apply(extract_dav, axis=1)
            df['debit_dav'] = df['montant_dav'].apply(lambda x: x if x > 0 else 0.0)
            df['credit_dav'] = df['montant_dav'].apply(lambda x: -x if x < 0 else 0.0)

# Après avoir calculé montant_dav et les colonnes debit/credit
            df_unique = df.drop_duplicates(subset=['Numero_compte'], keep='first')

# Supprimer toutes les lignes existantes dans la table et ré-insérer les uniques
            conn.execute(text(f"DELETE FROM {table_name}"))

# Insérer uniquement les lignes uniques

            # Ajouter les colonnes si elles n'existent pas
            def add_column_if_not_exists(conn, table_name, column_name, column_type="DOUBLE DEFAULT 0"):
                result = conn.execute(text(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table AND COLUMN_NAME = :column
                """), {"table": table_name, "column": column_name}).fetchone()

                if not result:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))

            add_column_if_not_exists(conn, table_name, "montant_dav")
            add_column_if_not_exists(conn, table_name, "debit_dav")
            add_column_if_not_exists(conn, table_name, "credit_dav")

            df_unique.to_sql(table_name, conn, if_exists='append', index=False)

            # Mise à jour dans la table
            for idx, row in df.iterrows():
                update_query = f"""
                    UPDATE {table_name}
                    SET montant_dav = :montant_dav,
                        debit_dav = :debit_dav,
                        credit_dav = :credit_dav
                    WHERE Numero_compte = :Numero_compte
                """
                conn.execute(text(update_query), {
                    "montant_dav": row['montant_dav'],
                    "debit_dav": row['debit_dav'],
                    "credit_dav": row['credit_dav'],
                    "Numero_compte": row['Numero_compte']
                })

            conn.commit()
            print(f"[INFO] Colonne montant_dav calculée et mise à jour pour {table_name} ✅")

        except Exception as e:
            print(f"[ERREUR] calcule_dav : {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (calcule_dav) : {close_err}")
