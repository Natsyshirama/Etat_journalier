import re
from db.db import DB
from sqlalchemy import text

class OperationEsris:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        self.country_addresses = {
           'AD': 'Andorre', 'AE': 'Émirats Arabes Unis', 'AF': 'Afghanistan', 'AG': 'Antigua et Barbuda', 'AI': 'Anguilla',
            'AL': 'Albanie', 'AM': 'Arménie', 'AN': 'Antilles néerlandaises', 'AO': 'Angola', 'AQ': 'Antarctique',
            'AR': 'Argentine', 'AS': 'Îles Samoa', 'AT': 'Autriche', 'AU': 'Australie', 'AW': 'Aruba', 'AZ': 'Azerbaïdjan',
            'BA': 'Bosnie-Herzégovine', 'BB': 'La Barbade', 'BD': 'Bangladesh', 'BE': 'Belgique', 'BF': 'Burkina Faso',
            'BG': 'Bulgarie', 'BH': 'Bahreïn', 'BI': 'Burundi', 'BJ': 'Benin', 'BM': 'Bermudas', 'BN': 'Brunéï', 'BO': 'Bolivie',
            'BR': 'Brésil', 'BS': 'Bahamas', 'BT': 'Bhoutan', 'BV': 'Îles Bouvet', 'BW': 'Botswana', 'BY': 'Biélorussie',
            'BZ': 'Bélize', 'CA': 'Canada', 'CC': 'Îles Coco', 'CF': 'République centrafricaine', 'CG': 'Congo', 'CH': 'Suisse',
            'CI': 'Côte d\'Ivoire', 'CK': 'Îles Cook', 'CL': 'Chili', 'CM': 'Cameroun', 'CN': 'Chine', 'CO': 'Colombie', 'CR': 'Costa Rica',
            'CS': 'Tchécoslovaquie (obsolète)', 'CU': 'Cuba', 'CV': 'Cap Vert', 'CX': 'Christmas Island', 'CY': 'Chypre', 'CZ': 'Tchèque (République)',
            'DE': 'Allemagne', 'DJ': 'Djibouti', 'DK': 'Danemark', 'DM': 'Dominique', 'DO': 'République Dominicaine', 'DZ': 'Algérie',
            'EC': 'Équateur', 'EE': 'Estonie', 'EG': 'Égypte', 'EH': 'Sahara Occidental', 'ER': 'Érythrée', 'ES': 'Espagne', 'ET': 'Éthiopie',
            'FI': 'Finlande', 'FJ': 'Îles Fidji', 'FK': 'Îles Falkland', 'FM': 'Micronésie', 'FO': 'Îles Féroé', 'FR': 'France', 'FX': 'France (métropolitaine)',
            'GA': 'Gabon', 'GB': 'Royaume-Uni (UK)', 'GD': 'Grenade', 'GE': 'Géorgie', 'GF': 'Guyane Française', 'GH': 'Ghana', 'GI': 'Gibraltar',
            'GL': 'Groenland', 'GM': 'Gambie', 'GN': 'Guinée', 'GP': 'Guadeloupe', 'GQ': 'Guinée équatoriale', 'GR': 'Grèce',
            'GS': 'Géorgie du Sud et îles Sandwich du Sud', 'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinée-Bissau', 'GY': 'Guyane', 'HK': 'Hong Kong',
            'HM': 'Îles Heard et MacDonald', 'HN': 'Honduras', 'HR': 'Croatie', 'HT': 'Haïti', 'HU': 'Hongrie', 'ID': 'Indonésie', 'IE': 'Irlande',
            'IL': 'Israël', 'IN': 'Inde', 'IO': 'Océan Indien Anglais', 'IQ': 'Irak', 'IR': 'République islamique d\'Iran', 'IS': 'Islande',
            'IT': 'Italie', 'JM': 'Jamaïque', 'JO': 'Jordanie', 'JP': 'Japon', 'KE': 'Kenya', 'KG': 'Kirghizistan', 'KH': 'Cambodge', 'KI': 'Kiribati',
            'KM': 'Comores', 'KN': 'Saint-Kitts-et-Nevis', 'KP': 'Corée du Nord', 'KR': 'Corée du Sud', 'KW': 'Koweït', 'KY': 'Îles Caïmans',
            'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Liban', 'LC': 'Sainte-Lucie', 'LI': 'Liechtenstein', 'LK': 'Sri Lanka', 'LR': 'Libéria',
            'LS': 'Lesotho', 'LT': 'Lituanie', 'LU': 'Luxembourg', 'LV': 'Lettonie', 'LY': 'Libye', 'MA': 'Maroc', 'MC': 'Monaco', 'MD': 'Moldavie',
            'MG': 'Madagascar', 'MH': 'Îles Marshall', 'MK': 'Macédoine', 'ML': 'Mali', 'MM': 'Birmanie (Myanmar)', 'MN': 'Mongolie', 'MO': 'Macao',
            'MP': 'Îles Mariannes', 'MQ': 'Martinique', 'MR': 'Mauritanie', 'MS': 'Montserrat', 'MT': 'Malte', 'MU': 'Île Maurice', 'MV': 'Maldives',
            'MW': 'Malawi', 'MX': 'Mexique', 'MY': 'Malaisie', 'MZ': 'Mozambique', 'NA': 'Namibie', 'NC': 'Nouvelle-Calédonie', 'NE': 'Niger',
            'NF': 'Île Norfolk', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Pays-Bas', 'NO': 'Norvège', 'NP': 'Népal', 'NR': 'Nauru', 'NU': 'Niue',
            'NZ': 'Nouvelle-Zélande', 'OM': 'Oman', 'PA': 'Panama', 'PE': 'Pérou', 'PF': 'Polynésie Française', 'PG': 'Papouasie-Nouvelle-Guinée',
            'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Pologne', 'PM': 'Saint-Pierre-et-Miquelon', 'PN': 'Pitcairn', 'PR': 'Porto Rico',
            'PT': 'Portugal', 'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Roumanie', 'RU': 'Fédération de Russie',
            'RW': 'Rwanda', 'SA': 'Arabie Saoudite', 'SB': 'Îles Salomon', 'SC': 'Seychelles', 'SD': 'Soudan', 'SE': 'Suède', 'SG': 'Singapour',
            'SH': 'Sainte-Hélène', 'SI': 'Slovénie', 'SJ': 'Île Jan Mayen', 'SK': 'Slovaquie (République slovaque)', 'SL': 'Sierra Leone',
            'SM': 'Saint-Marin', 'SN': 'Sénégal', 'SO': 'Somalie', 'SR': 'Surinam', 'ST': 'Sao Tomé-et-Principe', 'SU': 'Union soviétique (obsolète)',
            'SV': 'Salvador', 'SY': 'Syrie', 'SZ': 'Swaziland', 'TC': 'Îles Turks-et-Caïques', 'TD': 'Tchad', 'TF': 'Territoires Antarctiques Français',
            'TG': 'Togo', 'TH': 'Thaïlande', 'TJ': 'Tadjikistan', 'TK': 'Tokelau', 'TM': 'Turkménistan', 'TN': 'Tunisie', 'TO': 'Tonga', 'TP': 'Timor',
            'TR': 'Turquie', 'TT': 'Trinité-et-Tobago', 'TV': 'Tuvalu', 'TW': 'Taïwan', 'TZ': 'Tanzanie', 'UA': 'Ukraine', 'UG': 'Ouganda', 'UK': 'Royaume-Uni',
            'UM': 'Petites îles extérieures des États-Unis', 'US': 'États-Unis', 'UY': 'Uruguay', 'UZ': 'Ouzbékistan', 'VA': 'Vatican',
            'VC': 'Saint-Vincent-et-les-Grenadines', 'VE': 'Vénézuela', 'VG': 'Îles Vierges britanniques', 'VI': 'Îles Vierges des États-Unis', 'VN': 'Vietnam',
            'VU': 'Vanuatu', 'WF': 'Îles Wallis-et-Futuna', 'WS': 'Samoa', 'YE': 'Yémen', 'YT': 'Mayotte', 'YU': 'Yougoslavie (obsolète)', 'ZA': 'Afrique du Sud',
            'ZM': 'Zambie', 'ZR': 'Zaïre', 'ZW': 'Zimbabwe'
        }
        self.countries_codes = {
            ("AF", "004"), ("ZA", "710"), ("AL", "008"), ("DZ", "12"), ("DE", "276"),
            ("AD", "020"), ("AO", "024"), ("AI", "660"), ("AQ", "010"), ("AG", "028"),
            ("AN", "530"), ("SA", "682"), ("AR", "032"), ("AM", "051"), ("AW", "533"),
            ("AU", "036"), ("AT", "040"), ("AZ", "031"), ("BS", "044"), ("BH", "048"),
            ("BD", "050"), ("BE", "056"), ("BZ", "084"), ("BJ", "204"), ("BM", "060"),
            ("BT", ""), ("BY", "064"), ("MM", "068"), ("BO", "070"), ("BA", "072"),
            ("BW", "074"), ("BR", "076"), ("BN", "096"), ("BG", "100"), ("BF", "854"),
            ("BI", "108"), ("KH", "116"), ("CM", "120"), ("CA", "124"), ("CV", "132"),
            ("CL", "152"), ("CN", "156"), ("CX", "162"), ("CY", "196"), ("CO", "170"),
            ("KM", "174"), ("CG", "178"), ("KP", "410"), ("KR", "408"), ("CR", "188"),
            ("CI", "384"), ("HR", "191"), ("CU", "192"), ("DK", "208"), ("DJ", "262"),
            ("DO", "214"), ("DM", "212"), ("EG", "818"), ("AE", "784"), ("EC", "218"),
            ("ER", "232"), ("ES", "724"), ("EE", "233"), ("US", "840"), ("ET", "231"),
            ("RU", "643"), ("FI", "246"), ("FR", "250"), ("FX", ""), ("GA", "266"),
            ("GM", "270"), ("GE", "268"), ("GS", "239"), ("GH", "288"), ("GI", "292"),
            ("UK", ""), ("GR", "300"), ("GD", "308"), ("GL", "304"), ("GP", "312"),
            ("GU", "316"), ("GT", "320"), ("GN", "324"), ("GW", "624"), ("GQ", "226"),
            ("GY", "328"), ("GF", "254"), ("HT", "332"), ("HN", "340"), ("HK", "344"),
            ("HU", "348"), ("SJ", ""), ("MU", "480"), ("NF", ""), ("BV", ""),
            ("KY", ""), ("CC", ""), ("CK", ""), ("FK", ""), ("FO", ""), ("FJ", ""),
            ("HM", ""), ("MP", ""), ("MH", ""), ("SB", ""), ("AS", ""), ("TC", ""),
            ("VG", "092"), ("VI", "850"), ("WF", ""), ("IN", "356"), ("ID", "360"),
            ("IQ", "368"), ("IE", "372"), ("IS", "352"), ("IL", "376"), ("IT", "380"),
            ("JM", "388"), ("JP", "392"), ("JO", "400"), ("KZ", "398"), ("KE", "404"),
            ("KG", "417"), ("KI", "296"), ("KW", "414"), ("BB", ""), ("LA", "418"),
            ("LS", "426"), ("LV", "428"), ("LB", "422"), ("LR", "430"), ("LY", "434"),
            ("LI", "438"), ("LT", "440"), ("LU", "442"), ("MO", "446"), ("MK", "807"),
            ("MG", "450"), ("MY", "458"), ("MW", "454"), ("MV", "462"), ("ML", "466"),
            ("MT", "470"), ("MA", "504"), ("MQ", "474"), ("MR", "478"), ("YT", "175"),
            ("MX", "484"), ("FM", "583"), ("MD", "498"), ("MC", "492"), ("MN", "496"),
            ("MS", "500"), ("MZ", "508"), ("NA", "516"), ("NR", "520"), ("NP", "524"),
            ("NI", "558"), ("NE", "562"), ("NG", "566"), ("NU", "570"), ("NO", "578"),
            ("NC", "540"), ("NZ", "554"), ("IO", "086"), ("OM", "512"), ("UG", "800"),
            ("UZ", "860"), ("PK", "586"), ("PW", "585"), ("PA", "591"), ("PG", "598"),
            ("PY", "600"), ("NL", "528"), ("PE", "604"), ("UM", "581"), ("PH", "608"),
            ("PN", "612"), ("PL", "616"), ("PF", "258"), ("PR", "630"), ("PT", "620"),
            ("QA", "634"), ("CF", ""), ("RE", "638"), ("RO", "642"), ("GB", "826"),
            ("RW", "646"), ("EH", "732"), ("KN", "659"), ("SH", "654"), ("LC", "662"),
            ("VC", "670"), ("SV", ""), ("WS", "882"), ("SM", ""), ("ST", "678"),
            ("SN", "686"), ("SC", "690"), ("SL", "694"), ("SG", "702"), ("SK", "703"),
            ("SI", "705"), ("SO", "706"), ("SD", "736"), ("LK", "144"), ("PM", ""),
            ("SE", "752"), ("CH", "756"), ("SR", "740"), ("SZ", "748"), ("SY", "760"),
            ("TJ", "762"), ("TW", "158"), ("TZ", "834"), ("TD", "148"), ("CS", ""),
            ("CZ", "203"), ("TF", "260"), ("TH", "764"), ("TP", "626"), ("TG", "768"),
            ("TK", "772"), ("TO", "776"), ("TT", ""), ("TN", "788"), ("TM", "795"),
            ("TR", "792"), ("TV", "798"), ("UA", "804"), ("SU", ""), ("UY", "858"),
            ("VU", "548"), ("VA", ""), ("VE", "862"), ("VN", "704"), ("YE", "887"),
            ("YU", ""), ("ZR", ""), ("ZM", "894"), ("ZW", "716")
        }
        self.teller = {
            '151', '152', '171', '172', 'SIGNATORY', 'USREGS.TP.LEGAL.ID', 'EM.DRAW.CHQ.NO', 'EM.DRAW.CHQ.AMT',
            'EM.DRAW.ACCT.NO', 'EM.DRAW.BANK', 'EM.DRAW.BRANCH', 'EM.DRAW.BRCH.CODE', 'EM.DRAW.CUST.NAME',
            'EM.CLEARED.BAL', 'EM.MEMBER.NAME', 'EM.ACCT.WORK.BAL', 'EM.PAY.TO', 'EM.AMT.ARREARS', 'EM.ACCT.NUM',
            'EM.SAVGS.AMOUNT', 'EM.REPAYMENT', 'EM.INT.REPAYMENT', 'EM.INTEREST.DUE', 'EM.CONS.DISCLOSE',
            'EM.SAVING.TMP.BAL', 'EM.LOAN.TMP.BAL', 'EM.INT.TMP.BAL', 'EM.ACCT.TYPE', 'L.REFERENCE', 'L.ORD.CUST',
            'L.ORD.CUST.CTRY', 'L.ORD.CUST.RES', 'L.BEN.NAME', 'L.BEN.ADD', 'L.BEN.RES', 'L.PAY.DETAILS', 'L.INI.CTRY',
            'L.ECO.CODE', 'L.CCY.REC', 'L.MODE.TXN', 'L.MAT.AGEN', 'L.NOM.PRES', 'L.NIF.PRES', 'L.NUM.STATS', 'L.TYP.IDEN',
            'L.NUM.IDEN', 'L.NUM.BEN', 'L.NOM.TIER', 'L.ORD.ADD', 'L.NAME.REC', 'L.ADDR', 'L.CIN', 'L.VERSION.NAME'
        }
        
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
    def create_reference_tables(self):
        conn = None
        try:
            conn = self.db.connect()
            
            
            # Table pour les champs teller
            conn.execute(text("DROP TABLE IF EXISTS esri_teller_fields"))
            create_teller_table = """
            CREATE TABLE esri_teller_fields (
                field_order INT PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                field_description VARCHAR(255)
            )
            """
            conn.execute(text(create_teller_table))
            
            # Table pour le mapping des colonnes
            conn.execute(text("DROP TABLE IF EXISTS esri_columns_mapping"))
            create_mapping_table = """
            CREATE TABLE esri_columns_mapping (
                output_column VARCHAR(100) PRIMARY KEY,
                teller_field VARCHAR(100) NOT NULL,
                description VARCHAR(255)
            )
            """
            conn.execute(text(create_mapping_table))
            
            # Table pour les pays et adresses
            conn.execute(text("DROP TABLE IF EXISTS esri_countries"))
            create_countries_table = """
            CREATE TABLE esri_countries (
                country_code VARCHAR(5) PRIMARY KEY,
                country_name VARCHAR(100) NOT NULL,
                numeric_code VARCHAR(10)
            )
            """
            conn.execute(text(create_countries_table))
            
            conn.commit()
            print("[INFO] Tables de référence créées ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_reference_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def populate_reference_tables(self):
        conn = None
        try:
            conn = self.db.connect()
            
            # Remplir la table teller_fields
            teller_data = []
            for i, field in enumerate(self.teller):
                teller_data.append(f"({i}, '{field}', 'Champ teller {field}')")
            
            insert_teller = f"""
            INSERT INTO esri_teller_fields (field_order, field_name, field_description) 
            VALUES {','.join(teller_data)}
            """
            conn.execute(text(insert_teller))
            
            # Remplir la table columns_mapping
            mapping_data = []
            
            
            for output_col, teller_field in self.columns_mapping.items():
                safe_output_col = output_col.replace("'", "''")
                safe_teller_field = teller_field.replace("'", "''")
                desc = f"Mapping {safe_output_col}".replace("'", "''")
                mapping_data.append(f"('{safe_output_col}', '{safe_teller_field}', '{desc}')")
            insert_mapping = f"""
            INSERT INTO esri_columns_mapping (output_column, teller_field, description) 
            VALUES {','.join(mapping_data)}
            """
            conn.execute(text(insert_mapping))
            
            # Remplir la table countries
            countries_data =[]
            for country_code, country_name in self.country_addresses.items():
                # Trouver le code numérique correspondant
                numeric_code = next((code for c, code in self.countries_codes if c == country_code), '')
                safe_country_name = country_name.replace("'", "''")

                countries_data.append(f"('{country_code}', '{safe_country_name}', '{numeric_code}')")
            
            insert_countries = f"""
            INSERT INTO esri_countries (country_code, country_name, numeric_code) 
            VALUES {','.join(countries_data)}
            """
            conn.execute(text(insert_countries))
            
            conn.commit()
            print("[INFO] Tables de référence remplies ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] populate_reference_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")
    
    def create_esri_functions(self):
        """Crée les fonctions MySQL qui utilisent les tables de référence"""
        conn = None
        try:
            conn = self.db.connect()
            
            self.create_reference_tables()
            self.populate_reference_tables()
            # Fonction pour extraire entre TELLER et MCBC (reste la même)
            create_extract_function = """
            CREATE FUNCTION extract_teller_mcbc(local_ref TEXT)
            RETURNS TEXT
            DETERMINISTIC
            BEGIN
                DECLARE result TEXT;
                SET result = REGEXP_SUBSTR(local_ref, 'TELLER,([^,]+)\\.MCBC');
                RETURN IFNULL(result, NULL);
            END
            """
            
            # Fonction améliorée qui utilise la table esri_teller_fields
            create_extract_field_function = """
            CREATE FUNCTION extract_field_value(local_ref TEXT, field_name VARCHAR(255))
            RETURNS TEXT
            DETERMINISTIC
            BEGIN
                DECLARE field_index INT;
                DECLARE field_value TEXT;
                
                -- Récupérer l'index depuis la table
                SELECT field_order INTO field_index 
                FROM esri_teller_fields 
                WHERE field_name = field_name
                 LIMIT 1; -- sécurité si doublon

                
                IF field_index IS NOT NULL AND field_index >= 0 THEN
                    SET field_value = SUBSTRING_INDEX(SUBSTRING_INDEX(local_ref, '|', field_index + 1), '|', -1);
                    RETURN NULLIF(field_value, '');
                END IF;
                
                RETURN NULL;
            END
            """
            
            # Fonction pour obtenir l'adresse du pays depuis la table
            create_country_address_function = """
            CREATE FUNCTION get_country_address(in_country_code TEXT)
                RETURNS TEXT
                DETERMINISTIC
                BEGIN
                    DECLARE country_name TEXT;

                    SELECT country_name INTO country_name
                    FROM esri_countries
                    WHERE country_code = in_country_code
                    LIMIT 1;

                    RETURN IFNULL(country_name, 'Adresse inconnue');
                END
            """
            
            # Fonction pour convertir le code pays depuis la table
            create_country_code_function = """
            CREATE FUNCTION convert_country_code(in_country_code TEXT)
                RETURNS TEXT
                DETERMINISTIC
                BEGIN
                    DECLARE numeric_code TEXT;

                    SELECT numeric_code INTO numeric_code
                    FROM esri_countries
                    WHERE country_code = in_country_code
                    LIMIT 1;

                    RETURN numeric_code;
                END

            """
            
            # Fonction pour récupérer dynamiquement les mappings
            create_get_mapping_function = """
            CREATE FUNCTION get_field_mapping(output_column VARCHAR(100))
            RETURNS VARCHAR(100)
            DETERMINISTIC
            BEGIN
                DECLARE teller_field VARCHAR(100);
                
                SELECT teller_field INTO teller_field
                FROM esri_columns_mapping 
                WHERE output_column = esri_columns_mapping.output_column;
                
                RETURN teller_field;
            END
            """
            
            # Supprimer et recréer les fonctions
            functions_to_drop = [
                'extract_teller_mcbc', 
                'extract_field_value', 
                'get_country_address', 
                'convert_country_code',
                'get_field_mapping'
            ]
            
            for func in functions_to_drop:
                conn.execute(text(f"DROP FUNCTION IF EXISTS {func}"))
            
            # Créer les fonctions
            conn.execute(text(create_extract_function))
            conn.execute(text(create_extract_field_function))
            conn.execute(text(create_country_address_function))
            conn.execute(text(create_country_code_function))
            conn.execute(text(create_get_mapping_function))
            
            conn.commit()
            print("[INFO] Fonctions ESRI avec tables créées ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_esri_functions_with_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def create_esri_report_table(self, date_debut: str, date_fin: str):
        """Crée la table de rapport ESRI directement en SQL"""
        conn = None
        try:
            conn = self.db.connect()
            
            # Supprimer la table si elle existe
            conn.execute(text("DROP TABLE IF EXISTS report_esri"))
            
            # Créer la table de rapport avec toutes les transformations
            create_table_query = """
            CREATE TABLE report_esri AS
            SELECT 
                co_code AS Agence,
                'EUR' AS Devise,
                'SIPEM' AS Banque,
                '0' AS Donneur_resident,
                DATE_FORMAT(value_date_1, '%Y/%m/%d') AS Date,
                amount_local_1 AS Montant,
                
                -- Extraction des champs
                extract_teller_mcbc(local_ref) AS Type,
                extract_field_value(local_ref, 'L.REFERENCE') AS Reference,
                extract_field_value(local_ref, 'L.ORD.CUST') AS Donneur_ordre,
                extract_field_value(local_ref, 'L.ORD.CUST.CTRY') AS Code_pays_donneur_ordre,
                extract_field_value(local_ref, 'L.BEN.NAME') AS Beneficiaire,
                extract_field_value(local_ref, 'L.BEN.RES') AS Beneficiaire_resident,
                extract_field_value(local_ref, 'L.BEN.ADD') AS Adresse_Beneficiaire,
                extract_field_value(local_ref, 'L.PAY.DETAILS') AS Nature,
                extract_field_value(local_ref, 'L.ECO.CODE') AS Code_economique,
                extract_field_value(local_ref, 'L.MODE.TXN') AS Sens,
                
                -- Transformations
                get_country_address(extract_field_value(local_ref, 'L.ORD.CUST.CTRY')) AS Adresse_donneur_ordre,
                convert_country_code(extract_field_value(local_ref, 'L.ORD.CUST.CTRY')) AS Code_pays
                
            FROM teller_mcbc_his_full
            WHERE transaction_code IN (40, 53)
            AND value_date_1 BETWEEN :date_debut AND :date_fin
            """
            
            conn.execute(text(create_table_query), {
                "date_debut": date_debut, 
                "date_fin": date_fin
            })
            
            conn.commit()
            print("[INFO] Table de rapport ESRI créée avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_esri_report_table : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def get_esri_report_data(self):
        """Récupère les données de la table de rapport"""
        conn = None
        try:
            conn = self.db.connect()
            
            # Vérifier si la table existe et contient des données
            check_query = "SELECT COUNT(*) as count FROM report_esri"
            result = conn.execute(text(check_query))
            count = result.fetchone()[0]
            
            if count == 0:
                print("[INFO] Aucune donnée trouvée dans le rapport ESRI")
                return [], []
            
            # Récupérer les données avec l'ordre désiré
            select_query = """
            SELECT 
                Agence, Type, Reference, Banque, Donneur_ordre, Donneur_resident,
                Adresse_donneur_ordre, Beneficiaire, Beneficiaire_resident, 
                Adresse_Beneficiaire, Montant, Nature, Code_economique, Devise, 
                Code_pays, Sens, Date
            FROM report_esri
            """
            
            result = conn.execute(text(select_query))
            data = [dict(row._mapping) for row in result]
            
            # Récupérer les colonnes
            columns_query = "SHOW COLUMNS FROM report_esri"
            columns_result = conn.execute(text(columns_query))
            columns = [row[0] for row in columns_result]
            
            # Ordre désiré des colonnes
            desired_order = [
                'Agence', 'Type', 'Reference', 'Banque', 'Donneur_ordre', 'Donneur_resident', 
                'Adresse_donneur_ordre', 'Beneficiaire', 'Beneficiaire_resident', 'Adresse_Beneficiaire',
                'Montant', 'Nature', 'Code_economique', 'Devise', 'Code_pays', 'Sens', 'Date'
            ]
            
            final_columns = [col for col in desired_order if col in columns]
            
            print(f"[INFO] Données ESRI récupérées avec succès ({len(data)} lignes) ✅")
            return data, final_columns
            
        except Exception as e:
            print(f"[ERREUR] get_esri_report_data : {e}")
            return [], []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def process_esri_data_optimized(self, date_debut: str, date_fin: str):
        """Traite les données ESRI de manière optimisée sans pandas"""
        try:
            # Créer les fonctions MySQL
            if not self.create_esri_functions():
                return [], []
            
            # Créer la table de rapport
            if not self.create_esri_report_table(date_debut, date_fin):
                return [], []
            
            # Récupérer les données
            data, columns = self.get_esri_report_data()
            
            return data, columns
            
        except Exception as e:
            print(f"[ERREUR] process_esri_data_optimized : {e}")
            import traceback 
            print(f"[DEBUG] {traceback.format_exc()}")
            return [], []

    def cleanup_esri_tables(self):
        """Nettoie les tables et fonctions ESRI"""
        conn = None
        try:
            conn = self.db.connect()
            
            # Supprimer la table de rapport
            conn.execute(text("DROP TABLE IF EXISTS report_esri"))
            
            # Supprimer les fonctions
            functions_to_drop = [
                'extract_teller_mcbc', 
                'extract_field_value', 
                'get_country_address', 
                'convert_country_code'
            ]
            
            for func in functions_to_drop:
                conn.execute(text(f"DROP FUNCTION IF EXISTS {func}"))
            
            conn.commit()
            print("[INFO] Nettoyage ESRI terminé ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] cleanup_esri_tables : {e}")
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")