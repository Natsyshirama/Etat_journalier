import pandas as pd
from sqlalchemy import text ,String
from controller.DbGet import DbGet
import math
from db.db import DB

dbGet = DbGet()

class DavUnique:
    def __init__(self):
        self.db = DB()  # engine SQLAlchemy
        self.engine = self.db.engine

    def create_table_arrCust(self):
        """
        creation du table arrangement_customer
        """
        conn = None
        try:
             # Créer la table arrangement_customer si elle n'existe pas déjà
            query = f"""CREATE TABLE IF NOT EXISTS arrangement_customer (
                    arrangement_id VARCHAR(50) NOT NULL,
                    customer_id VARCHAR(50) NOT NULL,
                    PRIMARY KEY (arrangement_id, customer_id)
                ) ;
            """
            conn = None
            conn.execute(text(query))
            conn.commit()
            
            print(f"[INFO] Table arrangement_customer créée ou déjà existante ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] create_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableDatPreCompute) : {close_err}")


    def insert_data_arrCust(self):
        """
        insertion des données dans arrangement_customer
        """
        conn = None
        try:
            conn.self.db.connect()
            
            df = pd.read_sql( "SELECT id AS arrangement_id, customer FROM aa_arrangement_mcbc_live_full", conn)
            # Étape 2 : Transformation -> explode customer (séparé par '|')
            rows = []
            for _, row in df.iterrows():
                arrangement_id = row["arrangement_id"]
                customers = str(row["customer"]).split("|") if row["customer"] else []
                for cust in customers:
                    if cust.strip():  # éviter les vides
                        rows.append((arrangement_id, cust.strip()))

            if not rows:
                print("[INFO] Aucune donnée à insérer dans arrangement_customer")
                return

            # Étape 3 : Insérer par batch
            
            insert_query = text("""
                INSERT IGNORE INTO arrangement_customer (arrangement_id, customer_id)
                VALUES (:arrangement_id, :customer_id)
            """)

            conn.execute(insert_query, [{"arrangement_id": a, "customer_id": c} for a, c in rows])
            conn.commit()
            conn.close()

            print(f"[INFO] Insertion réussie : {len(rows)} lignes insérées ✅")
    
        except Exception as e:
            print(f"[ERREUR] calculeAmtCap : {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (calculeAmtCap) : {close_err}")
                    
                    
    def create_index(self):
        """
        creation des index pour arrangement_customer
        """
        index = [
                " CREATE INDEX  idx_arrangement_id ON arrangement_customer (arrangement_id)",

                " CREATE INDEX idx_interest_id ON aa_arr_interest_mcbc_live_full (id(255))",

                " CREATE INDEX  idx_customer_id ON arrangement_customer (customer_id)",
                
                "CREATE UNIQUE INDEX  idx_arr_cust ON arrangement_customer (arrangement_id, customer_id)"
                ]
                
        conn = None
        try:
            conn = self.db.connect()
            for q in index:
                conn.execute(text(q))
                conn.commit()
                print(f"[INFO] Index créé ou déjà existant ✅ {q}")
            return True
        except Exception as e:
            print(f"[ERREUR] create_index : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_index) : {close_err}")
                    
                    
    def create_table_dav(self):
        """
            creation du table dat_dav_uniquecr
        """
        conn = None
        try:
            
            label = dbGet.getHistoryDate()
            
            table_name = f"dav_{label}"
            
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                WITH resolved_customer AS (
                    SELECT DISTINCT
                    ac.arrangement_id,
                    CASE 
                        WHEN c.sector = 1000 THEN CONCAT(c.short_name, ' ', c.name_1)
                        ELSE c.name_1
                    END AS Nom_compte
                FROM arrangement_customer ac
                JOIN customer_mcbc_live_full c
                ON ac.customer_id = c.id  
                        )
                        
                SELECT 
                    arrangement.co_code AS Agence, 
                    arrangement.customer AS code_client,
                    arrangement.linked_appl_id AS Numero_compte,
                    arrangement.product AS Produits,
                    rc.Nom_compte,
                    customer.street AS Adresse,
                    customer.sms_1 AS Contact,
                    customer.gender AS Titre,
                    customer.industry,
                    customer.target,
                    customer.legal_id AS Identification_Personne,
                    NULL AS taux_d_interet, -- remplacé les multiples CASE qui renvoyaient NULL
                    arrangement.product_group AS Type_Produit,
                    contract_balance.open_balance AS open_balance,
                    contract_balance.debit_mvmt AS debit_mvmt,
                    contract_balance.credit_mvmt AS credit_mvmt,
                    account.opening_date AS Date_effet,
                    TIMESTAMPDIFF(MONTH, arrangement.start_date, account_details.maturity_date) AS Durée_en_mois,
                    DATEDIFF(account_details.maturity_date, arrangement.start_date) AS Durée_en_jours, 
                    account_details.maturity_date AS date_echeance,
                    customer.account_officer AS chargé_clientele,
                    CASE
                        WHEN customer.sector = 1000 THEN 'Particulier'
                        ELSE 'Morale'
                    END AS categorie,
                    contract_balance.type_sysdate,
                    interet.id AS id_comp_2

                FROM 
                    aa_arrangement_mcbc_live_full AS arrangement
                INNER JOIN 
                    aa_account_details_mcbc_live_full AS account_details
                    ON account_details.id = arrangement.id
                LEFT JOIN 
                    customer_mcbc_live_full AS customer
                    ON arrangement.customer = customer.id
                LEFT JOIN 
                    eb_cont_bal_mcbc_live_full AS contract_balance
                    ON contract_balance.id = arrangement.linked_appl_id
                LEFT JOIN 
                    account_mcbc_live_full AS account
                    ON account.id = arrangement.linked_appl_id 
                LEFT JOIN 
                    aa_arr_interest_mcbc_live_full AS interet
                    ON SUBSTRING_INDEX(interet.id, '-', 1) = arrangement.id
                LEFT JOIN 
                    resolved_customer rc
                    ON rc.arrangement_id = arrangement.id

                WHERE 
                    arrangement.product_line IN ('ACCOUNTS')
                    AND arrangement.arr_status IN ('AUTH', 'CURRENT','PENDING.CLOSURE')
                    AND arrangement.product_group IN ('DV.SP.MG') LIMIT 100 ;

            )
            """
            
            conn = self.db.connect()
            conn.execute(text(query))
            conn.commit()
        except Exception as e:
            print(f"[ERREUR] create_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableDatPreCompute) : {close_err}")

   