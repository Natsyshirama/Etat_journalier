# Cahier de Charges – Réconciliation PowerCard / T24

## 1. Présentation du projet

Développement d'une solution de réconciliation et de rapprochement des données provenant de deux sources :
- **PowerCard** : Données des transactions par cartes de paiement
- **T24** : Données des transactions bancaires (Temenos T24)

L'objectif est d'identifier et d'analyser les divergences entre ces deux sources de données afin d'assurer l'intégrité des transactions bancaires.

---

## 2. Objectif principal

- **Réconcilier** les données PowerCard avec celles de T24
- **Identifier** les écarts et divergences entre les deux systèmes
- **Analyser** les raisons des non-concordances
- **Faciliter** la résolution des différences détectées
- **Assurer** la conformité des transactions bancaires

---

## 3. Fonctionnalités

### 3.1 Authentification
- Connexion sécurisée par nom d'utilisateur + mot de passe (JWT ou session)
- Gestion des rôles :
  - **Administrateur** : Accès complet (import, modification, suppression)
  - **Expert Métier** : Consultation et export uniquement
- Validation et gestion des utilisateurs (activation/blocage)

### 3.2 Importation des données (Admin) - J-1

#### 3.2.1 Import PowerCard
- Téléchargement de fichiers CSV au format : `powercard_YYYYMMDD.csv`
- Colonnes attendues :
  - External stan, Reference, Source, Destination, Message
  - Processing code, Action, PAN
  - Local time, Internal time, Transaction amount
  - Terminal no., Acceptor point, Authorization reference
  - Current table indicator, Source account number
- Validation et détection des doublons
- Enregistrement en base de données

#### 3.2.2 Import T24
- Téléchargement de fichiers CSV au format : `t24_YYYYMMDD.csv`
- Colonnes attendues :
  - Num Compte, Credit Amount, Processing Date
  - L.AT.PAN.NO, L.AT.RRN
  - Compte DB Cions, Saisi le
- Validation des données et contrôle de qualité
- Enregistrement en base de données

### 3.3 Réconciliation et comparaison

#### 3.3.1 Appariement des transactions
- Appariement automatique par :
  - PAN (numéro de carte)
  - Montant (amount)
  - Date de transaction (traitement)
  - Référence de transaction
- Détection des correspondances partielles
- Identification des transactions orphelines

#### 3.3.2 Analyse des différences
- **Transactions en excès PowerCard** : Présentes dans PowerCard mais absentes de T24
- **Transactions en excès T24** : Présentes dans T24 mais absentes de PowerCard
- **Divergences de montants** : Même transaction mais montants différents
- **Divergences de dates** : Écarts de traitement ou de saisie
- **Divergences d'état** : Action/Status différents entre les deux systèmes

### 3.4 Consultation et analyse des différences

#### 3.4.1 Mode de consultation
- **Mode unique** : Consultation des différences pour une date spécifique (J-1)
- **Mode plage** : Consultation sur une période (date début - date fin)

#### 3.4.2 Affichage des résultats
- Tableau récapitulatif des différences détectées
- Pour chaque différence :
  - Date de traitement (processing_date)
  - Type de différence (excès PowerCard, excès T24, divergence, etc.)
  - Détails PowerCard :
    - PAN, Référence, Action
    - Montant, Date/Heure locale
  - Détails T24 :
    - Nombre de correspondances trouvées
    - Affichage détaillé de chaque match T24
  - Statut de réconciliation

#### 3.4.3 Détails des transactions
- Consultation des détails complets d'une transaction PowerCard
- Consultation des détails complets d'une transaction T24
- Affichage des correspondances multiples (cas où plusieurs T24 matchen un PowerCard)

### 3.5 Assignation des dates de traitement (T24 → PowerCard)

#### 3.5.1 Processus automatique
- Récupération de `saisie_le` depuis T24
- Recherche des transactions PowerCard dans une plage horaire (début/fin)
- Assignation de la `processing_date` aux transactions PowerCard correspondantes
- Cas de gestion :
  - **Correspondance exacte** : 1 T24 → 1 PowerCard
  - **Correspondance automatique** : Assignation par plage de dates

#### 3.5.2 Résultats et statistiques
- Nombre de lignes traitées par période
- Nombre de mises à jour exactes
- Nombre de mises à jour automatiques
- Détection des périodes sans données

### 3.6 Statistiques et rapports

#### 3.6.1 Tableaux de bord
- **Statistiques PowerCard** :
  - Total transactions par date
  - Distribution par action (WITHDRAWAL, Authentication, etc.)
  - Montants totaux par action
  - Taux d'approbation/rejet
  
- **Statistiques de réconciliation** :
  - Nombre de différences détectées
  - Taux d'appariement (% de transactions appairées)
  - Évolution du taux de réconciliation (journalière/mensuelle)

#### 3.6.2 Graphiques
- Évolution journalière du nombre de transactions
- Distribution des types de différences
- Évolution du taux de réconciliation dans le temps
- Montants par action/type

### 3.7 Gestion des fichiers (Admin)

#### 3.7.1 Export de données
- Export en format Excel
- Filtrage par :
  - Date unique ou période
  - Activité (PowerCard, T24, Réconciliation)
  - Type de différence
  - Date/Plage de dates
- Génération de rapports de réconciliation

#### 3.7.2 Téléchargement
- Historique des fichiers importés
- Téléchargement des fichiers source
- Historique des réconciliations effectuées

