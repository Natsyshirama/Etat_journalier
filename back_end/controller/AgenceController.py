from typing import List, Optional
from sqlalchemy import text
from datetime import datetime
from db.db import DB

class AgenceController:
    def __init__(self):
        self.db = DB()
        
        conn = self.db.connect()
        try:
            query = text("""
                CREATE TABLE IF NOT EXISTS agence (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    souscode VARCHAR(10) UNIQUE NOT NULL,
                    nom VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_code (code),
                    INDEX idx_souscode (souscode)
                )
            """)
            
            conn = self.db.connect()
            conn.execute(query)
            conn.commit()
            print("[INFO] Table 'agence' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table agence : {e}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion: {close_err}")
    # Créer une nouvelle agence
    def create_agence(self, code: str, souscode: str, nom: str):
        conn = None
        try:
            query = text("""
                INSERT INTO agence (code, souscode, nom)
                VALUES (:code, :souscode, :nom)
            """)
            
            conn = self.db.connect()
            result = conn.execute(query, {
                "code": code,
                "souscode": souscode,
                "nom": nom
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
    
    # Récupérer toutes les agences
    def get_all_agences(self):
        conn = None
        try:
            query = text("""
                SELECT id, code, souscode, nom, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
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
    
    # Récupérer une agence par son code
    def get_agence_by_code(self, code: str):
        conn = None
        try:
            query = text("""
                SELECT id, code, souscode, nom,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM agence 
                WHERE code = :code
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
    
    # Mettre à jour une agence
    def update_agence(self, code: str, souscode: Optional[str] = None, nom: Optional[str] = None):
        conn = None
        try:
            # Construire dynamiquement la requête UPDATE
            update_fields = []
            params = {"code": code}
            
            if souscode is not None:
                update_fields.append("souscode = :souscode")
                params["souscode"] = souscode
            
            if nom is not None:
                update_fields.append("nom = :nom")
                params["nom"] = nom
            
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