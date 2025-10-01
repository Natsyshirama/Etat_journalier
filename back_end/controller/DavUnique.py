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
       
        conn = None
        try:
             # Créer la table arrangement_customer si elle n'existe pas déjà
            query = f"""CREATE TABLE IF NOT EXISTS arrangement_customer (
                    arrangement_id VARCHAR(50) NOT NULL,
                    customer_id VARCHAR(50) NOT NULL,
                    PRIMARY KEY (arrangement_id, customer_id)
                ) ;
            """
            conn = self.db.connect()
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
  
        conn = None
        try:
            conn= self.db.connect()
            
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

            print(f"[INFO] Insertion réussie : {len(rows)} lignes insérées ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] calculeAmtCap : {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (calculeAmtCap) : {close_err}")
                    
                    
    def create_index(self):
       
        index = [
                " CREATE INDEX IF NOT EXISTS idx_arrangement_id ON arrangement_customer (arrangement_id)",

                " CREATE INDEX IF NOT EXISTS idx_interest_id ON aa_arr_interest_mcbc_live_full (id(255))",

                " CREATE INDEX IF NOT EXISTS  idx_customer_id ON arrangement_customer (customer_id)",
                
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
                    
                    
    def create_table_dav(self,name: str):
       
        conn = None
        try:
            
            
            
            table_name = f"dav_{name}"
            
            query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} AS
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
                    NULL AS taux_d_interet,
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
                    AND arrangement.product_group IN ('DV.SP.MG') LIMIT 100;
                """
                
            conn = self.db.connect()
            conn.execute(text(query))
            conn.commit()
            
            print(f"[INFO] Création de la table {table_name} en cours... ✅")
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

    def update_statusHistoryInsert(self, name: str):
            conn = None
            try:
                conn = self.db.connect()
                
                query = f"""
                        UPDATE history_insert
                        SET dav_status = true
                        WHERE label = '{name}';
                """
                conn.execute(text(query))
                conn.commit()
                
                print(f"[INFO] history_insert mis à jour pour {name} ✅")
                return True
                
            except Exception as e:
                print(f"[ERREUR] clean_tableDatPreCompute : {e}")
                return None
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception as close_err:
                        print(f"[ERREUR] Fermeture connexion (clean_tableDatPreCompute) : {close_err}")
                
    
                
    def traitement_dav(self, table_name: str):
        
        conn = None
        try:
            conn = self.db.connect()

            # Remplacer NULL par 0
            query_nulls = f"""
            UPDATE {table_name}
            SET 
                debit_mvmt   = COALESCE(debit_mvmt, 0),
                credit_mvmt  = COALESCE(credit_mvmt, 0),
                open_balance = COALESCE(open_balance, 0);
            """
            conn.execute(text(query_nulls))

            # Nettoyer code_client (prendre la première partie avant '|')
            query_code_client = f"""
            UPDATE {table_name}
            SET code_client = SUBSTRING_INDEX(code_client, '|', 1);
            """
            conn.execute(text(query_code_client))
            
            query_dedup = f"""
                DELETE t1 FROM {table_name} t1
                INNER JOIN {table_name} t2
                ON t1.Agence = t2.Agence
                AND t1.code_client = t2.code_client
                AND t1.Numero_compte = t2.Numero_compte
                AND t1.Produits = t2.Produits
                AND t1.id_comp_2 < t2.id_comp_2;
                """
            conn.execute(text(query_dedup))
            conn.commit()
            
           

            # Supprimer colonnes inutiles
            query_drop_cols = f"""
            ALTER TABLE {table_name}
            DROP COLUMN type_sysdate,
            DROP COLUMN debit_mvmt,
            DROP COLUMN open_balance,
            DROP COLUMN credit_mvmt;
            """
            conn.execute(text(query_drop_cols))
            conn.commit()
            print(f"[INFO] Nettoyage terminé pour {table_name} ✅")

        except Exception as e:
            print(f"[ERREUR] clean_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (clean_tableDatPreCompute) : {close_err}")

 