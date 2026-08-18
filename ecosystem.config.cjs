module.exports = {
  apps: [
    {
      name: "fastapi-backend",
      script: "/var/www/money/Etat_journalier/venv/bin/python",
      args: "-m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4",
      cwd: "/var/www/money/Etat_journalier/back_end",
      autorestart: true,
      watch: false
    }
  ]
}