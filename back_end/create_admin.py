import bcrypt
from sqlalchemy import create_engine, text

engine = create_engine("'mysql+pymysql://rgab-dev:azerty%402026@localhost/money_deb'")

username = "admin"
password = "admin"
immatricule = "ADMIN"

hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

with engine.connect() as conn:
    conn.execute(
        text("""
            INSERT INTO users (
                username, password, immatricule, privillege,
                validate_status, is_blocked, validate_by, validate_at
            )
            VALUES (
                :username, :password, :immatricule, :privillege,
                TRUE, FALSE, 'script', NOW()
            )
            ON DUPLICATE KEY UPDATE
                password = VALUES(password),
                immatricule = VALUES(immatricule),
                privillege = VALUES(privillege),
                validate_status = TRUE,
                is_blocked = FALSE,
                validate_by = 'script',
                validate_at = NOW()
        """),
        {
            "username": username,
            "password": hashed_password,
            "immatricule": immatricule,
            "privillege": "admin",
        },
    )
    conn.commit()

print("Utilisateur admin créé/modifié avec succès.")