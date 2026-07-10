# Deployment Guide — EFI WC26 Dashboard

Produktions-Deployment auf Phusion Passenger / netcup Shared Hosting.
Backend (FastAPI), Frontend (SvelteKit) und Ingestion-Pipeline laufen als
separate Passenger-Apps — ohne Docker.

> **Architektur:** Browser → SvelteKit Node.js App (`domain.com`) → FastAPI Python App (`api.domain.com`) → MySQL 8.0

---

## Voraussetzungen

| Komponente | Version | Bezug |
|---|---|---|
| Python | ≥ 3.11 | Plesk Python-App-Modul |
| Node.js | ≥ 20 LTS | Plesk Node.js-Modul |
| MySQL | 8.0 | Plesk Datenbanken |
| SSH-Zugang | — | Für pip install, npm build |

---

## 01 — Datenbankeinrichtung

### Datenbank und User anlegen (Plesk)

1. **Plesk → Datenbanken → Datenbank hinzufügen**
   - Name: `wc26`
   - Zeichensatz: `utf8mb4`
   - Kollation: `utf8mb4_unicode_ci`

2. **Datenbankbenutzer anlegen**
   - User: `wc26user` · Starkes Passwort · Alle Rechte auf `wc26`

### Schema und Seeds importieren (via SSH)

```bash
# Schema
mysql -u wc26user -p wc26 < db/init/01_schema.sql

# Seeds — Reihenfolge wichtig (FK-Abhängigkeiten)!
mysql -u wc26user -p wc26 < db/seeds/02_match_10_ger_cur.sql
mysql -u wc26user -p wc26 < db/seeds/03_team_aggregates.sql
mysql -u wc26user -p wc26 < db/seeds/04_all_matches.sql
mysql -u wc26user -p wc26 < db/seeds/05_final_third_entries.sql
```

### Verifizieren

```bash
mysql -u wc26user -p wc26 -e "SELECT COUNT(*) AS teams FROM teams; SELECT COUNT(*) AS matches FROM matches;"
# Erwartet: 48 Teams · ≥ 88 Matches (wächst mit jedem neuen PDF-Ingest)
```

> **Hinweis:** Auf Plesk Shared Hosting ist `MYSQL_HOST=localhost` zu setzen, nicht `db` (Docker-Servicename).

---

## 02 — Backend deployen (FastAPI)

FastAPI ist ASGI. Passenger unterstützt nativ nur WSGI. Die Bridge erfolgt über `a2wsgi`.

### Virtualenv und Abhängigkeiten

```bash
cd /var/www/vhosts/domain.com/wc26/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt a2wsgi
```

### .env anlegen

```bash
cp ../.env.example .env
nano .env   # alle Werte befüllen (siehe Abschnitt 06)
```

### passenger_wsgi.py erstellen

Datei `backend/passenger_wsgi.py` anlegen:

```python
import sys, os
from pathlib import Path
from dotenv import load_dotenv

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))
os.chdir(str(HERE))

load_dotenv(HERE / ".env")

# Virtualenv aktivieren (falls Passenger nicht automatisch aktiviert)
activate = HERE / ".venv" / "bin" / "activate_this.py"
if activate.exists():
    exec(activate.read_text(), {"__file__": str(activate)})

from a2wsgi import ASGIMiddleware
from app.main import app

application = ASGIMiddleware(app)
```

### Plesk: Python-App konfigurieren

- Domain: `api.domain.com`
- Python-Version: `3.11`
- Application root: `/var/www/vhosts/domain.com/wc26/backend`
- Application startup file: `passenger_wsgi.py`

### Passenger-Restart nach Änderungen

```bash
mkdir -p backend/tmp && touch backend/tmp/restart.txt
```

---

## 03 — Frontend deployen (SvelteKit)

SvelteKit nutzt `@sveltejs/adapter-node` → erzeugt `frontend/build/index.js`.

### Build erstellen

```bash
cd /var/www/vhosts/domain.com/wc26/frontend
npm ci

# Env-Variablen für den Build
export PUBLIC_API_URL=https://api.domain.com
export BODY_SIZE_LIMIT=0

npm run build
# Erzeugt: frontend/build/index.js  (Node.js-Server)
#           frontend/build/client/   (statische Assets)
```

