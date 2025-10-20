 
--============================================ INDEXIATION ==================================================
 
-- Table principale : aa_arrangement_mcbc_live_full
CREATE INDEX idx_arrangement_filters
    ON aa_arrangement_mcbc_live_full (product_line, arr_status, product_group);
 
CREATE INDEX idx_customer_sector
    ON customer_mcbc_live_full (sector);
 
CREATE INDEX idx_account_details_maturity
    ON aa_account_details_mcbc_live_full (maturity_date);
 
-- Table : eb_cont_bal_mcbc_live_full
CREATE INDEX idx_contract_balance_id
    ON eb_cont_bal_mcbc_live_full (id);
 
-- Table : account_mcbc_live_full
 
 
--=============================================== requête SQL ===============================================
 
DROP TABLE IF EXISTS temp_clients;
 
CREATE TABLE temp_clients AS
    SELECT id, CONCAT(short_name, ' ', name_1) AS nom_complet, gender,salary,account_officer,phone_1,sms_1,sector,industry,street,target,legal_id
    FROM customer_mcbc_live_full;
 
--================================================ INDEXIATION SQL ===============================================
 
CREATE INDEX idx_client_id ON temp_clients (id(255));  
CREATE INDEX idx_account_officer ON temp_clients (account_officer(255));
CREATE INDEX idx_phone_1 ON temp_clients (phone_1(255));
CREATE INDEX idx_sms_1 ON temp_clients (sms_1(255));
CREATE INDEX idx_industry ON temp_clients (industry(255));
CREATE INDEX idx_gender ON temp_clients (gender(255));
CREATE INDEX idx_salary ON temp_clients (salary(255));
CREATE INDEX idx_sector ON temp_clients (sector(255));
CREATE INDEX idx_target ON temp_clients (target(255));
CREATE INDEX idx_legal_id ON temp_clients (legal_id(255));
CREATE INDEX idx_street ON temp_clients (street(255));
 
--=============================================== Function SQL ===============================================
DROP FUNCTION IF EXISTS solde_account;
DELIMITER $$

CREATE FUNCTION solde_account(
    type_sysdate TEXT,
    open_balance TEXT,
    credit_mvmt TEXT,
    debit_mvmt TEXT,
    date_limite INT  -- Nouveau paramètre
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

    -- PLUS BESOIN de déclarer date_limite ici, c'est maintenant un paramètre
    -- DECLARE date_limite INT DEFAULT 20250915;  <-- SUPPRIMÉ

    -- Initialisation des chaînes
    SET remaining_type = type_sysdate;
    SET remaining_open = open_balance;
    SET remaining_credit = credit_mvmt;
    SET remaining_debit = debit_mvmt;

    -- Boucle principale (identique)
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

        ELSEIF token LIKE 'CURACCOUNT-%' THEN
            SET date_part = CAST(SUBSTRING(token, LOCATE('-', token) + 1) AS UNSIGNED);

            IF date_part <= date_limite THEN  -- Utilise le paramètre ici
                SET sold_total = sold_total + open_val + credit_val + debit_val;
            END IF;
        END IF;

    END WHILE;

    -- Retourne le total converti en chaîne
    RETURN CAST(sold_total AS CHAR);
END$$

DELIMITER ;


--=============================================== requête SQL ================================================
 
 
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import math



engine = create_engine(
    "mysql+pymysql://root@localhost/dfe",
    connect_args={"connect_timeout": 10}
)

# Requête SQL mise à jour pour récupérer les informations nécessaires
sql_query = """

SELECT
    arrangement.co_code AS Agence,
    arrangement.customer AS code_client,
    arrangement.linked_appl_id AS Numero_compte,
    arrangement.product AS Produits,
    customer.nom_complet AS Nom_compte,
    customer.street AS Adresse,
    customer.sms_1 AS Contact,
    customer.gender AS Titre,
    customer.industry,
    customer.target,
    customer.legal_id AS Identification_Personne,
    NULL AS taux_d_interet,
    arrangement.product_group AS Type_Produit,
    solde_account(contract_balance.type_sysdate, contract_balance.open_balance, contract_balance.credit_mvmt, contract_balance.debit_mvmt)  AS solde,
    account.opening_date AS Date_effet,
    account_details.maturity_date AS date_echeance,
    customer.account_officer AS chargé_clientele,
    CASE
        WHEN customer.sector = 1000 THEN 'Particulier'
        ELSE 'Morale'
    END AS categorie
FROM
    aa_arrangement_mcbc_live_full AS arrangement
INNER JOIN
    aa_account_details_mcbc_live_full AS account_details
    ON account_details.id = arrangement.id
LEFT JOIN
    temp_clients AS customer
    ON customer.id= arrangement.customer
LEFT JOIN
    eb_cont_bal_mcbc_live_full AS contract_balance
    ON contract_balance.id = arrangement.linked_appl_id
LEFT JOIN account_mcbc_live_full AS account
    ON account.id = arrangement.linked_appl_id
WHERE
    arrangement.product_line='ACCOUNTS'
    AND arrangement.arr_status IN ('AUTH', 'CURRENT','PENDING.CLOSURE')
    AND arrangement.product_group ='DV.SP.MG';
    """
df = pd.read_sql(sql_query, engine)
# Fonction pour supprimer les doublons exacts dans Nom_compte
def remove_duplicate_name(name):
    if pd.isnull(name):
        return name
    words = name.strip().split()
    half = len(words) // 2
    if len(words) % 2 == 0 and words[:half] == words[half:]:
        return ' '.join(words[:half])
    return name

# Appliquer le nettoyage seulement aux clients Morale (categorie != 'Particulier')
df.loc[df['categorie'] != 'Particulier', 'Nom_compte'] = (
    df.loc[df['categorie'] != 'Particulier', 'Nom_compte']
    .apply(remove_duplicate_name)
)

df['solde'] = pd.to_numeric(df['solde'], errors='coerce')
# Colonnes Credit et Debit sans apply
df['Credit'] = df['solde'].where(df['solde'] > 0)
df['Debit'] = df['solde'].where(df['solde'] < 0)



# Exporter les résultats en CSV
df.to_excel('output/DAVSqlteste.xlsx', index=False)
