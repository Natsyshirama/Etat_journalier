import pandas as pd
from sqlalchemy import text ,String
from controller.DbGet import DbGet
import math
from db.db import DB

dbGet = DbGet()

class DavUnique:
    def __init__(self):
        self.db = DB()  
        self.engine = self.db.engine

    def create_temp_client(self):
       
        
        try:
            
            query = f"""
            CREATE TABLE temp_clients AS
                SELECT id, CONCAT(short_name, ' ', name_1) AS nom_complet, gender,salary,account_officer,phone_1,sms_1,sector,industry,street,target,legal_id
                FROM customer_mcbc_live_full;
            """
            with self.db.connect() as conn:
                drop_query = "DROP TABLE IF EXISTS temp_clients"
                conn.execute(text(drop_query))
                
                conn.execute(text(query))
                conn.commit()
            
            
            print(f"[INFO] Table temporaire temp_client créée  ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] creation table temporaire temp_client erreur : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tabletemp_client) : {close_err}")

    def create_index(self):
       
        index = [
                " CREATE INDEX IF NOT EXISTS idx_client_id ON temp_clients (id(255))",

                " CREATE INDEX IF NOT EXISTS idx_account_officer ON temp_clients (account_officer(255))",

                " CREATE INDEX IF NOT EXISTS idx_phone_1 ON temp_clients (phone_1(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_sms_1 ON temp_clients (sms_1(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_industry ON temp_clients (industry(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_gender ON temp_clients (gender(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_salary ON temp_clients (salary(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_sector ON temp_clients (sector(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_target ON temp_clients (target(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_legal_id ON temp_clients (legal_id(255))",
                
                " CREATE INDEX IF NOT EXISTS idx_street ON temp_clients (street(255))",
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
          
          
          
    def create_funct(self):
        try:
            
            query = """
            
    CREATE FUNCTION solde_account(
        type_sysdate TEXT,
        open_balance TEXT,
        credit_mvmt TEXT,
        debit_mvmt TEXT,
        date_limite INT
    )
    RETURNS TEXT
    DETERMINISTIC
    BEGIN
        -- Variables de travail
        DECLARE token TEXT;
        DECLARE remaining_type TEXT;
        DECLARE remaining_open TEXT;
        DECLARE remaining_credit TEXT;
        DECLARE remaining_debit TEXT;

        DECLARE sep_pos INT;
        DECLARE open_val DECIMAL(20,2);
        DECLARE credit_val DECIMAL(20,2);
        DECLARE debit_val DECIMAL(20,2);
        DECLARE sold_total DECIMAL(20,2) DEFAULT 0;
        DECLARE date_part INT;

        -- Initialisation des chaînes
        SET remaining_type = type_sysdate;
        SET remaining_open = open_balance;
        SET remaining_credit = credit_mvmt;
        SET remaining_debit = debit_mvmt;

        -- Boucle principale
        WHILE LENGTH(remaining_type) > 0 DO
            -- Extraction du token actuel
            SET sep_pos = LOCATE('|', remaining_type);
            IF sep_pos = 0 THEN
                SET token = remaining_type;
                SET remaining_type = '';
            ELSE
                SET token = LEFT(remaining_type, sep_pos - 1);
                SET remaining_type = SUBSTRING(remaining_type, sep_pos + 1);
            END IF;

            -- open_balance
            SET sep_pos = LOCATE('|', remaining_open);
            IF sep_pos = 0 THEN
                SET open_val = IF(remaining_open = '' OR remaining_open IS NULL, 0, CAST(remaining_open AS DECIMAL(20,2)));
                SET remaining_open = '';
            ELSE
                SET open_val = IF(LEFT(remaining_open, sep_pos - 1) = '' OR LEFT(remaining_open, sep_pos - 1) IS NULL,
                                0, CAST(LEFT(remaining_open, sep_pos - 1) AS DECIMAL(20,2)));
                SET remaining_open = SUBSTRING(remaining_open, sep_pos + 1);
            END IF;

            -- credit_mvmt
            SET sep_pos = LOCATE('|', remaining_credit);
            IF sep_pos = 0 THEN
                SET credit_val = IF(remaining_credit = '' OR remaining_credit IS NULL, 0, CAST(remaining_credit AS DECIMAL(20,2)));
                SET remaining_credit = '';
            ELSE
                SET credit_val = IF(LEFT(remaining_credit, sep_pos - 1) = '' OR LEFT(remaining_credit, sep_pos - 1) IS NULL,
                                    0, CAST(LEFT(remaining_credit, sep_pos - 1) AS DECIMAL(20,2)));
                SET remaining_credit = SUBSTRING(remaining_credit, sep_pos + 1);
            END IF;

            -- debit_mvmt
            SET sep_pos = LOCATE('|', remaining_debit);
            IF sep_pos = 0 THEN
                SET debit_val = IF(remaining_debit = '' OR remaining_debit IS NULL, 0, CAST(remaining_debit AS DECIMAL(20,2)));
                SET remaining_debit = '';
            ELSE
                SET debit_val = IF(LEFT(remaining_debit, sep_pos - 1) = '' OR LEFT(remaining_debit, sep_pos - 1) IS NULL,
                                0, CAST(LEFT(remaining_debit, sep_pos - 1) AS DECIMAL(20,2)));
                SET remaining_debit = SUBSTRING(remaining_debit, sep_pos + 1);
            END IF;

            -- Filtrage et ajout au total
            IF token = 'CURACCOUNT' THEN
                SET sold_total = sold_total + open_val + credit_val + debit_val;

            ELSEIF token LIKE 'CURACCOUNT-%%' THEN
                SET date_part = CAST(SUBSTRING(token, LOCATE('-', token) + 1) AS UNSIGNED);

                IF date_part <= date_limite THEN
                    SET sold_total = sold_total + open_val + credit_val + debit_val;
                END IF;
            END IF;

        END WHILE;

        -- Retourne le total converti en chaîne
        RETURN CAST(sold_total AS CHAR);
    END
    """

            with self.db.connect() as conn:
                drop_query = "DROP FUNCTION IF EXISTS solde_account"
                conn.execute(text(drop_query))
                conn.commit()
                
                conn.execute(text(query))
                conn.commit()
            
            print(f"[INFO] Function solde_account créée avec succès ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] création function solde_account erreur : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (creation function solde_account) : {close_err}")
         
              
                    
    def create_table_dav(self, name: str):
        
        try:
            table_name = f"dav_{name}"
            
            
            query = f"""
                
                CREATE TABLE {table_name} AS
                SELECT
                    arr.co_code AS Agence,
                    arr.customer AS code_client,
                    arr.linked_appl_id AS Numero_compte,
                    arr.product AS Produits,
                    CASE 
                        WHEN cust.sector != 1000 AND cust.nom_complet IS NOT NULL THEN
                            CASE 
                                WHEN cust.nom_complet LIKE '% % %' THEN 
                                    SUBSTRING_INDEX(cust.nom_complet, ' ', 
                                        (LENGTH(cust.nom_complet) - LENGTH(REPLACE(cust.nom_complet, ' ', '')) + 1) DIV 2)
                                ELSE cust.nom_complet
                            END
                        ELSE cust.nom_complet
                    END AS Nom_compte,
                    cust.street AS Adresse,
                    cust.sms_1 AS Contact,
                    cust.gender AS Titre,
                    cust.industry,
                    cust.target,
                    cust.legal_id AS Identification_Personne,
                    NULL AS taux_d_interet,
                    arr.product_group AS Type_Produit,
                    -- Calcul du solde UNE SEULE FOIS
                    CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)) AS solde,
                    -- Colonnes calculées
                    GREATEST(CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)), 0) AS Credit,
                    ABS(LEAST(CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)), 0)) AS Debit,
                    acc.opening_date AS Date_effet,
                    acc_det.maturity_date AS date_echeance,
                    cust.account_officer AS chargé_clientele,
                    CASE 
                        WHEN cust.sector = 1000 THEN 'Particulier' 
                        ELSE 'Morale' 
                    END AS categorie
                FROM aa_arrangement_mcbc_live_full arr
                INNER JOIN aa_account_details_mcbc_live_full acc_det ON acc_det.id = arr.id
                LEFT JOIN temp_clients cust ON cust.id = arr.customer
                LEFT JOIN eb_cont_bal_mcbc_live_full cb ON cb.id = arr.linked_appl_id
                LEFT JOIN account_mcbc_live_full acc ON acc.id = arr.linked_appl_id
                WHERE arr.product_line = 'ACCOUNTS'
                    AND arr.arr_status IN ('AUTH', 'CURRENT','PENDING.CLOSURE')
                    AND arr.product_group = 'DV.SP.MG' LIMIT 100;
            """
            
            with self.db.connect() as conn:
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                conn.execute(text(drop_query))
                conn.execute(text(query))
                conn.commit()
            
            print(f"[INFO] Table {table_name} créée ")
            return table_name
            
        except Exception as e:
            print(f"[ERREUR] Version ultra-rapide : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_table_dav_ultra_fast) : {close_err}")
        
                    
    def create_table_epr(self, name: str):
        
        try:
            table_name = f"epr_{name}"
            
            # Solution 1: Sans CTE - direct
            query = f"""
                
                CREATE TABLE {table_name} AS
                SELECT
                    arr.co_code AS Agence,
                    arr.customer AS code_client,
                    arr.linked_appl_id AS Numero_compte,
                    arr.product AS Produits,
                    CASE 
                        WHEN cust.sector != 1000 AND cust.nom_complet IS NOT NULL THEN
                            CASE 
                                WHEN cust.nom_complet LIKE '% % %' THEN 
                                    SUBSTRING_INDEX(cust.nom_complet, ' ', 
                                        (LENGTH(cust.nom_complet) - LENGTH(REPLACE(cust.nom_complet, ' ', '')) + 1) DIV 2)
                                ELSE cust.nom_complet
                            END
                        ELSE cust.nom_complet
                    END AS Nom_compte,
                    cust.street AS Adresse,
                    cust.sms_1 AS Contact,
                    cust.gender AS Titre,
                    cust.industry,
                    cust.target,
                    cust.legal_id AS Identification_Personne,
                    NULL AS taux_d_interet,
                    arr.product_group AS Type_Produit,
                    -- Calcul du solde UNE SEULE FOIS
                    CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)) AS solde,
                    -- Colonnes calculées
                    GREATEST(CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)), 0) AS Credit,
                    ABS(LEAST(CAST(solde_account(
                        cb.type_sysdate, 
                        cb.open_balance, 
                        cb.credit_mvmt, 
                        cb.debit_mvmt,
                        {name} 
                    ) AS DECIMAL(20,2)), 0)) AS Debit,
                    acc.opening_date AS Date_effet,
                    acc_det.maturity_date AS date_echeance,
                    cust.account_officer AS chargé_clientele,
                    CASE 
                        WHEN cust.sector = 1000 THEN 'Particulier' 
                        ELSE 'Morale' 
                    END AS categorie
                FROM aa_arrangement_mcbc_live_full arr
                INNER JOIN aa_account_details_mcbc_live_full acc_det ON acc_det.id = arr.id
                LEFT JOIN temp_clients cust ON cust.id = arr.customer
                LEFT JOIN eb_cont_bal_mcbc_live_full cb ON cb.id = arr.linked_appl_id
                LEFT JOIN account_mcbc_live_full acc ON acc.id = arr.linked_appl_id
                WHERE arr.product_line = 'ACCOUNTS'
                    AND arr.arr_status IN ('AUTH', 'CURRENT')
                    AND arr.product_group = 'EPN.SP.MG' LIMIT 100;
            """
            
            with self.db.connect() as conn:
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                conn.execute(text(drop_query))
                conn.execute(text(query))
                conn.commit()
            
            print(f"[INFO] Table {table_name} créée (ULTRA RAPIDE) ⚡")
            return table_name
            
        except Exception as e:
            print(f"[ERREUR] Version ultra-rapide : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_table_dav_ultra_fast) : {close_err}")
        
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

            query_nulls = f"""
            UPDATE {table_name}
            SET 
                debit_mvmt   = COALESCE(debit_mvmt, 0),
                credit_mvmt  = COALESCE(credit_mvmt, 0),
                open_balance = COALESCE(open_balance, 0);
            """
            conn.execute(text(query_nulls))

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

 