### 3.8 Suivi des transactions

#### 3.8.1 Consultation des transactions PowerCard
- Filtrage par date ou plage de dates
- Filtrage par processing code
- Filtrage par action (Approved, Rejected, etc.)
- Affichage des détails complets
- Affichage du dernier `local_time` enregistré

#### 3.8.2 Consultation des transactions T24
- Filtrage par date ou plage de dates
- Affichage des détails complets
- Affichage du dernier `saisie_le` enregistré

---

## 4. Contraintes techniques

### 4.1 Environnement
- Fonctionnement exclusivement en **intranet**
- Serveur Windows ou Linux selon l'infrastructure existante
- Réseau local de l'entreprise uniquement

### 4.2 Technologies

| Composant | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python 3.9+) |
| **Frontend** | Vue.js 3 + Vuetify 3 |
| **Base de données** | MySQL 8.0+ |
| **Authentification** | JWT (JSON Web Tokens) |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic |
| **API** | RESTful |
| **Build tool** | Vite |
| **Reverse Proxy** | Nginx (optionnel) |

### 4.3 Structure de base de données

#### Table : `powercard`
```sql
id, external_stan, reference, source, destination, message,
processing_code, action, pan, local_time, internal_time,
transaction_amount, terminal_no, acceptor_point,
authorization_reference, current_table_indicator,
source_account_number, import_date, processing_date,
created_at, updated_at
```

#### Table : `t24_transactions`
```sql
id, account_number, credit_amount, processing_date, pan, rrn,
compte_db_cions, saisie_le, import_date, created_at, updated_at
```

#### Table : `reconciliation_diffs`
```sql
id, processing_date, type (excess_powercard|excess_t24|divergence),
powercard_id, t24_ids (JSON array), divergence_details (JSON),
status, created_at, resolved_at, resolved_by
```

### 4.4 Sécurité

- **Authentification** : JWT avec expiration configurable
- **Autorisation** : Contrôle d'accès basé sur les rôles (RBAC)
- **Mots de passe** : Hachage avec bcrypt ou Argon2
- **Chiffrement** : HTTPS/SSL en intranet
- **Audit** : Logging de toutes les actions critiques
- **Validation** : Validation stricte des données en entrée
- **Injection SQL** : Protection via ORM et requêtes paramétrées
- **Sessions** : Expiration automatique des sessions inactives

---

## 5. Livrables

### 5.1 Code source
- ✅ Backend complet (FastAPI)
- ✅ Frontend complet (Vue.js 3 + Vuetify)
- ✅ Scripts de migration de base de données
- ✅ Configuration environnement (`.env` template)

### 5.2 Base de données
- ✅ Schéma SQL documenté
- ✅ Scripts de création des tables
- ✅ Scripts de migration de données
- ✅ Index optimisés pour les requêtes de réconciliation

### 5.3 Documentation
- ✅ Manuel utilisateur (Admin + Expert Métier)
- ✅ Manuel d'installation et configuration
- ✅ Documentation API (Swagger/OpenAPI)
- ✅ Guide de dépannage

### 5.4 Tests
- ✅ Tests unitaires (backend)
- ✅ Tests d'intégration API
- ✅ Tests fonctionnels (frontend)
- ✅ Plan de recette utilisateur

---

## 6. Métriques de succès

| Métrique | Objectif |
|----------|----------|
| **Taux d'appariement** | ≥ 95% des transactions appairées |
| **Temps de réconciliation** | < 5 minutes pour une journée de données |
| **Disponibilité** | 99% en heures de bureau |
| **Performance** | Chargement tableau < 2 secondes |
| **Couverture tests** | ≥ 80% |

---

## 7. Calendrier de développement (Estimé)

| Phase | Durée | Tâches |
|-------|-------|--------|
| **Phase 1 : Setup** | 1 semaine | Architecture, config, DB |
| **Phase 2 : Backend** | 2-3 semaines | API, réconciliation, import |
| **Phase 3 : Frontend** | 2-3 semaines | UI, composants, intégration |
| **Phase 4 : Tests** | 1-2 semaines | Tests, QA, corrections |
| **Phase 5 : Déploiement** | 1 semaine | Déploiement, formation |

---

## 8. Risques et mitigation

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Volume de données élevé | Performance dégradée | Pagination, indexation, cache |
| Incohérence données | Mauvaise réconciliation | Validation stricte, audit log |
| Indisponibilité réseau | Service inaccessible | Architecture résiliente, monitoring |
| Erreur utilisateur | Données corrompues | Validations, confirmations |

---

## 9. Maintenance et support

- **Support Tier 1** : Expert Métier (simple consultation)
- **Support Tier 2** : Admin (import, résolution des différences)
- **Support Tier 3** : Développeur (bugs, améliorations)
- **Hotline** : Support en heures de bureau
- **SLA** : Réponse critique < 2h, Résolution < 1 jour ouvrable

---

## 10. Évolutions futures (Phase 2)

- Automatisation complète de la résolution des différences
- Alertes en temps réel pour divergences critiques
- Module de rapprochement multi-devises
- Intégration avec d'autres systèmes de paiement
- Portail client pour consultation autonome
- Webhooks/API pour intégrations tierces

---

**Approbation :**

| Rôle | Nom | Signature | Date |
|------|-----|-----------|------|
| Product Owner | | | |
| Responsable IT | | | |
| Responsable Métier | | | |

---

*Dernière mise à jour : 2026-08-17*
