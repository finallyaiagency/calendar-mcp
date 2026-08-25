# DEPLOY TO VERCEL

## 1. Push to GitHub
```bash
cd /home/jarvis/calendar-mcp
git init
git add .
git commit -m "Calendar MCP MVP"
# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/calendar-mcp.git
git push -u origin main
```

## 2. Import on Vercel
- Go to https://vercel.com/new
- Import your GitHub repo
- Framework: **FastAPI** (auto-detected)
- Root Directory: `./` (project root)
- Build Command: `pip install -r requirements.txt`
- Output Directory: `.`

## 3. Set Environment Variables (Vercel Dashboard)
Go to **Settings → Environment Variables** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@ep-xxx.neon.tech/dbname` | Production, Preview, Development |
| `SECRET_KEY` | `openssl rand -hex 32` output | Production, Preview, Development |

## 4. Deploy
Click **Deploy**. Vercel will:
1. Install `requirements.txt` (includes `mangum`)
2. Build the serverless function at `api/index.py`
3. Serve at `https://calendar-mcp-xxx.vercel.app`

## 5. Run DB Init (one-time)
After first deploy, run locally with prod env to create tables:
```bash
# Option A: Pull Vercel env locally
vercel env pull .env.production.local

# Option B: Set locally temporarily
export DATABASE_URL="your-neon-url"
export SECRET_KEY="your-secret"
python init_db.py
```

## 6. Test Endpoints
```
https://your-app.vercel.app/                          # health
https://your-app.vercel.app/auth/register             # POST
https://your-app.vercel.app/auth/login                # POST
https://your-app.vercel.app/calendar/                 # GET (needs Bearer token)
https://your-app.vercel.app/ics/upload/1              # POST file (needs Bearer)
https://your-app.vercel.app/mcp/tools/call            # POST (MCP tools)
```

---

**Notes:**
- Vercel serverless = cold starts (~1-2s first request). OK for MCP agents.
- Max function duration: 30s (set in `vercel.json`).
- For persistent MCP stdio connections, you'd need a separate long-running server (Railway/Fly.io/Render). Vercel is HTTP-only.
- If you need MCP stdio transport for agents, deploy to Railway/Render instead and use Vercel only for the web UI.