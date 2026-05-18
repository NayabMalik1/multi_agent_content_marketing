import streamlit as st
import time
import os
from dotenv import load_dotenv

load_dotenv()

import database as db
from agents import (
    ResearcherAgent, WriterAgent, SEOOptimizerAgent,
    EditorAgent, PublisherAgent
)
from utils import generate_pdf

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ContentFlow AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

/* ── Header banner ── */
.header-banner {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 1.75rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin: 0 0 6px 0;
    line-height: 1.1;
}
.subtitle {
    color: #94a3b8;
    font-size: 0.92rem;
    font-weight: 400;
    margin: 0;
    line-height: 1.5;
}

/* ── Agent cards ── */
.agent-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.875rem 1rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.875rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.agent-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 8px 25px -8px rgba(59,130,246,0.3);
    transform: translateX(4px);
}
.agent-card.running {
    border-color: #3b82f6;
    background: #eff6ff;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}
.agent-card.done    { border-color: #22c55e; background: #f0fdf4; }
.agent-card.error   { border-color: #ef4444; background: #fef2f2; }
.agent-card.pending { border-color: #e2e8f0; background: #ffffff; }

.agent-icon {
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.agent-card:hover .agent-icon { transform: scale(1.15) rotate(2deg); }
.agent-card.running .agent-icon { animation: pulse 1.5s ease-in-out infinite; }

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.08); }
}
.agent-icon svg {
    width: 28px; height: 28px;
    transition: all 0.3s ease;
}
.agent-card:hover .agent-icon svg {
    filter: drop-shadow(0 4px 8px rgba(59,130,246,0.3));
}
.agent-name   { font-weight: 600; font-size: 0.9rem;  color: #0f172a; }
.agent-status { font-size: 0.75rem; color: #475569; font-weight: 400; }

/* ── Metric boxes ── */
.metric-box {
    background: linear-gradient(135deg, #1e293b, #334155);
    border-radius: 12px;
    padding: 1rem;
    color: #ffffff;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
}
.metric-val   { font-size: 1.75rem; font-weight: 700; color: #ffffff; }
.metric-label { font-size: 0.7rem; opacity: 0.85; letter-spacing: 0.5px; color: #e2e8f0; }

/* ── Feedback badge ── */
.feedback-badge {
    display: inline-block;
    background: #fef3c7; color: #92400e;
    padding: 0.15rem 0.5rem; border-radius: 20px;
    font-size: 0.7rem; font-weight: 500; margin-left: 0.5rem;
}

/* ── Buttons ── */
.stButton>button {
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 500 !important; padding: 0.5rem 1.5rem !important;
    font-size: 0.9rem !important; transition: all 0.3s ease !important;
}
.stButton>button:hover {
    opacity: 0.95 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px -8px rgba(0,0,0,0.3) !important;
}

/* ═══════════════════════════════════════════════════════
   FIX 1 — Sidebar: force light background + dark text
   so inputs, labels, and captions are always readable
   ═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #f8fafc !important;
}
/* Every text node inside the sidebar */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] caption,
[data-testid="stSidebar"] .stCaption {
    color: #1e293b !important;
}
/* Input boxes */
[data-testid="stSidebar"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}
[data-testid="stSidebar"] input::placeholder {
    color: #94a3b8 !important;
}
/* Help tooltip icons */
[data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg {
    stroke: #64748b !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]           { gap: 1.5rem; }
.stTabs [data-baseweb="tab"]               { font-weight: 500; font-size: 0.9rem; color: #475569; }
.stTabs [data-baseweb="tab"]:hover         { color: #3b82f6; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #1e293b; font-weight: 600; }

/* ── Expander ── */
.streamlit-expanderHeader { font-weight: 500; font-size: 0.85rem; color: #1e293b; }
.streamlit-expanderHeader:hover { color: #3b82f6; }

/* ── Download caption ── */
.download-caption {
    font-size: 0.7rem; color: #64748b;
    margin-top: 0.25rem; text-align: center;
}

/* ── History run card ── */
.history-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.history-meta { font-size: 0.8rem; color: #475569; margin-top: 2px; }

/* ── Alerts ── */
.stAlert { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ============================================================================
# SVG ICONS
# ============================================================================
def get_svg_icon(icon_name, color="#4f46e5"):
    icons = {
        "logo": f'''<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4h16v16H4z"/><path d="M8 8h8M8 12h6M8 16h4"/>
        </svg>''',

        "researcher": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="8" y1="11" x2="14" y2="11"/>
            <line x1="11" y1="8" x2="11" y2="14"/>
        </svg>''',

        "writer": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
            <path d="M15 5l4 4"/>
        </svg>''',

        "seo": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
            <polyline points="16 7 22 7 22 13"/>
        </svg>''',

        "editor": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>''',

        "chart": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6"  y1="20" x2="6"  y2="14"/>
            <line x1="2"  y1="20" x2="22" y2="20"/>
        </svg>''',

        "publisher": f'''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>''',

        "check": f'''<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
        </svg>''',

        "spinner": f'''<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="15.7">
                <animateTransform attributeName="transform" type="rotate"
                    from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </circle>
        </svg>''',

        "download": f'''<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>''',

        "settings": f'''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H5.78a1.65 1.65 0 0 0-1.51 1 1.65 1.65 0 0 0 .33 1.82l.07.07A10 10 0 0 0 12 17.66a10 10 0 0 0 6.18-2.59z"/>
        </svg>''',

        "folder": f'''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>''',

        "dollar": f'''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M8 8h6a2 2 0 0 1 0 4h-4a2 2 0 0 0 0 4h6"/>
            <path d="M12 6v2M12 16v2"/>
        </svg>''',
    }
    return icons.get(icon_name, icons["logo"])


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        {get_svg_icon("logo", "#1e293b")}
        <span style="font-size:1.2rem; font-weight:700; color:#0f172a;">ContentFlow AI</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Past runs ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        {get_svg_icon("folder")}
        <span style="font-weight:600; color:#1e293b; font-size:0.9rem;">Past Runs</span>
    </div>
    """, unsafe_allow_html=True)

    runs = db.get_all_runs()
    if runs:
        for run in runs[:6]:
            is_done = run["status"] == "completed"
            icon_svg = get_svg_icon("check") if is_done else get_svg_icon("spinner")
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px;
                        font-size:0.78rem; color:#1e293b; margin:4px 0;
                        padding:6px 8px; background:#f1f5f9;
                        border-radius:8px;">
                {icon_svg}
                <span>#{run['id']} — {run['topic'][:22]}...</span>
            </div>
            """, unsafe_allow_html=True)


    else:
        st.caption("No runs yet — create your first content!")

    st.markdown("---")

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        {get_svg_icon("dollar")}
        <span style="font-weight:600; color:#1e293b; font-size:0.9rem;">Business Value</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
<small style="color:#475569;">
⏱️ Manual: ~8 hours/article<br>
⚡ ContentFlow: ~3 minutes<br>
💰 Save ~$320 per article
</small>
""", unsafe_allow_html=True)


# ============================================================================
# MAIN HEADER
# ============================================================================
st.markdown("""
<div class="header-banner">
    <div class="main-title">ContentFlow AI</div>
    <div class="subtitle">
        6‑Agent Content Pipeline &nbsp;·&nbsp; Powered by Groq &nbsp;·&nbsp;
        Professional Marketing Content in Minutes
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# TABS
# ============================================================================
tab1, tab2 = st.tabs(["▶  Create Content", "ℹ  Pipeline Info"])

# ── Helpers ──────────────────────────────────────────────────────────────────
AGENTS_META = [
    ("researcher", "Researcher",    "Research & Outline",   "#3b82f6"),
    ("writer",     "Writer",        "Draft Creation",       "#8b5cf6"),
    ("seo",        "SEO Optimizer", "Meta & Keywords",      "#10b981"),
    ("editor",     "Editor",        "Quality Control",      "#f59e0b"),
    ("chart",      "Chart Designer","Visual Data",          "#ef4444"),
    ("publisher",  "Publisher",     "HTML Export",          "#06b6d4"),
]

def render_agent_card(ph, icon_key, name, desc, state, extra=""):
    cls_map   = {"pending":"pending","running":"running","done":"done","error":"error"}
    cls       = cls_map.get(state, "pending")
    color_map = {
        "researcher":"#3b82f6","writer":"#8b5cf6","seo":"#10b981",
        "editor":"#f59e0b","chart":"#ef4444","publisher":"#06b6d4"
    }
    color     = color_map.get(icon_key, "#4f46e5")
    icon_html = get_svg_icon(icon_key, color)
    badge     = f'<span class="feedback-badge">{extra}</span>' if extra else ""
    ph.markdown(f"""
<div class="agent-card {cls}">
  <span class="agent-icon">{icon_html}</span>
  <div>
    <div class="agent-name">{name}{badge}</div>
    <div class="agent-status">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ============================================================================
# TAB 1 — CREATE CONTENT  (unchanged logic)
# ============================================================================
with tab1:
    col_left, col_right = st.columns([1.6, 1], gap="large")

    with col_left:
        st.markdown("#### What to Create?")
        topic = st.text_input(
            "Topic or Keyword",
            placeholder="e.g., How AI is transforming digital marketing in 2025",
            label_visibility="collapsed"
        )

        c1, c2 = st.columns(2)
        with c1:
            max_retries = st.slider(
                "Editor Retry Limit", 1, 3, 2,
                help="Max times Writer can revise if Editor rejects"
            )
        with c2:
            quality_threshold = st.slider(
                "Quality Threshold", 5, 9, 7,
                help="Min quality score (1–10) required to approve"
            )

        has_key = bool(
            os.getenv("GROQ_API_KEY") or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )
        run_btn = st.button(
            "▶  Run Pipeline",
            use_container_width=True,
            disabled=(not topic or not has_key)
        )
        if not has_key:
            st.warning("🔑 Enter at least one API key in the sidebar to begin.")

    with col_right:
        st.markdown("#### Agent Team")
        agent_placeholders = []
        for icon_key, name, desc, color in AGENTS_META:
            ph = st.empty()
            render_agent_card(ph, icon_key, name, desc, "pending")
            agent_placeholders.append((ph, icon_key, name, desc))

    if run_btn and topic:
        run_id = db.create_run(topic)

        with col_left:
            progress_bar = st.progress(0, text="Initialising pipeline…")
            status_text  = st.empty()
            log_expander = st.expander("📋 Activity Log", expanded=False)
            log_box      = log_expander.empty()
            logs         = []

        def add_log(msg):
            logs.append(f"• {msg}")
            log_box.markdown("\n".join(logs[-20:]))

        try:
            step = 0

            # ── Agent 1: Researcher ───────────────────────────────────────────
            ph, ik, nm, ds = agent_placeholders[0]
            render_agent_card(ph, ik, nm, ds, "running")
            status_text.info("🔍 Researcher: Analysing topic and gathering insights…")
            add_log("Researcher started")
            db.log_agent(run_id, "Researcher", "running")

            researcher = ResearcherAgent()
            research   = researcher.run(topic)

            db.log_agent(run_id, "Researcher", "completed", topic, research)
            db.save_version(run_id, "Researcher", str(research), 1)
            render_agent_card(ph, ik, nm, f"{len(research.get('keywords',[]))} keywords found", "done")
            add_log(f"Researcher done — {len(research.get('keywords',[]))} keywords")
            step += 1
            progress_bar.progress(step / 6, text="Researcher ✓")

            # ── Agents 2 + 4: Writer ↔ Editor feedback loop ──────────────────
            writer   = WriterAgent()
            editor   = EditorAgent()
            feedback = ""
            iteration = 0
            approved  = False
            draft     = ""
            edit_result = {}

            while not approved and iteration < max_retries:
                iteration += 1

                ph, ik, nm, ds = agent_placeholders[1]
                iter_lbl = f"v{iteration}" if iteration > 1 else ""
                render_agent_card(ph, ik, nm, ds, "running", iter_lbl)
                status_text.info(f"✍️ Writer: Drafting content (attempt {iteration})…")
                add_log(f"Writer started — attempt {iteration}")
                db.log_agent(run_id, "Writer", "running",
                             {"research": str(research), "feedback": feedback})

                draft = writer.run(research, feedback)
                db.log_agent(run_id, "Writer", "completed", None,
                             {"length": len(draft)}, iterations=iteration)
                db.save_version(run_id, "Writer", draft, iteration)
                render_agent_card(ph, ik, nm, f"{len(draft.split())} words", "done", iter_lbl)
                add_log(f"Writer done — {len(draft.split())} words")

                ph, ik, nm, ds = agent_placeholders[3]
                render_agent_card(ph, ik, nm, ds, "running")
                status_text.info(f"✅ Editor: Reviewing quality (attempt {iteration})…")
                add_log(f"Editor reviewing — attempt {iteration}")
                db.log_agent(run_id, "Editor", "running")

                edit_result = editor.run(draft, research)
                score       = edit_result["score"]
                approved    = edit_result["approved"] or score >= quality_threshold
                feedback    = edit_result["feedback"]
                draft       = edit_result["polished_content"]

                db.log_agent(run_id, "Editor", "completed", None,
                             edit_result, iterations=iteration)
                db.save_version(run_id, "Editor", draft, iteration)

                render_agent_card(
                    ph, ik, nm,
                    f"Score {score}/10",
                    "done" if approved else "error"
                )
                add_log(f"Editor: {score}/10 — {'Approved ✓' if approved else 'Retry requested'}")

                if not approved and iteration < max_retries:
                    status_text.warning(
                        f"⚠️ Quality {score}/10 below threshold {quality_threshold}/10. "
                        f"Writer revising…"
                    )
                    time.sleep(0.8)

            step += 2
            progress_bar.progress(step / 6, text="Writer + Editor ✓")

            # ── Agent 3: SEO Optimizer ────────────────────────────────────────
            ph, ik, nm, ds = agent_placeholders[2]
            render_agent_card(ph, ik, nm, ds, "running")
            status_text.info("📈 SEO Optimizer: Adding meta tags and keywords…")
            add_log("SEO Optimizer started")
            db.log_agent(run_id, "SEO Optimizer", "running")

            seo_agent = SEOOptimizerAgent()
            seo_data  = seo_agent.run(draft, research)

            db.log_agent(run_id, "SEO Optimizer", "completed", None, {
                "meta_title":       seo_data.get("meta_title"),
                "meta_description": seo_data.get("meta_description"),
            })
            render_agent_card(ph, ik, nm, "Meta tags optimised", "done")
            add_log("SEO Optimizer done")
            step += 1
            progress_bar.progress(step / 6, text="SEO Optimizer ✓")

            # ── Agent 5: Chart Designer ───────────────────────────────────────
            ph, ik, nm, ds = agent_placeholders[4]
            render_agent_card(ph, ik, nm, ds, "running")
            status_text.info("📊 Chart Designer: Creating data visualisations…")
            add_log("Chart Designer started")
            db.log_agent(run_id, "Chart Designer", "running")

            from agents.chart_designer import ChartDesignerAgent
            chart_agent = ChartDesignerAgent()
            visual_data = chart_agent.run(research)

            db.log_agent(run_id, "Chart Designer", "completed", None,
                         {"chart_count": visual_data.get("charts_count", 0)})
            render_agent_card(
                ph, ik, nm,
                f"{visual_data.get('charts_count', 0)} charts created",
                "done"
            )
            add_log(f"Chart Designer done — {visual_data.get('charts_count', 0)} charts")
            step += 1
            progress_bar.progress(step / 6, text="Chart Designer ✓")

            # ── Agent 6: Publisher ────────────────────────────────────────────
            ph, ik, nm, ds = agent_placeholders[5]
            render_agent_card(ph, ik, nm, ds, "running")
            status_text.info("🚀 Publisher: Assembling final output…")
            add_log("Publisher started")
            db.log_agent(run_id, "Publisher", "running")

            publisher  = PublisherAgent()
            pub_result = publisher.run(seo_data, visual_data, research, run_id)

            db.log_agent(run_id, "Publisher", "completed", None,
                         {"filename": pub_result["filename"]})
            db.complete_run(run_id, pub_result["html"], {
                "meta_title": seo_data.get("meta_title"),
                "word_count": len(draft.split()),
                "editor_score": edit_result.get("score", 0),
                "iterations":  iteration,
            })
            render_agent_card(ph, ik, nm, "HTML ready", "done")
            add_log("Publisher done — HTML assembled")
            step += 1
            progress_bar.progress(6 / 6, text="Pipeline complete! ✓")

            status_text.success("🎉 Pipeline complete! Your content is ready.")
            time.sleep(0.4)

            # ── Metrics ───────────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 📊 Performance Summary")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">{len(draft.split())}</div>'
                    f'<div class="metric-label">WORDS</div></div>',
                    unsafe_allow_html=True
                )
            with m2:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">{edit_result.get("score","—")}/10</div>'
                    f'<div class="metric-label">QUALITY</div></div>',
                    unsafe_allow_html=True
                )
            with m3:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">{iteration}</div>'
                    f'<div class="metric-label">ITERATIONS</div></div>',
                    unsafe_allow_html=True
                )
            with m4:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="metric-val">~3m</div>'
                    f'<div class="metric-label">TIME SAVED</div></div>',
                    unsafe_allow_html=True
                )

            # ── Content preview ───────────────────────────────────────────────
            st.markdown("---")
            st.markdown("#### 👁 Content Preview")
            with st.expander("Preview Final Article", expanded=True):
                st.components.v1.html(pub_result["html"], height=500, scrolling=True)

            # ── SEO details ───────────────────────────────────────────────────
            st.markdown("#### 🔍 SEO Details")
            seo_c1, seo_c2 = st.columns(2)
            with seo_c1:
                st.info(f"**Meta Title:**\n\n{seo_data.get('meta_title', '—')}")
            with seo_c2:
                st.info(f"**Meta Description:**\n\n{seo_data.get('meta_description', '—')}")

            # ── Downloads ─────────────────────────────────────────────────────
            st.markdown("#### ⬇️ Download Options")
            dl1, dl2, dl3 = st.columns(3)

            with dl1:
                st.download_button(
                    label="📄 Download HTML",
                    data=pub_result["html"].encode("utf-8"),
                    file_name=pub_result["filename"],
                    mime="text/html",
                    use_container_width=True,
                )
                st.markdown(
                    '<p class="download-caption">Full article with styling</p>',
                    unsafe_allow_html=True
                )

            with dl2:
                st.download_button(
                    label="📝 Download Draft",
                    data=draft.encode("utf-8"),
                    file_name=f"draft_{run_id}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
                st.markdown(
                    '<p class="download-caption">Plain text draft</p>',
                    unsafe_allow_html=True
                )

            with dl3:
                meta_title = seo_data.get("meta_title", topic)
                pdf_bytes  = generate_pdf(draft, title=meta_title)
                st.download_button(
                    label="🖨️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"article_{run_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.markdown(
                    '<p class="download-caption">Print-ready PDF</p>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            status_text.error(f"❌ Pipeline error: {e}")
            st.exception(e)
            db.log_agent(run_id, "System", "error", None, {"error": str(e)})


# ============================================================================
# TAB 2 — PIPELINE INFO
# ============================================================================
with tab2:
    st.markdown("### How It Works")
    st.markdown("""
| # | Agent | Role | Technology |
|---|-------|------|------------|
| 1 | **Researcher** | Topic analysis, keyword research, outline | Groq LLM + SerpAPI |
| 2 | **Writer** | Full blog draft creation | Groq Llama 3.3 |
| 3 | **SEO Optimizer** | Meta tags, keywords, internal links | Groq LLM |
| 4 | **Editor** | Quality scoring + feedback loop | Groq LLM |
| 5 | **Chart Designer** | Data visualisation (matplotlib) | Python (free) |
| 6 | **Publisher** | HTML assembly + PDF export | Native Python |
""")

    st.markdown("---")
    st.markdown("### 💰 Business Value Calculator")
    articles_per_month = st.slider("Articles per month", 1, 50, 10)
    manual_cost = articles_per_month * 8 * 40
    ai_cost     = articles_per_month * 0.02
    saved       = manual_cost - ai_cost
    st.markdown(f"""
| Metric | Manual | ContentFlow AI |
|--------|--------|----------------|
| Time per article | 8 hours | ~3 minutes |
| Cost per article | $320 | ~$0.02 |
| **Monthly ({articles_per_month} articles)** | **${manual_cost:,.0f}** | **${ai_cost:.2f}** |
| **Monthly savings** | — | **${saved:,.0f}** |
""")
    st.success(f"💰 You save **${saved:,.0f} per month** with ContentFlow AI!")

    st.markdown("---")
    st.markdown("### 🗄 Database Schema")
    st.code("""
pipeline_runs    → id, topic, status, timestamps, final_content, metadata
agent_logs       → id, run_id, agent_name, status, input_data, output_data
content_versions → id, run_id, version, agent_name, content
""", language="sql")

    st.markdown("---")
    st.markdown("### ✅ Requirements Fulfilled")
    st.markdown("""
| Requirement | Implementation |
|-------------|----------------|
| LLM Integration | Groq (Llama 3.3 70B) / Gemini / OpenAI |
| SQLite Database | 3 tables with full run logging |
| External APIs | SerpAPI + optional WordPress REST API |
| 6 Agents | Complete multi-agent pipeline |
| Feedback Loop | Editor → Writer with configurable retries |
| Real-time UI | Live agent status cards + progress bar |
| Downloads | HTML ✓ · Plain Text ✓ · PDF ✓ |
| Deployable | Streamlit Cloud ready |
""")