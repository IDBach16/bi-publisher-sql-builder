# Deploy to Streamlit Community Cloud

Goal: publish this app at `https://<your-app>.streamlit.app`.

## What's deployable

| Feature | Cloud | Local |
| --- | --- | --- |
| AI SQL generator (Claude) | yes | yes |
| Schema browser (65 tables) | yes | yes |
| Examples / Quick Reference | yes | yes |
| Catalog Library (RAG) | only if you commit catalog files | yes |
| Live Fusion JDBC test | **no** (no JVM on SCC) | yes |

The `jpype` + `JayDeBeApi` packages and the 81 MB `orfujdbc` JAR are local-only and excluded from the deploy.

## One-time setup

### 1. Create a GitHub repo for this app

This folder needs its own repo (not nested inside your home dir's repo).

```bash
cd "C:/Users/IBach/OneDrive - Terillium/Desktop/BI_Publisher_App"
git init -b main
git add .
git status                  # double-check no .env, no *.jar, no client catalogs
git commit -m "Initial commit"
```

Create a **private** empty repo on github.com (private is strongly recommended — even with .gitignore, this is internal tooling). Then:

```bash
git remote add origin https://github.com/<your-user>/<repo>.git
git push -u origin main
```

### 2. Connect Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with your GitHub account.
2. Click **New app**.
3. Pick your repo, branch `main`, main file path `app.py`.
4. Click **Advanced settings** -> **Secrets** and paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

5. Click **Deploy**. First build takes ~3 minutes (installs streamlit, anthropic, pandas, openpyxl, python-dotenv).

You'll get a URL like `https://bi-publisher-sql-builder.streamlit.app`.

## What I changed for cloud safety

- `app.py` imports wrap `jpype` / `jaydebeapi` in `try/except`. If they're not installed, `JDBC_AVAILABLE = False` and the live Fusion fields are disabled with a notice. SQL generation still works.
- `_get_secret()` helper reads from `st.secrets` first (cloud) then env vars (local). Anthropic API key works in both.
- `requirements.txt` has `jpype1` / `JayDeBeApi` / `pyperclip` commented out so the cloud build doesn't try to pull a JVM.
- `.gitignore` excludes `.env`, `*.jar`, `.streamlit/secrets.toml`, `__pycache__/`, and (by default) the `.xdm.catalog` client files.

## Want the Catalog Library populated in production?

The `.xdm.catalog` files contain client-specific SQL. Two options:

**Option A — Commit them to your private repo (recommended if repo is private):**
Open `.gitignore` and delete these two lines:
```
*.xdm.catalog
Data Models.catalog
```
Then `git add *.xdm.catalog && git commit -m "Add catalog library"`.

**Option B — Keep them out, add an upload feature:** the app would need a new code path that takes uploaded catalog files at runtime. Ask if you want me to wire that.

## Local dev still works the same

`.env` and the JDBC packages are unchanged for local use:

```bash
pip install -r requirements.txt
pip install jpype1 JayDeBeApi pyperclip   # local-only extras
streamlit run app.py
```

## Updating the deployed app

Every `git push` to `main` triggers an auto-redeploy. No manual step needed.
