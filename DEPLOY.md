# Deployment Guide — EFI WC26 Dashboard

Produktions-Deployment auf **Phusion Passenger / netcup Shared Hosting (Plesk)** —
ohne Docker. Diese Anleitung ist bewusst kleinschrittig geschrieben: jeder Befehl
steht für sich, darunter steht was er tut und was du sehen solltest. Wenn etwas
nicht klappt → Abschnitt **12 — Troubleshooting** ganz unten.

> **So hängt alles zusammen:**
> `Browser` → **SvelteKit Node.js-App** (`domain.com`) → **FastAPI Python-App** (`api.domain.com`) → **MySQL 8.0**
>
> Es sind also **drei** Dinge einzurichten: die Datenbank, das Backend (Python)
> und das Frontend (Node.js). Die Ingestion (PDF-Import) läuft im selben Python-
> Environment wie das Backend.

> **Platzhalter, die du überall ersetzt:**
> - `domain.com` → deine echte Frontend-Domain
> - `api.domain.com` → deine echte Backend-Subdomain
> - `username` → dein Plesk/SSH-Benutzername
> - `/var/www/vhosts/domain.com/wc26` → der Pfad, in den du das Repo hochlädst

---

## 00 — Was du vorher brauchst

| Komponente | Version | Wo in Plesk |
|---|---|---|
| Python | **≥ 3.11** | Plesk → Websites & Domains → **Python** |
| Node.js | **≥ 20 LTS** (22/24 empfohlen — Node 20 ist End-of-Life) | Plesk → **Node.js** |
| MySQL | **8.0** | Plesk → **Datenbanken** |
| SSH-Zugang | — | Plesk → **SSH-Zugang aktivieren** (für `pip`/`npm`) |

**Repo hochladen:** Lade den kompletten Projektordner nach
`/var/www/vhosts/domain.com/wc26` hoch (Git-Clone via SSH oder Datei-Upload).
Danach gibt es dort die Unterordner `backend/`, `frontend/`, `ingestion/`, `db/`.

> Die Datei `.env` ist **nicht** im Repo (steht in `.gitignore`). Du legst sie
> in Schritt 07 selbst an. `.env.example` ist die Vorlage.

---

## 01 — Datenbank einrichten

### 1a. Datenbank + Benutzer anlegen (Plesk-Oberfläche, kein SSH)

1. **Plesk → Datenbanken → Datenbank hinzufügen**
   - Datenbankname: `wc26`
   - Zeichensatz: `utf8mb4`, Kollation: `utf8mb4_unicode_ci`
2. Bei „Zugehöriger Datenbankbenutzer" → **Neuen Benutzer erstellen**
   - Benutzername: `wc26user`
   - Passwort: **starkes Passwort** (in Schritt 08 erzeugen wir eins) → **notieren!**
   - Rechte: alle auf `wc26`

### 1b. Schema + Daten importieren (via SSH)

Verbinde dich per SSH und wechsle in den Projektordner:

```bash
cd /var/www/vhosts/domain.com/wc26
```

Dann der Reihe nach (die **Reihenfolge ist wichtig** — es gibt Fremdschlüssel):

```bash
# 1. Tabellenstruktur (leere Tabellen)
mysql -u wc26user -p wc26 < db/init/01_schema.sql

# 2. Anker-Teams (Deutschland/Curaçao) + Basisdaten
mysql -u wc26user -p wc26 < db/seeds/02_match_10_ger_cur.sql

# 3. Alle 48 Teams + Aggregat-Statistiken
mysql -u wc26user -p wc26 < db/seeds/03_team_aggregates.sql

# 4. Alle Matchdaten (großer Dump aus den PDF-Ingests)
mysql -u wc26user -p wc26 < db/seeds/04_all_matches.sql

# 5. Final-Third-Zonen (separate Datenquelle)
mysql -u wc26user -p wc26 < db/seeds/05_final_third_entries.sql
```

Nach jedem `mysql … -p` fragt es nach dem **Passwort von `wc26user`** (aus 1a).

