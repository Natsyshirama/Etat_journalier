# Fonctionnalité Power Card - Documentation Complète

## 📋 Vue d'ensemble

Cette fonctionnalité permet d'importer les transactions Power Card depuis des fichiers CSV et de les stocker dans la base de données pour analyse et réconciliation avec Temenos T24.

## 🗄️ Structure de la Base de Données

### Table: `transact_power_card`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INT | Clé primaire auto-incrémentée |
| external_stan | VARCHAR(50) | Identifiant externe de la transaction |
| reference | VARCHAR(100) | Référence unique de la transaction |
| source | VARCHAR(100) | Source de la transaction (ATM, etc.) |
| destination | VARCHAR(100) | Destination (HOST, etc.) |
| message | VARCHAR(255) | Type de message |
| processing_code | VARCHAR(50) | Code de traitement |
| action | VARCHAR(50) | Statut (Approved, Rejected, etc.) |
| pan | VARCHAR(100) | Numéro de carte (partiellement masqué) |
| source_account_number | VARCHAR(100) | Numéro de compte source |
| local_time | DATETIME | Heure locale de la transaction |
| internal_time | DATETIME | Heure interne du système |
| transaction_amount | VARCHAR(50) | Montant de la transaction |
| terminal_no | VARCHAR(50) | Numéro du terminal |
| acceptor_point | VARCHAR(50) | Point d'acceptation |
| authorization_reference | VARCHAR(100) | Référence d'autorisation |
| current_table_indicator | VARCHAR(50) | Indicateur de table |
| import_date | DATE | Date d'import (filtreur principal) |
| created_at | TIMESTAMP | Timestamp de création |

**Index:**
- import_date
- reference
- pan
- local_time
- action
- source_account_number

---

## 🛠️ Backend

### 1. Controller: `PowerCardController.py`

**Localisation:** `back_end/controller/PowerCardController.py`

**Méthodes principales:**

```python
class PowerCardController:
    def __init__(self):
        # Initialise la connexion BD et le pattern de fichier
        # Pattern: powercard_YYYYMMDD.csv
    
    def init_table(self):
        # Crée la table transact_power_card si elle n'existe pas
    
    def validate_filename(filename: str) -> str:
        # Valide le format du nom de fichier
        # Format: powercard_YYYYMMDD.csv
        # Retourne: date_str (YYYYMMDD)
    
    def read_csv_file(file: UploadFile) -> DataFrame:
        # Lit et parse le fichier CSV
    
    def clean_dataframe(df: DataFrame) -> DataFrame:
        # Nettoie les colonnes et données
        # - Normalise les noms de colonnes
        # - Remplace NaN par None
        # - Trim les espaces
    
    def insert_data(conn, df: DataFrame, import_date: str) -> tuple:
        # Insère les données dans la table
        # Retourne: (rows_inserted, errors_list)
    
    def process_file(file: UploadFile, import_date: str) -> dict:
        # Orchestration complète d'un import
        # Valide -> Lit -> Nettoie -> Insère
    
    def get_power_card_stats(import_date: str = None) -> dict:
        # Retourne les statistiques:
        # - Total transactions
        # - Nombre approuvées/rejetées
        # - Montant total
    
    def get_transactions_by_date(import_date: str, limit: int, offset: int) -> list:
        # Récupère les transactions paginées
```

### 2. API Routes: `apiPowerCard.py`

**Localisation:** `back_end/api/apiPowerCard.py`

**Endpoints:**

#### POST `/api/powercard/import`
Importe un fichier Power Card
- **Paramètres:**
  - `file` (FormData): Fichier CSV
  - `import_date` (Query): Date au format YYYY-MM-DD
- **Réponse:**
  ```json
  {
    "status": "success|error",
    "data": {
      "filename": "powercard_20260705.csv",
      "success": true,
      "messages": ["Import réussi..."],
      "rows_inserted": 150,
      "error_count": 0
    }
  }
  ```

#### GET `/api/powercard/stats`
Récupère les statistiques
- **Paramètres:**
  - `import_date` (Query, optional): Date au format YYYY-MM-DD
- **Réponse (une date):**
  ```json
  {
    "status": "success",
    "data": {
      "import_date": "2026-07-05",
      "total_transactions": 150,
      "transaction_days": 1,
      "total_amount": 15600000.50,
      "approved_count": 145,
      "rejected_count": 5
    }
  }
  ```
- **Réponse (toutes les dates):**
  ```json
  {
    "status": "success",
    "data": [
      {
        "import_date": "2026-07-05",
        "total_transactions": 150,
        "approved_count": 145,
        "rejected_count": 5
      }
    ]
  }
  ```

#### GET `/api/powercard/transactions`
Récupère les transactions paginées
- **Paramètres:**
  - `import_date` (Query): Date au format YYYY-MM-DD (required)
  - `limit` (Query): Nombre de résultats (default: 100, max: 1000)
  - `offset` (Query): Pagination offset (default: 0)
- **Réponse:**
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": 1,
        "reference": "6,18605E+11",
        "pan": "507656XXXXXX5902",
        "local_time": "2026-07-05 06:15:00",
        "transaction_amount": "20,000.00 MGA",
        "action": "Approved",
        ...
      }
    ],
    "count": 100
  }
  ```

### 3. Configuration: `app.py`

Ajoutez les imports et enregistrement:
```python
from api.apiPowerCard import api_router_powercard

