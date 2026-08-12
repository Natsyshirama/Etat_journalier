module.exports = {
  apps: [
    {
      name: "fastapi-backend",
      script: "D:\\marc\\GAB\\Etat_journalier\\.venv\\Scripts\\python.exe",
      args: "-m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4",
      cwd: "D:\\marc\\GAB\\Etat_journalier\\back_end",
      autorestart: true,
      watch: false
    }
  ]
}