### 1c. Prüfen, ob die Daten drin sind

```bash
mysql -u wc26user -p wc26 -e "SELECT COUNT(*) AS teams FROM teams; SELECT COUNT(*) AS matches FROM matches;"
```

**Erwartete Ausgabe:** `teams = 48` und `matches ≥ 96`
(die Match-Zahl wächst mit jedem neuen PDF-Ingest — 96 ist der aktuelle Stand).

---

## 02 — Backend (FastAPI) deployen

FastAPI ist eine ASGI-App, Passenger versteht aber nur WSGI. Die Brücke ist das
Paket `a2wsgi` (installieren wir gleich mit).

### 2a. Python-Environment + Pakete

```bash
cd /var/www/vhosts/domain.com/wc26/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt a2wsgi
```

- `venv` = ein isolierter Python-Ordner nur für dieses Projekt.
- `source … activate` = dieses Environment „einschalten" (die Shell zeigt dann `(.venv)` vorn).
- `requirements.txt` ist **auf exakte Versionen gepinnt** → reproduzierbarer Build.

### 2b. `passenger_wsgi.py` anlegen

Lege die Datei `backend/passenger_wsgi.py` mit **genau diesem Inhalt** an
(z. B. `nano backend/passenger_wsgi.py`):

```python
import sys, os
from pathlib import Path
from dotenv import load_dotenv

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))
os.chdir(str(HERE))

load_dotenv(HERE / ".env")

# Virtualenv aktivieren, falls Passenger es nicht selbst tut
activate = HERE / ".venv" / "bin" / "activate_this.py"
if activate.exists():
    exec(activate.read_text(), {"__file__": str(activate)})

from a2wsgi import ASGIMiddleware
from app.main import app

application = ASGIMiddleware(app)
```

### 2c. Plesk: Python-App anlegen

**Plesk → Websites & Domains → (Subdomain `api.domain.com`) → Python:**
- Python-Version: **3.11**
- Application root: `/var/www/vhosts/domain.com/wc26/backend`
- Application startup file: `passenger_wsgi.py`

> Die `.env` befüllst du in **Schritt 07**, bevor du das Backend zum ersten Mal
> startest.

### 2d. Neustart nach jeder Änderung

```bash
mkdir -p /var/www/vhosts/domain.com/wc26/backend/tmp
touch /var/www/vhosts/domain.com/wc26/backend/tmp/restart.txt
```

`touch restart.txt` sagt Passenger „lade die App neu".

---

## 03 — Frontend (SvelteKit) deployen

SvelteKit baut mit `@sveltejs/adapter-node` einen kleinen Node-Server nach
`frontend/build/`.

### 3a. Build erzeugen

```bash
cd /var/www/vhosts/domain.com/wc26/frontend
npm ci
```

`npm ci` installiert exakt die Versionen aus `package-lock.json` (reproduzierbar).

```bash
# Diese Variable muss beim Build gesetzt sein:
export PUBLIC_API_URL=https://api.domain.com
export BODY_SIZE_LIMIT=0

npm run build
```

**Erwartete Ausgabe:** endet mit `✓ built in …` und `Using @sveltejs/adapter-node`.
Danach existiert `frontend/build/index.js`.

### 3b. Plesk: Node.js-App anlegen

**Plesk → Websites & Domains → (Domain `domain.com`) → Node.js:**
- Node.js-Version: **20 oder höher** (22/24 empfohlen)
- Application root: `/var/www/vhosts/domain.com/wc26/frontend`
- Application startup file: `build/index.js`

### 3c. Umgebungsvariablen in Plesk setzen

