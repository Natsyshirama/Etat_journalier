from sqlalchemy import text
from db.db import DB

class DecaissementOptimise:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
    def create_capital_function(self):
        """Crée une fonction MySQL pour calculer le montant capital"""
        try:
            query = """
            CREATE FUNCTION calcul_montant_capital(
                type_sysdate TEXT,
                debit_mvmt TEXT,
                credit_mvmt TEXT,
                open_balance TEXT
            )
            RETURNS DECIMAL(20,2)
            DETERMINISTIC
            BEGIN
                DECLARE token TEXT;
                DECLARE remaining_type TEXT;
                DECLARE remaining_debit TEXT;
                DECLARE remaining_credit TEXT;
                DECLARE remaining_open TEXT;
                
                DECLARE sep_pos INT;
                DECLARE debit_val DECIMAL(20,2);
                DECLARE credit_val DECIMAL(20,2);
                DECLARE open_val DECIMAL(20,2);
                DECLARE montant_total DECIMAL(20,2) DEFAULT 0;

                -- Initialisation des chaînes
                SET remaining_type = type_sysdate;
                SET remaining_debit = debit_mvmt;
                SET remaining_credit = credit_mvmt;
                SET remaining_open = open_balance;

                -- Boucle principale
                WHILE LENGTH(remaining_type) > 0 DO
                    -- Extraction du token type_sysdate
                    SET sep_pos = LOCATE('|', remaining_type);
                    IF sep_pos = 0 THEN
                        SET token = remaining_type;
                        SET remaining_type = '';
                    ELSE
                        SET token = LEFT(remaining_type, sep_pos - 1);
                        SET remaining_type = SUBSTRING(remaining_type, sep_pos + 1);
                    END IF;

                    -- Extraction debit_mvmt
                    SET sep_pos = LOCATE('|', remaining_debit);
                    IF sep_pos = 0 THEN
                        SET debit_val = IF(remaining_debit = '' OR remaining_debit IS NULL, 0, 
                                         CAST(remaining_debit AS DECIMAL(20,2)));
                        SET remaining_debit = '';
                    ELSE
                        SET debit_val = IF(LEFT(remaining_debit, sep_pos - 1) = '' OR LEFT(remaining_debit, sep_pos - 1) IS NULL,
                                        0, CAST(LEFT(remaining_debit, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_debit = SUBSTRING(remaining_debit, sep_pos + 1);
                    END IF;

                    -- Extraction credit_mvmt
                    SET sep_pos = LOCATE('|', remaining_credit);
                    IF sep_pos = 0 THEN
                        SET credit_val = IF(remaining_credit = '' OR remaining_credit IS NULL, 0, 
                                          CAST(remaining_credit AS DECIMAL(20,2)));
                        SET remaining_credit = '';
                    ELSE
                        SET credit_val = IF(LEFT(remaining_credit, sep_pos - 1) = '' OR LEFT(remaining_credit, sep_pos - 1) IS NULL,
                                         0, CAST(LEFT(remaining_credit, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_credit = SUBSTRING(remaining_credit, sep_pos + 1);
                    END IF;

                    -- Extraction open_balance
                    SET sep_pos = LOCATE('|', remaining_open);
                    IF sep_pos = 0 THEN
                        SET open_val = IF(remaining_open = '' OR remaining_open IS NULL, 0, 
                                        CAST(remaining_open AS DECIMAL(20,2)));
                        SET remaining_open = '';
                    ELSE
                        SET open_val = IF(LEFT(remaining_open, sep_pos - 1) = '' OR LEFT(remaining_open, sep_pos - 1) IS NULL,
                                        0, CAST(LEFT(remaining_open, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_open = SUBSTRING(remaining_open, sep_pos + 1);
                    END IF;

                    -- Calcul pour TOTCOMMITMENT
                    IF token = 'TOTCOMMITMENT' OR token LIKE 'TOTCOMMITMENT-2024%' OR token LIKE 'TOTCOMMITMENT-2025%' THEN
                        SET montant_total = montant_total + debit_val + credit_val + open_val;
                    END IF;

                END WHILE;

                RETURN montant_total;
            END
            """

            with self.db.connect() as conn:
                drop_query = "DROP FUNCTION IF EXISTS calcul_montant_capital"
                conn.execute(text(drop_query))
                conn.commit()
                
                conn.execute(text(query))
                conn.commit()
            
            print("[INFO] Function calcul_montant_capital créée avec succès ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] création function calcul_montant_capital : {e}")
            return False

    def create_frais_dossier_function(self):
        """Crée une fonction MySQL pour calculer les frais de dossier"""
        try:
            query = """
            CREATE FUNCTION calcul_frais_dossier(
                montant_capital DECIMAL(20,2),
                charge_rate DECIMAL(10,4)
            )
            RETURNS DECIMAL(20,2)
            DETERMINISTIC
            BEGIN
                DECLARE frais DECIMAL(20,2);
                
                IF montant_capital IS NULL OR charge_rate IS NULL THEN
                    RETURN NULL;
                END IF;
                
                SET frais = montant_capital * (charge_rate / 100);
                RETURN frais;
            END
            """

            with self.db.connect() as conn:
                drop_query = "DROP FUNCTION IF EXISTS calcul_frais_dossier"
                conn.execute(text(drop_query))
                conn.commit()
                
                conn.execute(text(query))
                conn.commit()
            
            print("[INFO] Function calcul_frais_dossier créée avec succès ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] création function calcul_frais_dossier : {e}")
            return False

    def create_temp_clients_table(self):
        """Crée une table temporaire pour les clients optimisée"""
        try:
            query = """
                CREATE TEMPORARY TABLE temp_clients_decaissement AS
                SELECT 
                    id,
                    CONCAT(short_name, ' ', name_1) AS nom_complet,
                    industry,
                    gender,
                    sector
                FROM customer_mcbc_live_full
            """
            
            with self.db.connect() as conn:
                drop_query = "DROP TEMPORARY TABLE IF EXISTS temp_clients_decaissement"
                conn.execute(text(drop_query))
                conn.commit()

                conn.execute(text(query))
                conn.commit()
            
            print("[INFO] Table temporaire clients créée avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_temp_clients_table : {e}")
            return False

    def create_indexes(self):
        """Crée les index optimisés"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_arrangement_id ON aa_arrangement_mcbc_live_full (id(255))",
            "CREATE INDEX IF NOT EXISTS idx_arrangement_customer ON aa_arrangement_mcbc_live_full (customer(255))",
            "CREATE INDEX IF NOT EXISTS idx_arrangement_linked_appl ON aa_arrangement_mcbc_live_full (linked_appl_id(255))",
            "CREATE INDEX IF NOT EXISTS idx_account_opening_date ON account_mcbc_live_full (opening_date)",
            "CREATE INDEX IF NOT EXISTS idx_em_arrangement ON em_lo_application_mcbc_live_full (arrangement_id(255))"
        ]
        
        try:
            with self.db.connect() as conn:
                for index_query in indexes:
                    conn.execute(text(index_query))
                conn.commit()
            
            print("[INFO] Index créés avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_indexes : {e}")
            return False

    def create_decaissement_table(self, date_limite: str):
        """Crée la table finale de décaissement"""
        try:
            table_name = f"decaissement_{date_limite}"
            
            query = f"""
                CREATE TABLE {table_name} AS
                SELECT
                    arr.co_code AS Agence, 
                    SUBSTRING_INDEX(arr.customer, '|', 1) AS code_client,
                    arr.linked_appl_id AS Numero_compte,
                    acc_det.id as Numero_pret,
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
                    cust.industry AS Secteur_Activite,
                    cust.gender AS Titre,
                    acc.opening_date AS date_decaissement,  
                    TIMESTAMPDIFF(MONTH, acc.opening_date, acc_det.maturity_date) AS Duree,
                    arr.product AS Produits,
                    (
                        SELECT effective_rate  
                        FROM aa_arr_interest_mcbc_live_full 
                        WHERE id_comp_1 = arr.id 
                        AND id_comp_2 = 'PRINCIPALINT' 
                        LIMIT 1
                    ) AS taux_d_interet,
                    -- Calcul du montant capital avec la fonction
                    calcul_montant_capital(
                        cb.type_sysdate, 
                        cb.debit_mvmt,  
                        cb.credit_mvmt,  
                        cb.open_balance
                    ) AS montant_capital,
                    chg.charge_rate,
                    -- Calcul des frais de dossier avec la fonction
                    calcul_frais_dossier(
                        calcul_montant_capital(cb.type_sysdate, cb.debit_mvmt, cb.credit_mvmt, cb.open_balance),
                        chg.charge_rate
                    ) AS frais_de_dossier,
                    CASE
                        WHEN cust.sector = 1000 THEN 'Particulier'
                        ELSE 'Morale'
                    END AS categorie
                FROM 
                    aa_arrangement_mcbc_live_full AS arr
                INNER JOIN 
                    aa_account_details_mcbc_live_full AS acc_det
                    ON acc_det.id = arr.id
                LEFT JOIN 
                    temp_clients_decaissement AS cust
                    ON cust.id = SUBSTRING_INDEX(arr.customer, '|', 1)
                LEFT JOIN 
                    eb_cont_bal_mcbc_live_full AS cb
                    ON cb.id = arr.linked_appl_id
                LEFT JOIN 
                    account_mcbc_live_full AS acc
                    ON acc.id = arr.linked_appl_id 
                LEFT JOIN 
                    aa_arr_charge_mcbc_live_full AS chg
                    ON SUBSTRING_INDEX(chg.id, '-', 1) = arr.id  
                INNER JOIN
                    em_lo_application_mcbc_live_full AS em
                    ON em.arrangement_id = arr.id   
                WHERE 
                    arr.product_line = 'LENDING'
                    AND arr.arr_status IN ('AUTH', 'CURRENT')
                    AND acc.opening_date >= '{date_limite}'
                    AND em.proc_status = 'DISBURSED'
                GROUP BY arr.linked_appl_id LIMIT 100;
            """
            
            with self.db.connect() as conn:
                # Supprimer la table si elle existe
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                conn.execute(text(drop_query))
                conn.commit()
                
                # Créer la nouvelle table
                conn.execute(text(query))
                conn.commit()
            
            print(f"[INFO] Table {table_name} créée avec succès ✅")
            return table_name
            
        except Exception as e:
            print(f"[ERREUR] create_decaissement_table : {e}")
            return False

    def generate_decaissement_report(self, date_limite: str):
        """Génère le rapport complet de décaissement"""
        try:
            # Créer les fonctions
            if not self.create_capital_function():
                return False
                
            if not self.create_frais_dossier_function():
                return False
            
            # Créer les index
            if not self.create_indexes():
                print("[ATTENTION] Problème avec les index, continuation...")
            
            # Créer la table temporaire clients
            if not self.create_temp_clients_table():
                return False
            
            # Créer la table finale
            table_name = self.create_decaissement_table(date_limite)
            
            if not table_name:
                return False
            
            # Vérifier les résultats
            with self.db.connect() as conn:
                # Compter les enregistrements
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                result = conn.execute(text(count_query))
                count = result.fetchone()[0]
                
                # Vérifier les doublons
                duplicate_query = f"""
                    SELECT Numero_compte, COUNT(*) 
                    FROM {table_name} 
                    GROUP BY Numero_compte 
                    HAVING COUNT(*) > 1
                """
                duplicates = conn.execute(text(duplicate_query)).fetchall()
                
            print(f"[INFO] Rapport généré avec succès : {count} enregistrements")
            if duplicates:
                print(f"[ATTENTION] {len(duplicates)} doublons détectés dans Numero_compte")
            else:
                print("[INFO] Aucun doublon détecté dans Numero_compte ✅")
            
            return {
                "status": "success",
                "table_name": table_name,
                "record_count": count,
                "duplicates_count": len(duplicates)
            }
            
        except Exception as e:
            print(f"[ERREUR] generate_decaissement_report : {e}")
            return False

    def cleanup(self, table_name: str = None):
        """Nettoie les ressources temporaires"""
        try:
            with self.db.connect() as conn:
                # Supprimer les fonctions
                functions_to_drop = [
                    "calcul_montant_capital",
                    "calcul_frais_dossier"
                ]
                
                for function in functions_to_drop:
                    try:
                        conn.execute(text(f"DROP FUNCTION IF EXISTS {function}"))
                    except Exception as e:
                        print(f"[ATTENTION] Impossible de supprimer {function} : {e}")
                
                # Supprimer les tables temporaires
                temp_tables = [
                    "temp_clients_decaissement"
                ]
                
                if table_name:
                    temp_tables.append(table_name)
                
                for table in temp_tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    except Exception as e:
                        print(f"[ATTENTION] Impossible de supprimer {table} : {e}")
                
                conn.commit()
                print("[INFO] Nettoyage effectué avec succès ✅")
                
        except Exception as e:
            print(f"[ERREUR] cleanup : {e}")