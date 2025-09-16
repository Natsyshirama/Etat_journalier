from sqlalchemy import text
from db.db import DB

class DbGet:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine

    def getHistoryDate(self):
        """
        Récupère le label actif dans history_mcbd
        """
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT label 
                FROM history_mcbd 
                WHERE used = 1 
                LIMIT 1
            """)
            result = conn.execute(query).fetchone()
            if result:
                return str(result[0])
            return None
        except Exception as e:
            print(f"[ERREUR] getHistory : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getHistory) : {close_err}")

    def create_tableDatPreCompute(self):
        """
        Crée une table DAT_<label> pré-calculée
        """
        conn = None
        try:
            # Récupération du label dynamique
            label = self.getHistoryDate()
            if not label:
                raise ValueError("Aucun label trouvé dans history_mcbd avec used=1")

            table_name = f"DAT_{label}"

            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT 
                arrangement.co_code AS Agence, 
                arrangement.customer AS code_client,
                arrangement.linked_appl_id AS Numero_compte,
                arrangement.product AS Produits,
                customer.name_1 AS Nom_compte,
                customer.street AS Adresse,
                customer.sms_1 AS Contact,
                cb.open_balance,
                cb.debit_mvmt,
                cb.credit_mvmt,
                cb.open_balance + cb.debit_mvmt - cb.credit_mvmt AS solde_calcule
            FROM 
                aa_arrangement_mcbc_live_full AS arrangement
            INNER JOIN aa_account_details_mcbc_live_full AS account_details
                ON account_details.id = arrangement.id
            LEFT JOIN customer_mcbc_live_full_partie_1 AS customer
                ON arrangement.customer = customer.id
            LEFT JOIN eb_cont_bal_mcbc_live_full AS cb
                ON cb.id = arrangement.linked_appl_id
            WHERE 
                arrangement.product_line = 'DEPOSITS'
                AND arrangement.arr_status IN ('AUTH', 'CURRENT')
                AND arrangement.product_group = 'DAT.SP.MG';
            """

            conn = self.db.connect()
            conn.execute(text(query))
            conn.commit()  # important pour valider la création

            print(f"[INFO] Table {table_name} créée avec succès ✅")
            return table_name

        except Exception as e:
            print(f"[ERREUR] create_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableDatPreCompute) : {close_err}")
