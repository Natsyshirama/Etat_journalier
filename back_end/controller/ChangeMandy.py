from sqlalchemy import text
from db.db import DB

class ChangeMandy:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
    def create_calcul_functions(self):
        """Crée les fonctions de calcul dans MySQL"""
        try:
            with self.db.connect() as conn:
                # Création d'une fonction qui peut gérer une seule date
                create_function_query = """
                CREATE FUNCTION calculate_currency_totals(
                    p_date_debut DATE,
                    p_date_fin DATE,
                    p_unique_mode BOOLEAN
                )
                RETURNS TEXT
                DETERMINISTIC
                BEGIN
                    DECLARE result TEXT DEFAULT '';
                    DECLARE v_date_fin DATE;
                    
                    -- Si mode unique, utiliser date_debut comme date_fin
                    IF p_unique_mode THEN
                        SET v_date_fin = p_date_debut;
                    ELSE
                        SET v_date_fin = p_date_fin;
                    END IF;
                    
                    SELECT CONCAT(
                        SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 23 THEN amount_fcy_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 23 THEN amount_local_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 23 THEN amount_fcy_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 23 THEN amount_local_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 26 THEN amount_fcy_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'USD' AND transaction_code = 26 THEN amount_local_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 26 THEN amount_fcy_1 ELSE 0 END), '|',
                        SUM(CASE WHEN currency_1 = 'EUR' AND transaction_code = 26 THEN amount_local_1 ELSE 0 END)
                    ) INTO result
                    FROM teller_mcbc_his_full
                    WHERE transaction_code IN (23, 26)
                    AND (
                        (p_unique_mode AND value_date_1 = p_date_debut)
                        OR
                        (NOT p_unique_mode AND value_date_1 BETWEEN p_date_debut AND v_date_fin)
                    );
                    
                    RETURN IFNULL(result, '0|0|0|0|0|0|0|0');
                END
                """
                
                conn.execute(text("DROP FUNCTION IF EXISTS calculate_currency_totals"))
                conn.execute(text(create_function_query))
                conn.commit()
                
                print("[INFO] Fonction calculate_currency_totals créée avec succès ✅")
                return True
                
        except Exception as e:
            print(f"[ERREUR] create_calcul_functions : {e}")
            return False

    def create_unified_temp_table(self, date_debut: str, date_fin: str, unique_mode: bool = False):
        conn = None
        try:
            if unique_mode:
                where_condition = "AND tel.value_date_1 = :date_debut"
            else:
                where_condition = "AND tel.value_date_1 BETWEEN :date_debut AND :date_fin"
            
            query = f"""
                CREATE TEMPORARY TABLE temp_change_unified AS
                SELECT
                    LEFT(tel.id, LENGTH(tel.id) - 1) AS `CODE_OPERATIONS`,
                    DATE_FORMAT(tel.value_date_1, '%Y/%m/%d') AS `Date_Operation`,
                    tel.narrative_1 AS `Nom_Beneficiaire`,
                    tel.narrative_2 AS `Adresse_Beneficiaire`,
                    CASE
                        WHEN transaction_code = 26 THEN tel.narrative_1
                        ELSE NULL
                    END AS `REF_TITRE_TRANSPORT`,
                    CASE
                        WHEN transaction_code = 26 THEN ''
                        ELSE NULL
                    END AS `DESTINATION_PRINCIPALE`,
                    CASE
                        WHEN transaction_code = 26 THEN 'FOR'
                        ELSE NULL
                    END AS `NATURE_VOYAGE`,
                    tel.currency_1 AS `CODE_DEVISE`,
                    tel.deal_rate AS `COURS`,
                    tel.amount_fcy_1 AS `MONTANT_OPERATION_DEVISE`,
                    tel.amount_local_1 AS `MONTANT_CV_MGA`,
                    'BB' AS `MODE_PAIEMENT`,
                    tel.narrative_1 AS `OBSERVATIONS`,
                    tel.co_code as Agence,
                    tel.transaction_code
                FROM
                    teller_mcbc_his_full AS tel
                WHERE
                    transaction_code IN (35, 38, 23, 26)
                    {where_condition}
            """
            
            conn = self.db.connect()
            drop_query = "DROP TEMPORARY TABLE IF EXISTS temp_change_unified"
            conn.execute(text(drop_query))
            
            # Préparer les paramètres selon le mode
            params = {"date_debut": date_debut}
            if not unique_mode:
                params["date_fin"] = date_fin
                
            conn.execute(text(query), params)
            conn.commit()
            
            mode_str = "unique" if unique_mode else "période"
            print(f"[INFO] Table temporaire unifiée créée avec succès (mode {mode_str}) ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_unified_temp_table : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def create_report_tables(self, date_debut: str, date_fin: str):
        conn = None
        try:
            conn = self.db.connect()
            
            conn.execute(text("DROP TABLE IF EXISTS report_change_etat"))
            query_etat = """
                CREATE TABLE report_change_etat AS
                SELECT 
                    CODE_OPERATIONS,
                    Date_Operation,
                    Nom_Beneficiaire,
                    Adresse_Beneficiaire,
                    REF_TITRE_TRANSPORT,
                    DESTINATION_PRINCIPALE,
                    NATURE_VOYAGE,
                    CODE_DEVISE,
                    COURS,
                    MONTANT_OPERATION_DEVISE,
                    MONTANT_CV_MGA,
                    MODE_PAIEMENT,
                    OBSERVATIONS,
                    Agence
                FROM temp_change_unified
            """
            conn.execute(text(query_etat))
            
            conn.execute(text("DROP TABLE IF EXISTS report_change_allocation"))
            query_allocation = """
                CREATE TABLE report_change_allocation AS
                SELECT 
                    CODE_OPERATIONS,
                    Date_Operation,
                    Nom_Beneficiaire,
                    Adresse_Beneficiaire,
                    REF_TITRE_TRANSPORT,
                    DESTINATION_PRINCIPALE,
                    NATURE_VOYAGE,
                    CODE_DEVISE,
                    COURS,
                    MONTANT_OPERATION_DEVISE,
                    MONTANT_CV_MGA,
                    MODE_PAIEMENT,
                    OBSERVATIONS,
                    Agence
                FROM temp_change_unified 
                WHERE transaction_code = 26
            """
            conn.execute(text(query_allocation))
            
            conn.execute(text("DROP TABLE IF EXISTS report_change_synthese"))
            query_synthese = """
                CREATE TABLE report_change_synthese AS
                SELECT
                    CASE WHEN transaction_code = 23 THEN 'ACHAT' ELSE 'VENTE' END AS Type_transaction,
                    SUM(CASE WHEN CODE_DEVISE = 'EUR' THEN MONTANT_OPERATION_DEVISE ELSE 0 END) AS EUR_Montant,
                    SUM(CASE WHEN CODE_DEVISE = 'EUR' THEN MONTANT_CV_MGA ELSE 0 END) AS EUR_Montant_CV_MGA,
                    SUM(CASE WHEN CODE_DEVISE = 'USD' THEN MONTANT_OPERATION_DEVISE ELSE 0 END) AS USD_Montant,
                    SUM(CASE WHEN CODE_DEVISE = 'USD' THEN MONTANT_CV_MGA ELSE 0 END) AS USD_Montant_CV_MGA,
                    SUM(CASE WHEN CODE_DEVISE IN ('EUR','USD') THEN MONTANT_CV_MGA ELSE 0 END) AS Total_MGA
                FROM temp_change_unified
                WHERE transaction_code IN (23, 26)
                GROUP BY Type_transaction
            """
            conn.execute(text(query_synthese))
            
            conn.commit()
            print("[INFO] Tables de rapport créées avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_report_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def get_report_data(self):
        conn = None
        try:
            conn = self.db.connect()
            
            result_etat = conn.execute(text("SELECT * FROM report_change_etat"))
            etat_data = [dict(row._mapping) for row in result_etat]
            
            result_allocation = conn.execute(text("SELECT * FROM report_change_allocation"))
            allocation_data = [dict(row._mapping) for row in result_allocation]
            
            result_synthese = conn.execute(text("SELECT * FROM report_change_synthese"))
            synthese_data = [dict(row._mapping) for row in result_synthese]
            
            return {
                
                "etat": etat_data,
                "allocation": allocation_data, 
                "synthese": synthese_data
            }
            
        except Exception as e:
            print(f"[ERREUR] get_report_data : {e}")
            return {"etat": [], "allocation": [], "synthese": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def generate_tables_report(self, date_debut: str, date_fin: str, unique_mode: bool = False):
        try:
            if not self.create_calcul_functions():
                return False
            
            if not self.create_unified_temp_table(date_debut, date_fin, unique_mode):
                return False
            
            if not self.create_report_tables(date_debut, date_fin):
                return False
            
            report_data = self.get_report_data()
            if not report_data["etat"] :
                return {
                "status": "warning",
                "message": f"Aucune donnée disponible pour générer le rapport pour  {date_debut}" if unique_mode else f"Rapport généré avec succès du {date_debut} au {date_fin}",
                "etat": [],
                "allocation": [],
                "synthese": []
            }
            
            
            return {
                "status": "success",
                "message": f"Rapport généré avec succès pour le {date_debut}" if unique_mode else f"Rapport généré avec succès du {date_debut} au {date_fin}",

                "etat": report_data["etat"],
                "allocation": report_data["allocation"],
                "synthese": report_data["synthese"]
            }
            
        except ValueError as ve:
            print(f"[ERREUR] Validation des dates : {ve}")
            return {
                "status": "error",
                "message": str(ve),
                "etat": [],
                "allocation": [],
                "synthese": []  
            }
              
        except Exception as e:
            print(f"[ERREUR] generate_tables_report : {e}")
            import traceback
            traceback.print_exc()
            return {
                    "status": "error",
                    "message": f"Erreur technique : {str(e)}",
                    "etat": [],
                    "allocation": [],
                    "synthese": []
                }

    def cleanup_tables(self):
        conn = None
        try:
            conn = self.db.connect()
            
            tables_to_drop = [
                "temp_change_unified",
                "report_change_etat", 
                "report_change_allocation",
                "report_change_synthese"
            ]
            
            for table in tables_to_drop:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            
            conn.commit()
            print("[INFO] Tables temporaires nettoyées ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] cleanup_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")