def create_table_dav(self, name: str):
    conn = None
    try:
        table_name = f"dav_{name}"
        
        query = f"""
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
                solde_account(
                    contract_balance.type_sysdate, 
                    contract_balance.open_balance, 
                    contract_balance.credit_mvmt, 
                    contract_balance.debit_mvmt,
                    {name} 
                ) AS solde,
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
                ON customer.id = arrangement.customer
            LEFT JOIN
                eb_cont_bal_mcbc_live_full AS contract_balance
                ON contract_balance.id = arrangement.linked_appl_id
            LEFT JOIN account_mcbc_live_full AS account
                ON account.id = arrangement.linked_appl_id
            WHERE
                arrangement.product_line='ACCOUNTS'
                AND arrangement.arr_status IN ('AUTH', 'CURRENT','PENDING.CLOSURE')
                AND arrangement.product_group ='DV.SP.MG' LIMIT 100;
        """
        
        conn = self.db.connect()
        
        # Supprimer la table si elle existe
        drop_query = f"DROP TABLE IF EXISTS {table_name}"
        conn.execute(text(drop_query))
        conn.commit()
        
        # Récupérer les données
        df = pd.read_sql(query, conn)

        # Nettoyer les noms en double
        def remove_duplicate_name(name):
            if pd.isnull(name):
                return name
            words = name.strip().split()
            half = len(words) // 2
            if len(words) % 2 == 0 and words[:half] == words[half:]:
                return ' '.join(words[:half])
            return name

        df.loc[df['categorie'] != 'Particulier', 'Nom_compte'] = (
            df.loc[df['categorie'] != 'Particulier', 'Nom_compte']
            .apply(remove_duplicate_name)
        )
        
        # Traitement des soldes
        df['solde'] = pd.to_numeric(df['solde'], errors='coerce')
        df['Credit'] = df['solde'].where(df['solde'] > 0, 0)
        df['Debit'] = df['solde'].where(df['solde'] < 0, 0).abs()
        
        # Créer la table dans la base de données
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists='replace',  # Remplace la table si elle existe
            index=False,           # Ne pas inclure l'index du DataFrame
            method='multi',        # Plus efficace pour l'insertion
            chunksize=1000         # Insérer par lots de 1000 lignes
        )
        
        print(f"[INFO] Table {table_name} créée avec succès avec {len(df)} lignes ✅")
        return True

    except Exception as e:
        print(f"[ERREUR] Création de la table {table_name} : {e}")
        return False
        
    finally:
        if conn:
            try:
                conn.close()
            except Exception as close_err:
                print(f"[ERREUR] Fermeture connexion (create_table_dav) : {close_err}")