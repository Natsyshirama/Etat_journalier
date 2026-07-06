-- Structure de la table Power Card
-- Cette table stocke toutes les transactions enregistrées depuis Power Card

CREATE TABLE IF NOT EXISTS transact_power_card (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Données transactionnelles
    external_stan VARCHAR(50),
    reference VARCHAR(100),
    source VARCHAR(100),
    destination VARCHAR(100),
    message VARCHAR(255),
    processing_code VARCHAR(50),
    action VARCHAR(50),
    
    -- Informations du client/compte
    pan VARCHAR(100),
    source_account_number VARCHAR(100),
    
    -- Temps et dates
    local_time DATETIME,
    internal_time DATETIME,
    
    -- Détails de la transaction
    transaction_amount VARCHAR(50),
    terminal_no VARCHAR(50),
    acceptor_point VARCHAR(50),
    authorization_reference VARCHAR(100),
    current_table_indicator VARCHAR(50),
    
    -- Métadonnées de l'import
    import_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index pour les recherches fréquentes
    INDEX idx_import_date (import_date),
    INDEX idx_reference (reference),
    INDEX idx_pan (pan),
    INDEX idx_local_time (local_time),
    INDEX idx_action (action),
    INDEX idx_source_account_number (source_account_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
