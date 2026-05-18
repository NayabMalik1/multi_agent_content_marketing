# ✦ ContentFlow AI — Multi-Agent Content Marketing Pipeline

> **Generate a full SEO-optimised blog post in ~3 minutes using 6 AI agents.**  
> 100% free APIs · Gemini LLM · SQLite · Streamlit

---

## 📁 Folder Structure

```
contentflow_ai/
├── app.py                    ← Streamlit UI + pipeline orchestrator
├── database.py               ← SQLite (3 tables)
├── llm_helper.py             ← Gemini LLM wrapper
├── .env.example              ← API key template
├── .gitignore
├── requirements.txt
├── README.md
└── agents/
    ├── __init__.py
    ├── researcher.py         ← SerpAPI + keyword research
    ├── writer.py             ← Full blog draft
    ├── seo_optimizer.py      ← Meta tags + internal links
    ├── editor.py             ← Quality score + feedback loop
    ├── visual_designer.py    ← Unsplash image sourcing
    └── publisher.py          ← HTML assembly + WordPress API
```

---

## 🚀 Run Locally

### 1. Clone / copy the project
```bash
git clone https://github.com/YOUR_USERNAME/contentflow-ai
cd contentflow_ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (required)
# All other keys are optional
```

### 4. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this folder to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch `main`, file `app.py`
4. In **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   UNSPLASH_ACCESS_KEY = "optional"
   SERPAPI_KEY = "optional"
   ```
5. Click **Deploy** — done! ✅

> **Note for Streamlit Cloud:** The SQLite DB resets on each cold start (ephemeral filesystem). For persistent storage, swap `database.py` to use `st.session_state` or a free Supabase DB.

---

## 🔑 API Keys (All Free)

| API | Purpose | Free Tier | Link |
|-----|---------|-----------|------|
| **Gemini** | LLM (required) | Generous free RPM | [aistudio.google.com](https://aistudio.google.com) |
| **Unsplash** | Stock images | 50 req/hour | [unsplash.com/developers](https://unsplash.com/developers) |
| **SerpAPI** | Search results | 100/month | [serpapi.com](https://serpapi.com) |
| **WordPress** | Publishing | Your own site | [wordpress.com](https://wordpress.com) |

---

## 🤖 The 6 Agents

```
Topic Input
    │
    ▼
[1] Researcher ──────► keyword list + outline
    │
    ▼
[2] Writer ◄──────────────────────────┐
    │                                 │ feedback if score < threshold
    ▼                                 │
[4] Editor ───────────────────────────┘ (feedback loop, up to N retries)
    │ approved ✓
    ▼
[3] SEO Optimizer ──► meta title, description, internal links
    │
    ▼
[5] Visual Designer ──► Unsplash images + HTML embeds
    │
    ▼
[6] Publisher ──────► Final HTML file + optional WordPress post
```

### Feedback Loop Detail
- Editor scores content 1–10
- If score < configured threshold (default: 7), feedback is sent back to Writer
- Writer rewrites with specific instructions
- Repeats up to `max_retries` times (configurable in UI)

---

## 💰 Business Value

| | Manual | ContentFlow AI |
|-|--------|----------------|
| Time per article | 6–8 hours | ~3 minutes |
| Cost (freelancer) | $240–$400 | ~$0.02 |
| SEO research | 1–2 hours extra | Included |
| Image sourcing | 30 min extra | Included |
| **Monthly (10 articles)** | **~$3,200** | **~$0.20** |

---

## 🗃️ Database Tables

```sql
pipeline_runs    → tracks each topic run + status + final content
agent_logs       → per-agent input/output/iterations log  
content_versions → every draft saved (supports rewrite history)
```

---

## ✅ Requirements Mapping

| Requirement | How It's Met |
|-------------|-------------|
| LLM (free) | Google Gemini 1.5 Flash |
| SQLite DB | 3 tables, auto-created on first run |
| External API #1 | SerpAPI (search/keyword research) |
| External API #2 | Unsplash (image sourcing) |
| External API #3 | WordPress REST API (publishing) |
| 6 Agents | All implemented as separate classes |
| Feedback loop | Editor → Writer loop with configurable retries |
| Real-time UI | Live agent card updates per step |
| Downloadable output | HTML download button |
| Streamlit Cloud | requirements.txt + secrets config ready |
| Original code | 100% original, no templates copied |