app.include_router(api_router_powercard, prefix="/api")
```

---

## 🎨 Frontend

### 1. Composable: `usePowerCardImport.js`

**Localisation:** `src/composables/usePowerCardImport.js`

**Fonctions:**
```javascript
export function usePowerCardImport() {
  // État réactif
  const file              // Fichier sélectionné
  const importDate        // Date d'import (YYYY-MM-DD)
  const loading           // État du chargement
  const uploadProgress    // Progression (0-100)
  const message           // Message utilisateur
  const messageType       // 'success', 'error', 'info'
  const importStats       // Stats du dernier import

  // Méthodes
  setApiUrl(apiUrl)                          // Configure l'URL API
  selectFile(file)                           // Sélectionne et valide le fichier
  setImportDate(date)                        // Configure la date
  uploadFile()                               // Lance l'upload
  fetchStats(date?)                          // Récupère les stats
  fetchTransactions(date, limit, offset)    // Récupère les transactions
  clearMessage()                             // Efface le message
}
```

### 2. Composants

#### `PowerCardUpload.vue`
**Localisation:** `src/components/powercard/PowerCardUpload.vue`

Formulaire d'upload avec:
- Sélecteur de date
- Input fichier CSV
- Validation du format de nom
- Affichage de la progression
- Résumé des résultats

#### `PowerCardStats.vue`
**Localisation:** `src/components/powercard/PowerCardStats.vue`

Affiche les statistiques:
- Cartes avec métriques principales (si date spécifiée)
- Tableau de toutes les dates avec tendances
- Filtrage par date
- Bouton pour voir les détails

#### `PowerCardTransactions.vue`
**Localisation:** `src/components/powercard/PowerCardTransactions.vue`

Tableau des transactions avec:
- Filtrage par date
- Affichage des colonnes principales
- Indicateur de statut (Approved/Rejected)
- Expansion de ligne pour détails

### 3. Page: `powercard.vue`

**Localisation:** `src/pages/app/powercard.vue`

Page principale avec 3 onglets:
1. **Import Power Card** - Upload et import des fichiers
2. **Statistiques** - Vue d'ensemble et tendances
3. **Transactions** - Liste détaillée avec recherche

---

## 📝 Utilisation

### Import d'un fichier Power Card

1. Accéder à la page: `/app/powercard`
2. Cliquer sur l'onglet "Import Power Card"
3. Sélectionner la date d'import (YYYY-MM-DD)
4. Sélectionner le fichier CSV (format: `powercard_YYYYMMDD.csv`)
5. Cliquer sur "Importer"
6. Attendre la confirmation

### Format du fichier CSV

Le fichier doit avoir les colonnes suivantes (dans n'importe quel ordre):
- External stan
- Reference
- Source
- Destination
- Message
- Processing code
- Action
- PAN
- Local time
- Internal time
- Transaction amount
- Terminal no.
- Acceptor point
- Authorization reference
- Current table indicator
- Source account number

**Exemple:** `powercard_20260705.csv`

### Consulter les statistiques

1. Cliquer sur l'onglet "Statistiques"
2. Sélectionner une date spécifique ou laisser vide pour toutes
3. Cliquer "Actualiser"

### Consulter les transactions

1. Cliquer sur l'onglet "Transactions"
2. Sélectionner une date
3. Cliquer "Charger"
4. Utiliser les filtres de pagination

---

## 🔄 Intégration avec la Navigation

Pour ajouter le lien dans le menu de navigation, modifiez `navigation_drawer.vue`:

```vue
<v-list-item
  title="Power Card"
  to="/app/powercard"
  prepend-icon="mdi-database-import"
/>
```

---

## 📊 Exemple de flux de données

```
Fichier CSV (powercard_20260705.csv)
    ↓
PowerCardUpload.vue (sélection date + fichier)
    ↓
API POST /api/powercard/import
    ↓
PowerCardController.process_file()
    - validate_filename()
    - read_csv_file()
    - clean_dataframe()
    - insert_data() → Table transact_power_card
    ↓
Retour JSON avec stats
    ↓
Affichage du résumé d'import
```

---

## 🔒 Sécurité

- ✅ Authentification requise (Bearer token)
- ✅ Validation du format du fichier
- ✅ Validation du format du nom
- ✅ Nettoyage des données (SQL injection)
- ✅ Gestion des erreurs robuste
- ✅ Logs détaillés

---

## 🐛 Dépannage

### "Format de nom invalide"
- Vérifiez que le fichier s'appelle `powercard_YYYYMMDD.csv`
- Exemple: `powercard_20260705.csv`

### "Format de date invalide"
- Utilisez le format YYYY-MM-DD
- Exemple: 2026-07-05

### "Erreur lors de l'insertion"
- Vérifiez que les colonnes CSV correspondent
- Vérifiez l'encodage (UTF-8)
- Vérifiez les permissions de la base de données

### Pas de données affichées
- Vérifiez que la date d'import existe
- Vérifiez le token d'authentification
- Vérifiez les logs du serveur

---

## 📈 Prochaines étapes

Pour la réconciliation Power Card ↔ Temenos:
1. Créer une table `temenos_transactions`
2. Créer un endpoint pour importer les données Temenos
3. Créer un service de réconciliation/comparaison
4. Créer une page "Écarts de réconciliation"
5. Implémenter les alertes pour les transactions non appairées

