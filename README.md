# Mini RCM Validation Engine

This prototype ingests claims, applies technical/medical rules (static + LLM), and surfaces outcomes in a Next.js UI backed by a Django API.

## Requirements

- Python 3.11+
- Node.js 18+
- Windows PowerShell (commands below use PowerShell)

## Backend (Django)

1. Create venv and install deps

```powershell
cd rcm-validation-engine
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Migrate and create admin user

```powershell
python manage.py migrate
python manage.py createsuperuser
```

3. Run server

```powershell
$env:DJANGO_DEBUG="1"
python manage.py runserver 0.0.0.0:8000
```

### API quick-check

- Health: GET http://localhost:8000/api/health/
- Auth: POST http://localhost:8000/api/auth/token/ {"username","password"}
- Create Tenant: POST http://localhost:8000/api/tenants/ {"name","code"} (use admin token or superuser session)
- Upload Rules: POST http://localhost:8000/api/rulesets/upload/ (form-data) technical, medical files; header `X-Tenant-ID: <tenantId>`
- Upload Claims: POST http://localhost:8000/api/upload/claims/ (form-data) file=.csv/.xlsx; header `X-Tenant-ID`
- Validate: POST http://localhost:8000/api/validate/ header `X-Tenant-ID`
- Results: GET http://localhost:8000/api/results/ header `X-Tenant-ID`

Env vars (optional):

- OPENAI_API_KEY, OPENAI_MODEL (for LLM evaluation)

## Frontend (Next.js)

1. Install deps

```powershell
cd "c:\Users\yordanos\Desktop\please work\frontend"
npm install
```

2. Configure API base URL
   Create `.env.local` in frontend:

```powershell
"NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api"
```

3. Run dev server

```powershell
npm run dev
```

## Usage Flow

1. Visit http://localhost:3000 and go to Login
2. Sign in with your Django superuser credentials
3. Enter Tenant ID (from admin or POST /tenants)
4. Upload technical/medical rules and claims
5. Run validation and view charts + table on dashboard

## Notes

- Multi-tenant is via `X-Tenant-ID` header (frontend sets from saved Tenant ID).
- Rule files: JSON/YAML/CSV/XLSX accepted. CSV/XLSX columns expected: category,id,type,field,operator,value,severity,message,error_type,recommendation.
- LLM is optional; if no OPENAI_API_KEY is set, pipeline still runs static rules.

## Demo Seed

To quickly try end-to-end with sample data:

```powershell
Set-Location -Path "c:\Users\yordanos\Desktop\rcm-validation-engine\backend"
. .\.venv\Scripts\Activate.ps1
# (optional) use Neon DB
# $env:DATABASE_URL = "postgresql://..."
python manage.py seed_demo
```

The command prints the Tenant ID. Use it in the UI login page as the tenant, then:

- Upload rules if you want to override the demo rules
- Run validation (already run by seed) and Refresh Results
