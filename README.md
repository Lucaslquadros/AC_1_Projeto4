# AC1 — Aplicação de Eventos do Campus

IBM4028 — Projeto em Ciência de Dados IV | IBMEC – CDIA | 2026.2
Entrega individual, 14/09.

Repositório único: `backend/` (FastAPI + SQLAlchemy + Azure Blob Storage) e
`frontend/` (React + Vite), juntando o que foi construído nas Aulas 04–09.

## Rodar local

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # ajuste depois, quando tiver Azure Storage
fastapi dev main.py
```

Abre em `http://127.0.0.1:8000/docs`. Sem `AZURE_STORAGE_CONNECTION_STRING`
no `.env`, tudo funciona exceto o upload de cartaz (`POST /eventos/{id}/cartaz`),
que só falha se for chamado — não impede o resto.

**Frontend** (em outro terminal)

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Abre em `http://localhost:5173`. Os dois precisam estar rodando ao mesmo
tempo.

## Checklist da AC1 (o que precisa estar de pé no dia 14/09)

- [ ] Frontend abre por uma URL pública, com HTTPS
- [ ] A lista de eventos carrega, vinda da API publicada
- [ ] Criar um evento pelo formulário funciona
- [ ] O cartaz é exibido
- [ ] Backend publicado, com banco e storage ligados
- [ ] Repositório sem `.env`, connection string ou chave de acesso

## Roteiro de deploy

Ordem que evita debugar duas coisas ao mesmo tempo: publique e teste o
backend inteiro primeiro, só depois mexa no frontend.

### 1. Backend no Azure — banco, storage e App Service

Recursos na mesma região e no mesmo resource group. Troque `SUFIXO` por
algo único (suas iniciais + números).

```bash
az login
az group create -n rg-ac1 -l brazilsouth

# --- Azure SQL ---
az sql server create -g rg-ac1 -n sql-eventos-SUFIXO -l brazilsouth \
  --admin-user adminac1 --admin-password 'DEFINA-UMA-SENHA-FORTE'

az sql db create -g rg-ac1 -s sql-eventos-SUFIXO -n eventos \
  --service-objective Basic --backup-storage-redundancy Local

# libera o App Service; sem isso o backend não conecta
az sql server firewall-rule create -g rg-ac1 -s sql-eventos-SUFIXO \
  -n permitir-servicos-azure --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# libere também o seu IP, para testar local contra o Azure SQL se quiser
# az sql server firewall-rule create -g rg-ac1 -s sql-eventos-SUFIXO \
#   -n meu-ip --start-ip-address <SEU_IP> --end-ip-address <SEU_IP>

# --- Blob Storage ---
az storage account create -g rg-ac1 -n steventossufixo -l brazilsouth \
  --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2

az storage container create --account-name steventossufixo -n cartazes

STORAGE_CS=$(az storage account show-connection-string \
  -g rg-ac1 -n steventossufixo --query connectionString -o tsv)

# --- App Service ---
az appservice plan create -g rg-ac1 -n plan-ac1 --is-linux --sku F1
az webapp create -g rg-ac1 -p plan-ac1 -n app-eventos-SUFIXO --runtime "PYTHON:3.12"

DB_URL="mssql+pyodbc://adminac1:DEFINA-UMA-SENHA-FORTE@sql-eventos-SUFIXO.database.windows.net:1433/eventos?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

az webapp config appsettings set -g rg-ac1 -n app-eventos-SUFIXO --settings \
  DATABASE_URL="$DB_URL" \
  AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CS" \
  AZURE_STORAGE_CONTAINER=cartazes \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true

# o App Service não adivinha o entrypoint do FastAPI
az webapp config set -g rg-ac1 -n app-eventos-SUFIXO \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"

az webapp config set -g rg-ac1 -n app-eventos-SUFIXO --health-check-path "/health"
az webapp update -g rg-ac1 -n app-eventos-SUFIXO --https-only true
```

`SCM_DO_BUILD_DURING_DEPLOYMENT=true` é o que faz o App Service instalar o
`requirements.txt` — sem isso a aplicação sobe sem as dependências e morre
no import. `gunicorn` precisa estar no `requirements.txt`; adicione
`gunicorn` a ele antes do deploy.

Publique o código (via GitHub Actions do App Service, VS Code Azure
extension, ou `az webapp up`) e confirme:

```bash
curl https://app-eventos-SUFIXO.azurewebsites.net/health
```

`{"status": "ok", "banco": "conectado", ...}` — se falhar, veja
`az webapp log tail -g rg-ac1 -n app-eventos-SUFIXO`.

### 2. Frontend — Static Web Apps (Aula 10)

Passo a passo completo em `../ArquivosAula10/Aula_10_Lab_Deploy_Frontend_Azure.md`.
Resumo:

1. `git init`, `git add .`, `git commit`, `git push` para um repositório novo
   no GitHub (confira que `.env` **não** aparece no `git status`).
2. Portal → **Create a resource → Static Web App**. Source: GitHub, branch
   `main`, Build presets: React, `App location: frontend`,
   `Api location: (vazio)`, `Output location: dist`.
3. O Azure cria `.github/workflows/azure-static-web-apps-....yml`. Abra e
   acrescente o bloco `env` no passo de build:
   ```yaml
   env:
     VITE_API_URL: https://app-eventos-SUFIXO.azurewebsites.net
   ```
4. No `backend/main.py`, adicione a URL do Static Web App em
   `ORIGENS_PERMITIDAS` e publique o backend de novo.
5. `public/staticwebapp.config.json` já está neste projeto — cobre o 404 ao
   recarregar uma rota (não é problema ainda, sem rotas, mas fica pronto).

### 3. Entregar

As duas URLs para o professor: a do Static Web App (frontend) e a do
repositório no GitHub.