Im selben Node.js-Panel unter **Environment Variables** (oder „Benutzerdefinierte
Umgebungsvariablen"):

```
ORIGIN           = https://domain.com
PUBLIC_API_URL   = https://api.domain.com
INTERNAL_API_URL = https://api.domain.com
BODY_SIZE_LIMIT  = 0
```

> **`PUBLIC_API_URL` ist Pflicht und muss stimmen.** Sie wird zur Laufzeit vom
> Node-Server gelesen und an den Browser weitergegeben (über SvelteKit
> `$env/dynamic/public`). Fehlt sie, ruft der Browser `localhost:8000` auf →
> nach dem ersten Seitenaufruf lädt nichts mehr.
>
> **`ORIGIN` ist Pflicht** — SvelteKit prüft damit CSRF; ohne sie schlagen alle
> Formular-POSTs (Kontakt, Upload) mit `403` fehl.

### 3d. Nach jedem Frontend-Update

```bash
cd /var/www/vhosts/domain.com/wc26/frontend
npm ci && npm run build
touch tmp/restart.txt
```

---

## 04 — Ingestion (PDF-Import) einrichten

### 4a. Pakete installieren (im Backend-venv)

```bash
source /var/www/vhosts/domain.com/wc26/backend/.venv/bin/activate
pip install -r /var/www/vhosts/domain.com/wc26/ingestion/requirements.txt
```

### 4b. PDF-Drop-Ordner anlegen (außerhalb des Webroots!)

```bash
mkdir -p /home/username/pdf_drop
chmod 700 /home/username/pdf_drop
```

`chmod 700` = nur du darfst rein. **Nicht** unter `httpdocs`/Webroot legen,
sonst wären die PDFs öffentlich abrufbar.

### 4c. Testlauf (schreibt nichts in die DB)

```bash
cd /var/www/vhosts/domain.com/wc26/ingestion
source ../backend/.venv/bin/activate
python -m ingestion.watch_pdfs --dir /home/username/pdf_drop --dry-run
```

**Erwartete Ausgabe:** eine Zeile Richtung „keine neuen PDFs / nichts zu tun".

---

## 05 — Upload-Endpoint absichern

### 5a. Secret erzeugen

```bash
openssl rand -hex 32
```

Kopiere die 64-stellige Ausgabe → in `.env` als `INGEST_SECRET_KEY` (Schritt 07).

### 5b. Upload testen (nach dem Live-Gang)

```bash
curl -X POST https://api.domain.com/api/v1/ingest/upload \
  -H "Authorization: Bearer DEIN_SECRET_KEY" \
  -F "file=@/pfad/zum/Match.pdf"
```

**Erwartete Ausgabe:** `{"status":"ok","file":"Match.pdf", …}`

### 5c. Admin-Oberfläche

`https://domain.com/admin/upload` (bewusst **nicht** im Menü verlinkt). Dort den
API-Key einmal eingeben; „merken"-Häkchen speichert ihn im Browser (localStorage).

> `INGEST_SECRET_KEY` **niemals** in Git committen — `.env` ist in `.gitignore`.

---

## 06 — Cron-Job (automatischer PDF-Import alle 5 Minuten)

**Plesk → Geplante Aufgaben (Scheduled Tasks) → Aufgabe hinzufügen**, Typ „Befehl":

```cron
*/5 * * * * cd /var/www/vhosts/domain.com/wc26/ingestion && /var/www/vhosts/domain.com/wc26/backend/.venv/bin/python -m ingestion.watch_pdfs --dir /home/username/pdf_drop >> /home/username/logs/efi_watch.log 2>&1
```

Log ansehen:

```bash
tail -f /home/username/logs/efi_watch.log
```

> **Datum/Locale:** Der PDF-Parser liest englische Datumsangaben ("13 June 2026")
> jetzt sprachunabhängig — der Cron läuft auch auf einem deutschen Server
> korrekt (kein `LC_TIME` nötig).

---

## 07 — `.env` anlegen (Backend)

```bash
cd /var/www/vhosts/domain.com/wc26/backend
cp ../.env.example .env
nano .env
```

Alle Werte befüllen (Referenz unten). **Danach Backend neu starten**
(`touch tmp/restart.txt`).

### Vollständige Variablen-Referenz

**Datenbank**

| Variable | Pflicht | Produktionswert | Beschreibung |
|---|---|---|---|
| `MYSQL_HOST` | Pflicht | `localhost` | Auf Shared Hosting **immer** `localhost` (nicht `db`) |
| `MYSQL_PORT` | Optional | `3306` | Standard-Port |
| `MYSQL_DATABASE` | Pflicht | `wc26` | Datenbankname |
| `MYSQL_USER` | Pflicht | `wc26user` | DB-Benutzer |
| `MYSQL_PASSWORD` | Pflicht | — | Starkes Passwort aus 1a |

**URLs & CORS**

| Variable | Pflicht | Beispiel | Beschreibung |
|---|---|---|---|
| `PUBLIC_API_URL` | Pflicht | `https://api.domain.com` | Backend-URL für **Browser**-Calls |
| `INTERNAL_API_URL` | Pflicht | `https://api.domain.com` | Backend-URL für **SSR**. Auf Passenger = `PUBLIC_API_URL` |
| `ALLOWED_ORIGIN` | Pflicht | `https://domain.com` | CORS — muss **exakt** die Frontend-Domain sein |
| `ORIGIN` | Pflicht | `https://domain.com` | SvelteKit-CSRF (als **Plesk-Node.js-Env-Var**, nicht in dieser .env) |
| `BODY_SIZE_LIMIT` | Pflicht | `0` | SvelteKit: `0` = unbegrenzt (für PDF-Upload) |

**SMTP (Kontaktformular — optional)**

| Variable | Beschreibung |
|---|---|
| `SMTP_HOST` | z. B. `smtp.gmail.com` |
| `SMTP_PORT` | `587` (STARTTLS) |
| `SMTP_USER` | Absender-Adresse |
| `SMTP_PASS` | Gmail **App-Passwort** (nicht das Hauptpasswort!) |
| `CONTACT_TO_EMAIL` | Empfänger der Kontaktmails |

**PDF-Ingestion**

| Variable | Beispiel | Beschreibung |
|---|---|---|
| `PDF_WATCH_DIR` | `/home/username/pdf_drop` | Absoluter Pfad zum Drop-Ordner |
| `INGEST_SECRET_KEY` | 64-Hex-String | Bearer-Token für den Upload-Endpoint |
| `INGESTION_PYTHON` | `/…/backend/.venv/bin/python` | Python mit den Ingestion-Paketen |
| `INGESTION_MODULE_DIR` | `/…/wc26/ingestion` | Ordner mit dem `ingestion/`-Paket |

---

## 08 — Secrets erzeugen & aufbewahren

```bash
# MySQL-Passwort für wc26user
openssl rand -base64 24

# INGEST_SECRET_KEY
openssl rand -hex 32

# Gmail App-Passwort: myaccount.google.com/apppasswords
```

Alle Secrets in einen **Passwort-Manager** (Bitwarden/1Password). Die `.env` auf
dem Server hat **kein** Git-Backup.

---

## 09 — Deploy-Checkliste (zum Abhaken)

**Datenbank**
- [ ] `wc26` + `wc26user` in Plesk angelegt
- [ ] `01_schema.sql` importiert
- [ ] Seeds `02 → 03 → 04 → 05` in dieser Reihenfolge importiert
- [ ] `SELECT COUNT(*)`: **48 Teams**, **≥ 96 Matches**

**Backend**
- [ ] `.venv` angelegt, `requirements.txt` + `a2wsgi` installiert
- [ ] `backend/.env` befüllt (nicht committet!)
- [ ] `backend/passenger_wsgi.py` erstellt
- [ ] Plesk Python-App auf `api.domain.com`
- [ ] `GET /health` → `{"status":"ok"}`
- [ ] `GET /health/db` → `{"status":"ok"}` (503 = DB nicht erreichbar)
- [ ] `ALLOWED_ORIGIN` == Frontend-Domain

**Frontend**
- [ ] `npm ci` + `npm run build` erfolgreich, `build/index.js` existiert
- [ ] Plesk Node.js-App (Startup `build/index.js`)
- [ ] `ORIGIN`, `PUBLIC_API_URL`, `INTERNAL_API_URL`, `BODY_SIZE_LIMIT` gesetzt
- [ ] Dashboard lädt Daten, **auch nach einem Klick auf eine Unterseite**

**Ingestion**
- [ ] Ingestion-Pakete im Backend-venv
- [ ] Drop-Ordner `chmod 700`, außerhalb Webroot
- [ ] `--dry-run` läuft fehlerfrei
- [ ] `INGEST_SECRET_KEY` gesetzt, Upload per curl getestet
- [ ] Cron-Job eingerichtet

---

## 10 — Verifizierung nach dem Live-Gang

```bash
# Backend erreichbar?
curl https://api.domain.com/health          # → {"status":"ok"}
curl https://api.domain.com/health/db        # → {"status":"ok"}

# CORS korrekt?
curl -I -H "Origin: https://domain.com" https://api.domain.com/api/v1/matches/
# → Header "Access-Control-Allow-Origin: https://domain.com"

# Frontend erreichbar?
curl -sI https://domain.com/                 # → HTTP/2 200

# Sprache/Richtung serverseitig korrekt? (nur relevant bei gesetztem Cookie)
curl -s -H "Cookie: efi-locale=ar" https://domain.com/ | grep -o '<html[^>]*>'
# → <html lang="ar" dir="rtl">   (Arabisch = rechts-nach-links)
```

Im Browser: Startseite lädt das neueste Match, **auf eine Unterseite klicken**
(z. B. „Matches") — die Daten müssen weiterhin laden (das prüft, dass
`PUBLIC_API_URL` im Browser korrekt ankommt).

---

## 11 — Update einspielen (späterer Code-Stand)

```bash
cd /var/www/vhosts/domain.com/wc26
git pull                 # oder neue Dateien hochladen

# Backend-Abhängigkeiten ggf. aktualisieren
cd backend && source .venv/bin/activate && pip install -r requirements.txt
touch tmp/restart.txt

# Frontend neu bauen
cd ../frontend && npm ci && npm run build && touch tmp/restart.txt

# DB-Schemaänderung? Nur dann:
mysql -u wc26user -p wc26 < db/init/01_schema.sql   # (idempotent, CREATE IF NOT EXISTS)
```

---

## 12 — Troubleshooting

| Symptom | Ursache | Lösung |
|---|---|---|
| Startseite lädt, Unterseiten leer/kaputt | `PUBLIC_API_URL` in Plesk-Node-Env fehlt/falsch | Env-Var setzen (Schritt 3c), `touch frontend/tmp/restart.txt` |
| Kontakt/Upload → `403 Forbidden` | `ORIGIN` fehlt | `ORIGIN=https://domain.com` in Plesk-Node-Env, Neustart |
| Browser-Konsole „CORS blocked" | `ALLOWED_ORIGIN` ≠ echte Frontend-Domain | In `backend/.env` exakt angleichen, Backend neu starten |
| `GET /health/db` → `503` | DB nicht erreichbar / falsche Zugangsdaten | `MYSQL_*` in `backend/.env` prüfen (`MYSQL_HOST=localhost`) |
| Backend startet nicht | `a2wsgi` fehlt oder `passenger_wsgi.py` falsch | `pip install a2wsgi`, Datei aus 2b prüfen, Neustart |
| Upload → `{"detail":"Ingestion failed"}` | `INGESTION_PYTHON`/`INGESTION_MODULE_DIR` falsch | Pfade in `.env` prüfen (venv-Python + `ingestion/`-Ordner) |
| Cron importiert nichts | falscher Python-Pfad im Cron | absoluten `…/.venv/bin/python` verwenden, Log prüfen |
| „counts wachsen nicht" nach Upload | PDF war kein gültiges PMSR | Log ansehen; nur echte FIFA-PMSR-PDFs werden akzeptiert |

**Backend/Frontend immer neu starten nach Änderungen:**
`touch <app>/tmp/restart.txt` (Passenger lädt dann neu).
