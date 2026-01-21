Backup Server (API)

Start:
  set BACKUP_API_TOKEN=your_token
  set BACKUP_PORT=8080
  python server.py

Endpoints (1 ultimo backup por chave):
  GET /health
    Authorization: Bearer <token>
    Response: {"status":"ok"}

  POST /backup
    Authorization: Bearer <token>
    Body: {"backup_key":"...","payload":{...}}

  GET /backup/{backup_key}
    Authorization: Bearer <token>
    Response: {"backup_key":"...","created_at":"...","payload":{...}}
