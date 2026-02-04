from typing import List, Optional
from sqlalchemy import text
from datetime import datetime
from db.db import DB

class AgenceController:
    def __init__(self):
        self.db = DB()
        
        conn = self.db.connect()
        try:
            # Créer la table zone d'abord
            zone_query = text("""
                CREATE TABLE IF NOT EXISTS zone (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute(zone_query)
            
            # Insérer les zones par défaut si elles n'existent pas
            zones_data = [
                ("NORD",),
                ("SUD",),
                ("EST",),
                ("TANA CENTRE",),
                ("TANA AVARADRANO",),
                ("TANA ATSIMONDRANO",)
            ]
            
            insert_zone_query = text("""
                INSERT IGNORE INTO zone (nom) 
                VALUES (:nom)
            """)
            
            # Dictionnaire pour mapper les noms de zones aux IDs
            zone_mapping = {}
            
            for nom, in zones_data:
                try:
                    result = conn.execute(insert_zone_query, {"nom": nom})
                    if result.rowcount == 1:
                        # Récupérer l'ID de la zone insérée
                        get_id_query = text("SELECT id FROM zone WHERE nom = :nom")
                        id_result = conn.execute(get_id_query, {"nom": nom})
                        zone_row = id_result.fetchone()
                        if zone_row:
                            zone_mapping[nom] = zone_row[0]
                            print(f"[INFO] Zone '{nom}' créée avec ID: {zone_mapping[nom]}")
                    else:
                        # La zone existe déjà, récupérer son ID
                        get_id_query = text("SELECT id FROM zone WHERE nom = :nom")
                        id_result = conn.execute(get_id_query, {"nom": nom})
                        zone_row = id_result.fetchone()
                        if zone_row:
                            zone_mapping[nom] = zone_row[0]
                            print(f"[INFO] Zone '{nom}' existe avec ID: {zone_mapping[nom]}")
                except Exception as e:
                    print(f"[ERREUR] Zone {nom}: {e}")
            
            print(f"[INFO] Mapping des zones: {zone_mapping}")
            
            # Modifier la table agence pour ajouter id_zone
            agence_query = text("""
                CREATE TABLE IF NOT EXISTS agence (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    souscode VARCHAR(10) UNIQUE NOT NULL,
                    nom VARCHAR(100) NOT NULL,
                    id_zone INT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_code (code),
                    INDEX idx_souscode (souscode),
                    INDEX idx_zone (id_zone),
                    FOREIGN KEY (id_zone) REFERENCES zone(id) ON DELETE SET NULL
                )
            """)
            
            conn.execute(agence_query)
            conn.commit()
            print("[INFO] Tables 'zone' et 'agence' créées ou déjà existantes")
            
            # Insérer les agences avec zones (utiliser les noms des zones au lieu des IDs)
            # On va mapper les anciennes zones aux nouvelles
            agences_with_zone_names = [
                ("MG0010002", "A02", "Analamahintsy", "TANA CENTRE"),
                ("MG0010003", "A03", "Andravoahangy", "TANA CENTRE"),
                ("MG0010004", "A04", "Imerinafovoany", "TANA CENTRE"),
                ("MG0010005", "A05", "Andoharanofotsy", "TANA CENTRE"),
                ("MG0010006", "A06", "Anosizato", "TANA AVARADRANO"),
                ("MG0010007", "A07", "Ankadidramamy", "TANA AVARADRANO"),
                ("MG0010008", "A08", "Itaosy", "TANA AVARADRANO"),
                ("MG0010009", "A09", "Ankorondrano", "TANA CENTRE"),
                ("MG0010010", "A10", "Tsaralalana", "TANA CENTRE"),
                ("MG0010011", "A11", "Antsirabe", "SUD"),
                ("MG0010012", "A12", "By Pass", "TANA ATSIMONDRANO"),
                ("MG0010013", "A13", "Ilafy", "TANA ATSIMONDRANO"),
                ("MG0010021", "A21", "Antsiranana", "NORD"),
                ("MG0010022", "A22", "Nosy Be", "NORD"),
                ("MG0010023", "A23", "Sambava", "NORD"),
                ("MG0010024", "A24", "Ambanja", "NORD"),
                ("MG0010025", "A25", "Antalaha", "NORD"),
                ("MG0010031", "A31", "Fianarantsoa", "SUD"),
                ("MG0010041", "A41", "Mahajanga", "EST"),
                ("MG0010051", "A51", "Moramanga", "EST"),
                ("MG0010052", "A52", "Ambatondrazaka", "EST"),
                ("MG0010053", "A53", "TANAMBAO", "SUD"),
                ("MG0010054", "A54", "Ankirihiry", "EST"),
                ("MG0010061", "A61", "Toliara", "SUD"),
                ("MG0011001", "A01", "Andavamamba", "TANA CENTRE")
            ]
            
            insert_query = text("""
                INSERT IGNORE INTO agence (code, souscode, nom, id_zone) 
                VALUES (:code, :souscode, :nom, :id_zone)
            """)
            
            inserted_count = 0
            error_count = 0
            for code, souscode, nom, zone_nom in agences_with_zone_names:
                try:
                    # Récupérer l'ID de la zone à partir du nom
                    zone_id = zone_mapping.get(zone_nom)
                    if not zone_id:
                        print(f"[ERREUR] Zone '{zone_nom}' non trouvée pour l'agence {code}")
                        error_count += 1
                        continue
                    
                    result = conn.execute(insert_query, {
                        "code": code,
                        "souscode": souscode,
                        "nom": nom,
                        "id_zone": zone_id
                    })
                    
                    if result.rowcount == 1:
                        inserted_count += 1
                        print(f"[INFO] Agence {code} insérée avec zone {zone_nom} (ID: {zone_id})")
                    else:
                        print(f"[INFO] Agence {code} existe déjà, ignorée")
                        
                except Exception as e:
                    error_count += 1
                    print(f"[ERREUR] Impossible d'insérer l'agence {code}: {e}")
            
            conn.commit()
            print(f"[INFO] Insertion terminée: {inserted_count} nouvelles agences insérées, {error_count} erreurs")
            
        except Exception as e:
            print(f"[ERREUR] Impossible de créer les tables : {e}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Créer une nouvelle agence
    def create_agence(self, code: str, souscode: str, nom: str, id_zone: Optional[int] = None):
        conn = None
        try:
            conn = self.db.connect()

            # Vérifier doublon code
            check_code_q = text("SELECT id FROM agence WHERE code = :code LIMIT 1")
            if conn.execute(check_code_q, {"code": code}).fetchone():
                return {"success": False, "error": "Code d'agence déjà existant"}

            # Vérifier doublon souscode
            check_souscode_q = text("SELECT id FROM agence WHERE souscode = :souscode LIMIT 1")
            if conn.execute(check_souscode_q, {"souscode": souscode}).fetchone():
                return {"success": False, "error": "Sous-code déjà existant"}

            insert_q = text("""
                INSERT INTO agence (code, souscode, nom, id_zone)
                VALUES (:code, :souscode, :nom, :id_zone)
            """)
            result = conn.execute(insert_q, {
                "code": code,
                "souscode": souscode,
                "nom": nom,
                "id_zone": id_zone
            })
            conn.commit()

            return {
                "success": True,
                "message": "Agence créée avec succès",
                "id": result.lastrowid
            }

        except Exception as e:
            print(f"[ERREUR] Impossible de créer l'agence : {e}")
            if conn:
                conn.rollback()
            return {
                "success": False,
                "error": f"Erreur création agence: {str(e)}"
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Récupérer toutes les agences avec informations zone
    def get_all_agences(self):
        conn = None
        try:
            query = text("""
                SELECT 
                    a.id, 
                    a.code, 
                    a.souscode, 
                    a.nom as nom,
                    a.id_zone,
                    z.nom as nom_zone,
                    DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                    DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM agence a
                LEFT JOIN zone z ON a.id_zone = z.id
                ORDER BY a.code
            """)
            
            conn = self.db.connect()
            result = conn.execute(query)
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les agences : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
                    
    def get_code_Agence(self):
        conn = None
        try:
            query = text("""
                SELECT  code
                FROM agence 
                ORDER BY code
            """)
            
            conn = self.db.connect()
            result = conn.execute(query)
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les agences : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Méthodes pour gérer les zones
    def get_all_zones(self):
        conn = None
        try:
            query = text("""
                SELECT id, nom,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM zone 
                ORDER BY nom
            """)
            
            conn = self.db.connect()
            result = conn.execute(query)
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les zones : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Récupérer une agence par son code avec zone
    def get_agence_by_code(self, code: str):
        conn = None
        try:
            query = text("""
                SELECT 
                    a.id, 
                    a.code, 
                    a.souscode, 
                    a.nom as nom_agence,
                    a.id_zone,
                    z.nom as nom_zone,
                    DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                    DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM agence a
                LEFT JOIN zone z ON a.id_zone = z.id
                WHERE a.code = :code
            """)
            
            conn = self.db.connect()
            result = conn.execute(query, {"code": code})
            columns = result.keys()
            row = result.fetchone()
            
            if row:
                return {
                    "success": True,
                    "data": dict(zip(columns, row))
                }
            else:
                return {
                    "success": False,
                    "error": "Agence non trouvée"
                }
                
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer l'agence : {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Mettre à jour une agence avec zone optionnelle
    def update_agence(self, code: str, souscode: Optional[str] = None, nom: Optional[str] = None, id_zone: Optional[int] = None):
        conn = None
        try:
            update_fields = []
            params = {"code": code}
            
            if souscode is not None:
                update_fields.append("souscode = :souscode")
                params["souscode"] = souscode
            
            if nom is not None:
                update_fields.append("nom = :nom")
                params["nom"] = nom
            
            if id_zone is not None:
                update_fields.append("id_zone = :id_zone")
                params["id_zone"] = id_zone
            
            if not update_fields:
                return {
                    "success": False,
                    "error": "Aucun champ à mettre à jour"
                }
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            set_clause = ", ".join(update_fields)
            
            query = text(f"""
                UPDATE agence 
                SET {set_clause}
                WHERE code = :code
            """)
            
            conn = self.db.connect()
            result = conn.execute(query, params)
            conn.commit()
            
            if result.rowcount == 0:
                return {
                    "success": False,
                    "error": "Agence non trouvée"
                }
            
            return {
                "success": True,
                "message": "Agence mise à jour avec succès",
                "rows_affected": result.rowcount
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de mettre à jour l'agence : {e}")
            if conn:
                conn.rollback()
            return {
                "success": False,
                "error": f"Erreur mise à jour: {str(e)}"
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    
    # Supprimer une agence
    def delete_agence(self, code: str):
        conn = None
        try:
            query = text("""
                DELETE FROM agence 
                WHERE code = :code
            """)
            
            conn = self.db.connect()
            result = conn.execute(query, {"code": code})
            conn.commit()
            
            if result.rowcount == 0:
                return {
                    "success": False,
                    "error": "Agence non trouvée"
                }
            
            return {
                "success": True,
                "message": "Agence supprimée avec succès",
                "rows_affected": result.rowcount
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de supprimer l'agence : {e}")
            if conn:
                conn.rollback()
            return {
                "success": False,
                "error": f"Erreur suppression: {str(e)}"
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    
    # Rechercher des agences
    def search_agences(self, search_term: str):
        conn = None
        try:
            query = text("""
                SELECT id, code, souscode, nom,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM agence 
                WHERE code LIKE :search 
                   OR souscode LIKE :search 
                   OR nom LIKE :search
                ORDER BY code
            """)
            
            conn = self.db.connect()
            search_pattern = f"%{search_term}%"
            result = conn.execute(query, {"search": search_pattern})
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            print(f"[ERREUR] Impossible de rechercher les agences : {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
            
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")