### Plesk: Node.js-App konfigurieren

- Domain: `domain.com`
- Node.js-Version: `20`
- Application root: `/var/www/vhosts/domain.com/wc26/frontend`
- Application startup file: `build/index.js`

### Umgebungsvariablen in Plesk (Environment Variables)

```
ORIGIN           = https://domain.com
PUBLIC_API_URL   = https://api.domain.com
INTERNAL_API_URL = https://api.domain.com
BODY_SIZE_LIMIT  = 0
```

> **ORIGIN ist Pflicht.** SvelteKit benötigt es zur CSRF-Validierung — ohne es schlagen alle POSTs mit 403 fehl.

### Nach jedem Code-Update

```bash
cd frontend && npm ci && npm run build
touch tmp/restart.txt
```

---

## 04 — Ingestion & PDF-Verzeichnis

### Abhängigkeiten installieren

Im gleichen Virtualenv wie das Backend (empfohlen):

```bash
source /var/www/vhosts/domain.com/wc26/backend/.venv/bin/activate
pip install -r /var/www/vhosts/domain.com/wc26/ingestion/requirements.txt
```

### PDF-Drop-Verzeichnis anlegen

```bash
mkdir -p /home/username/pdf_drop
chmod 700 /home/username/pdf_drop   # nicht öffentlich erreichbar!
```

### Test (Dry-run)

```bash
cd /var/www/vhosts/domain.com/wc26/ingestion
source ../backend/.venv/bin/activate
python -m ingestion.watch_pdfs --dir /home/username/pdf_drop --dry-run
# Erwartet: "No PDF files found ... nothing to do"
```

---

## 05 — PDF-Upload-Endpoint absichern

### Secret Key generieren

```bash
openssl rand -hex 32
# Ausgabe in .env als INGEST_SECRET_KEY eintragen
```

### Test mit curl

```bash
curl -X POST https://api.domain.com/api/v1/ingest/upload \
  -H "Authorization: Bearer DEIN_SECRET_KEY" \
  -F "file=@/pfad/zum/Match.pdf"
# Erwartet: {"status":"ok","file":"Match.pdf","log":"..."}
```

### Admin-UI

Unter `https://domain.com/admin/upload` — nicht im Navigations-Menü verlinkt.
API-Key einmalig eingeben (optional im Browser speichern via localStorage).

> **Wichtig:** `INGEST_SECRET_KEY` niemals in Git committen. Die `.env` ist in `.gitignore`.

---

## 06 — Cron-Job einrichten

`watch_pdfs.py` ist der Cron-basierte Fallback — verarbeitet alle neuen PDFs im Drop-Ordner alle 5 Minuten.

**Plesk → Scheduled Tasks → Neuer Task:**

```cron
*/5 * * * * cd /var/www/vhosts/domain.com/wc26/ingestion \
  && /var/www/vhosts/domain.com/wc26/backend/.venv/bin/python \
  -m ingestion.watch_pdfs \
  --dir /home/username/pdf_drop \
  >> /home/username/logs/efi_watch.log 2>&1
```

### Log überwachen

```bash
tail -f /home/username/logs/efi_watch.log
```

---

## 07 — Umgebungsvariablen — Vollständige Referenz

### Datenbank

| Variable | Pflicht | Produktionswert | Beschreibung |
|---|---|---|---|
| `MYSQL_HOST` | Pflicht | `localhost` | Auf Shared Hosting immer `localhost` |
| `MYSQL_PORT` | Optional | `3306` | Standard MySQL-Port |
| `MYSQL_DATABASE` | Pflicht | `wc26` | Datenbankname |
| `MYSQL_USER` | Pflicht | `wc26user` | DB-Benutzer |
| `MYSQL_PASSWORD` | Pflicht | — | Starkes Passwort |

### URLs & CORS

| Variable | Pflicht | Beispielwert | Beschreibung |
|---|---|---|---|
| `PUBLIC_API_URL` | Pflicht | `https://api.domain.com` | Backend-URL für Browser-Calls |
| `INTERNAL_API_URL` | Pflicht | `https://api.domain.com` | Backend-URL für SSR. Auf Passenger = PUBLIC_API_URL |
| `ALLOWED_ORIGIN` | Pflicht | `https://domain.com` | CORS-erlaubte Origin (muss exakt passen) |
| `ORIGIN` | Pflicht | `https://domain.com` | SvelteKit CSRF-Origin (Plesk Node.js Env-Var) |
| `BODY_SIZE_LIMIT` | Pflicht | `0` | SvelteKit: `0` = unlimitiert (für PDF-Upload) |

### SMTP (Kontaktformular)

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `SMTP_HOST` | Optional | SMTP-Server (z. B. `smtp.gmail.com`) |
| `SMTP_PORT` | Optional | `587` (STARTTLS) |
| `SMTP_USER` | Optional | Absender-E-Mail-Adresse |
| `SMTP_PASS` | Optional | Gmail App-Passwort (nicht Hauptpasswort!) |
| `CONTACT_TO_EMAIL` | Optional | Empfänger für Kontaktformular-Mails |

### PDF-Ingestion

| Variable | Pflicht | Beispielwert | Beschreibung |
|---|---|---|---|
| `PDF_WATCH_DIR` | Pflicht | `/home/user/pdf_drop` | Absoluter Pfad zum Drop-Verzeichnis |
| `INGEST_SECRET_KEY` | Pflicht | 64-stelliger Hex-String | Bearer-Token für Upload-Endpoint |
| `INGESTION_PYTHON` | Pflicht | `/pfad/.venv/bin/python3` | Python-Interpreter mit Ingestion-Deps |
| `INGESTION_MODULE_DIR` | Pflicht | `/pfad/wc26/ingestion` | Verzeichnis mit dem `ingestion/`-Paket |

---

## 08 — Secrets — Generierung & Aufbewahrung

```bash
# MySQL-Passwort
openssl rand -base64 24

# INGEST_SECRET_KEY
openssl rand -hex 32

# Gmail App-Passwort
# → myaccount.google.com/apppasswords
```

**Backup:** Alle Secrets in einem Passwort-Manager speichern (Bitwarden, 1Password o.ä.).
Die `.env` auf dem Server hat keinen Git-Backup.

---

## 09 — Deploy-Checkliste

### Datenbank
- [ ] MySQL-Datenbank `wc26` und User `wc26user` in Plesk angelegt
- [ ] `db/init/01_schema.sql` importiert
- [ ] Alle Seeds in Reihenfolge importiert (02 → 03 → 04 → 05)
- [ ] 48 Teams, ≥ 88 Matches per `SELECT COUNT(*)` bestätigt

### Backend
- [ ] Virtualenv angelegt, `requirements.txt` + `a2wsgi` installiert
- [ ] `backend/.env` befüllt (nicht committet!)
- [ ] `backend/passenger_wsgi.py` erstellt
- [ ] Plesk Python-App konfiguriert (`api.domain.com`)
- [ ] `GET /health` gibt `{"status":"ok"}` zurück
- [ ] CORS: `ALLOWED_ORIGIN` stimmt exakt mit Frontend-Domain überein

### Frontend
- [ ] `npm ci` und `npm run build` erfolgreich
- [ ] `frontend/build/index.js` existiert
- [ ] Plesk Node.js-App konfiguriert (Startup: `build/index.js`)
- [ ] `ORIGIN` und `PUBLIC_API_URL` in Plesk Env-Vars gesetzt
- [ ] `BODY_SIZE_LIMIT=0` gesetzt
- [ ] Dashboard im Browser erreichbar, Daten werden geladen

### PDF-Ingestion
- [ ] Ingestion-Deps im Backend-Virtualenv installiert
- [ ] PDF-Drop-Verzeichnis angelegt, `chmod 700`
- [ ] `watch_pdfs.py --dry-run` läuft ohne Fehler
- [ ] `INGEST_SECRET_KEY` gesetzt
- [ ] Upload-Endpoint mit curl getestet
- [ ] Cron-Job in Plesk Scheduled Tasks eingerichtet

---

## 10 — Verifizierung

```bash
# Backend
curl https://api.domain.com/health
curl https://api.domain.com/health/db

# CORS
curl -I -H "Origin: https://domain.com" https://api.domain.com/api/v1/matches/
# → Access-Control-Allow-Origin: https://domain.com

# Frontend
curl -sI https://domain.com/
# → HTTP/2 200
```
