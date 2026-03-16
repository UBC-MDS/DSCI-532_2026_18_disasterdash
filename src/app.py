"""
Disaster Dash (v3) — AI Explorer Tab Added
Global Disaster Impact & Humanitarian Aid (2018–2024)
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
from pathlib import Path
import pandas as pd
from datetime import datetime
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from querychat import QueryChat
import io
import ibis

# Load .env from project root (parent of src/)
# override=True ensures python-dotenv's quote-stripped value beats VS Code's raw injection
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=True)
except ImportError:
    pass

# ── Lazy Load Data with DuckDB────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "global_disaster_response_2018_2024.parquet"
con = ibis.duckdb.connect() 
disaster_table = con.read_parquet(DATA_PATH)
df = disaster_table.execute()   # only for QueryChat and Header Stats

# ── Country → ISO-3 ────────────────────────────────────────────────────────────
ISO3 = {
    "Australia": "AUS", "Bangladesh": "BGD", "Brazil": "BRA",
    "Canada": "CAN",    "Chile": "CHL",       "China": "CHN",
    "France": "FRA",    "Germany": "DEU",     "Greece": "GRC",
    "India": "IND",     "Indonesia": "IDN",   "Italy": "ITA",
    "Japan": "JPN",     "Mexico": "MEX",      "Nigeria": "NGA",
    "Philippines": "PHL", "South Africa": "ZAF", "Spain": "ESP",
    "Turkey": "TUR",    "United States": "USA",
}
# ── GDP (Current USD, 2024 World Bank) ─────────────────────────────
GDP = {
    "Australia": 1757022451652.83,
    "Bangladesh": 450119432068.852,
    "Brazil": 2185821648943.86,
    "Canada": 2243636826633.76,
    "Chile": 330267137371.592,
    "China": 18743803170827.2,
    "Germany": 4685592577804.69,
    "Spain": 1725671652742.19,
    "France": 3160442622465.08,
    "Greece": 256238371778.118,
    "Indonesia": 1396300098190.97,
    "India": 3909891533858.08,
    "Italy": 2380825077243.59,
    "Japan": 4027597523550.58,
    "Mexico": 1856365616165.94,
    "Nigeria": 252261880141.151,
    "Philippines": 461617509782.355,
    "United States": 28750956130731.2,
    "South Africa": 401144998373.585,
}
# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_currency(v):
    s = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:  return f"{s}${v/1e12:.2f}T"
    if v >= 1e9:   return f"{s}${v/1e9:.1f}B"
    if v >= 1e6:   return f"{s}${v/1e6:.1f}M"
    if v >= 1e3:   return f"{s}${v/1e3:.1f}K"
    return f"{s}${v:.0f}"

def fmt_num(v):
    if v >= 1e6:  return f"{v/1e6:.1f}M"
    if v >= 1e3:  return f"{v/1e3:.1f}K"
    return f"{v:,.0f}"


def normalize_sql(query: str) -> str:
    return query.strip().rstrip(";").strip()


SQL_MUTATION_PATTERN = re.compile(
    r"\b(drop|delete|truncate|insert|update|alter|create|replace|merge|grant|revoke)\b",
    flags=re.IGNORECASE,
)


def is_read_only_sql(query: str) -> bool:
    q = normalize_sql(query)
    if not q:
        return False
    if ";" in q:
        return False
    if SQL_MUTATION_PATTERN.search(q):
        return False
    q_lower = q.lower()
    return q_lower.startswith("select") or q_lower.startswith("with")


def is_count_intent(intent: str, query: str) -> bool:
    text = f"{intent} {query}".lower()
    count_terms = ("how many", "count", "number of", "total events", "total disasters")
    return any(term in text for term in count_terms)


def force_count_query(query: str) -> str:
    q = normalize_sql(query)
    if "count(" in q.lower():
        return q
    return f"SELECT COUNT(*) AS n FROM ({q}) AS count_subquery"

# ── Constants ──────────────────────────────────────────────────────────────────
COUNTRIES      = sorted(ISO3.keys())
DISASTER_TYPES = [
    "Drought", "Earthquake", "Extreme Heat", "Flood", "Hurricane",
    "Landslide", "Storm Surge", "Tornado", "Volcanic Eruption", "Wildfire",
]
SUMMARY_CHOICES = {
    "mean": "Average",
    "sum":  "Total Sum",
    "min":  "Minimum",
    "max":  "Maximum",
}
AI_STYLE_CHOICES = {
    "concise": "Concise Analyst",
    "policy_brief": "Policy Brief",
    "step_by_step": "Step-by-Step",
}
AI_STYLE_INSTRUCTIONS = {
    "concise": (
        "Write compact answers in 3 to 5 bullet points. Lead with the key result, "
        "then include one short interpretation line."
    ),
    "policy_brief": (
        "Write a policy brief style answer with sections: Finding, Policy Implication, "
        "Recommended Action. Keep each section short and evidence-based."
    ),
    "step_by_step": (
        "Explain the result step by step: filters applied, metric computed, and result "
        "interpretation. Keep steps explicit and numbered."
    ),
}
MAP_METRICS = {
    "disasters":    "Disaster Frequency",
    "coverage_pct": "Aid Coverage (%)",
    "total_loss":   "Economic Loss (USD)",
    "casualties":   "Total Casualties",
}
QUESTION_MAP = {
    "total_loss": "Where are disasters causing the highest economic losses?",
    "coverage_pct": "Where are disaster losses least covered by aid?",
    "disasters": "Where are disasters occurring most frequently?",
    "casualties": "Where are disasters causing the greatest loss of life?",
}
LAST_UPDATED = datetime.today().strftime("%B %d, %Y")
DATASET_COLUMNS = [str(c) for c in df.columns]
DATASET_COLUMNS_TEXT = ", ".join(DATASET_COLUMNS)


def style_prompt_suffix(style_key: str) -> str:
    rule = AI_STYLE_INSTRUCTIONS.get(style_key, AI_STYLE_INSTRUCTIONS["concise"])
    return f"\n\nResponse style override for this session:\n{rule}"

# ── QueryChat Config ───────────────────────────────────────────────────────────
# Uses Anthropic Claude (Haiku) for natural language dataframe queries
# Requires ANTHROPIC_API_KEY set locally (via .env) or in Posit Connect secrets

import chatlas, os as _os, sys as _sys
from dotenv import load_dotenv as _load_dotenv
_load_dotenv()  # loads .env from the working directory if present

_anthropic_key = _os.getenv("ANTHROPIC_API_KEY")
if not _anthropic_key:
    print(
        "\n❌  ANTHROPIC_API_KEY is not set.\n"
        "   Add it to a .env file in the project root or Posit Connect secrets.\n",
        file=_sys.stderr,
    )
    _sys.exit(1)

AI_EXTRA_INSTRUCTIONS = f"""
You are the Disaster Dash AI assistant for policy analysts studying disaster aid gaps.

Dataset context:
- Table name: global_disaster_response_2018_2024
- Date coverage: 2018-01-01 to 2024-12-31
- Available columns: {DATASET_COLUMNS_TEXT}

User goal context:
- Help users identify underfunded disaster responses.
- Prioritize reliable, dataset-grounded evidence over generic claims.

Tool usage rules:
1) If the user asks for counts, totals, averages, rankings, percentages, or any numeric claim, run querychat_query before answering.
2) If the user asks to filter or show a subset in dashboard visuals, run querychat_update_dashboard using a SELECT or WITH query.
3) For requests that need both a numeric answer and dashboard filtering, run querychat_query first, then querychat_update_dashboard.
4) Never provide invented numbers. If no tool result is available, say that and request clarification.

SQL safety rules:
- Use only SELECT or WITH statements.
- Keep queries read-only.
- Use only the known table and columns.

Answer quality rules:
- State the filters applied.
- If query result is empty, explicitly say no rows matched and suggest broader filters.
- Keep reasoning concise and tied to returned results.
"""

AI_GREETING = """Hi! I am your Disaster Dash AI assistant.

Ask for filtered slices, counts, rankings, and comparisons. I will run dataset queries and then update the table and charts below.

Try these examples:
- "How many flood events occurred in India after 2020?"
- "Show only earthquakes in Japan between 2021 and 2023."
- "Which 5 countries had the highest total economic loss in 2024?"
- "Filter events where casualties are greater than 1000 and aid is below 10 million USD."
- "Compare total aid amount for floods vs hurricanes since 2019."
- "What is the average response time for wildfires in Australia?"
- "List countries where aid coverage is below 30 percent."
- "Show disasters in Bangladesh in 2022 and summarize total loss and aid."
"""

qc = QueryChat(
    df,
    "global_disaster_response_2018_2024",
    client=chatlas.ChatAnthropic(model="claude-3-haiku-20240307", api_key=_anthropic_key),
    extra_instructions=AI_EXTRA_INSTRUCTIONS,
    greeting=AI_GREETING,
)
QC_BASE_SYSTEM_PROMPT = qc.system_prompt

# ── Design Tokens ──────────────────────────────────────────────────────────────
NAVY    = "#0b1f3a"
BLUE    = "#1a56db"
AMBER   = "#f59e0b"
GREEN   = "#059669"
RED     = "#dc2626"
BG      = "#eef2f7"
CARD    = "#ffffff"
BORDER  = "#dde4ee"
T_PRI   = "#0f172a"
T_SEC   = "#64748b"
T_MUTED = "#94a3b8"

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Instrument+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .bslib-page-fill {{
    font-family: 'Instrument Sans', system-ui, sans-serif !important;
    background: {BG} !important;
    color: {T_PRI};
    font-size: 14px;
}}

/* ── PAGE HEADER ── */
#page-header {{
    background: linear-gradient(135deg, {NAVY} 0%, #0d2d54 50%, #103468 100%);
    padding: 18px 28px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    position: relative;
    overflow: hidden;
}}
#page-header::before {{
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 600px 300px at 80% 50%, rgba(26,86,219,0.18) 0%, transparent 70%);
    pointer-events: none;
}}
#page-header .brand {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
#page-header .logo {{
    width: 42px; height: 42px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    flex-shrink: 0;
}}
#page-header h1 {{
    font-family: 'Arial Black', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.5px;
    line-height: 1.1;
}}
#page-header .tagline {{
    font-size: 0.72rem;
    color: rgba(255,255,255,0.55);
    font-weight: 500;
    letter-spacing: 0.3px;
    margin-top: 2px;
}}
#page-header .header-meta {{
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}}
.header-stat {{
    text-align: right;
    color: rgba(255,255,255,0.9);
}}
.header-stat .hs-val {{
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1;
    color: #fff;
}}
.header-stat .hs-lbl {{
    font-size: 0.62rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 2px;
    font-weight: 600;
}}

/* ── SIDEBAR ── */
.bslib-sidebar-layout > .sidebar {{
    background: {CARD} !important;
    border-right: 1px solid {BORDER} !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.06);
    overflow-y: auto;
    padding: 0 !important;
}}
.bslib-sidebar-layout > .sidebar > .sidebar-content {{
    padding: 0 !important;
}}

.sb-section {{
    padding: 16px 14px 0 14px;
}}
.ai-sidebar-note {{
    margin-top: 7px;
    font-size: 0.69rem;
    line-height: 1.35;
    color: {T_SEC};
}}
.sb-label {{
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    color: {T_MUTED};
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.sb-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {BORDER};
}}

/* Inputs */
.selectize-control.multi .selectize-input,
.input-daterange .form-control,
.form-select, select.form-control {{
    background: {BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {T_PRI} !important;
    font-size: 0.78rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    padding: 6px 9px !important;
    min-height: 34px;
    box-shadow: none !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}}
.selectize-control.multi .selectize-input.focus,
.input-daterange .form-control:focus,
.form-select:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
    outline: none !important;
    background: #fff !important;
}}
.selectize-dropdown {{
    background: #fff !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 0.79rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.13) !important;
    color: {T_PRI} !important;
    z-index: 9999 !important;
}}
.selectize-dropdown .option:hover,
.selectize-dropdown .option.active {{
    background: rgba(26,86,219,0.07) !important;
    color: {BLUE} !important;
}}
.selectize-input .item {{
    background: {NAVY} !important;
    color: #fff !important;
    border-radius: 5px !important;
    font-size: 0.67rem !important;
    padding: 2px 6px !important;
    border: none !important;
    white-space: nowrap;
    font-weight: 500;
}}
.selectize-input .item .remove {{
    color: rgba(255,255,255,0.6) !important;
    border-left: 1px solid rgba(255,255,255,0.2) !important;
    padding-left: 4px !important;
    margin-left: 3px !important;
}}
.selectize-control.multi .selectize-input {{
    max-height: 72px;
    overflow-y: auto;
}}

/* Quick-pick buttons */
.sb-btns {{
    display: flex;
    gap: 6px;
    margin-top: 5px;
}}
.sb-btns .action-button {{
    flex: 1;
    background: {BG} !important;
    color: {T_SEC} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-size: 0.67rem !important;
    font-weight: 600 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    padding: 4px 6px !important;
    transition: all 0.15s;
}}
.sb-btns .action-button:hover {{
    background: {NAVY} !important;
    color: #fff !important;
    border-color: {NAVY} !important;
}}
#reset_button {{
    display: block;
    width: calc(100% - 28px);
    margin: 10px 14px 14px !important;
    background: #fff5f5 !important;
    color: {RED} !important;
    border: 1px solid #fee2e2 !important;
    border-radius: 8px !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    padding: 8px !important;
    transition: all 0.2s;
}}
#reset_button:hover {{
    background: {RED} !important;
    color: #fff !important;
    border-color: {RED} !important;
    box-shadow: 0 4px 14px rgba(220,38,38,0.28);
    transform: translateY(-1px);
}}

/* Active filter pill strip */
#filter-strip {{
    background: {CARD};
    border-bottom: 1px solid {BORDER};
    padding: 7px 16px 7px 48px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    font-size: 0.7rem;
}}
.fp-label {{
    color: {T_MUTED};
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    font-size: 0.62rem;
}}
.fp-pill {{
    background: rgba(11,31,58,0.07);
    color: {NAVY};
    border: 1px solid rgba(11,31,58,0.15);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.68rem;
    font-weight: 600;
}}
.fp-sep {{ color: {BORDER}; font-size: 1rem; }}

/* AI helper copy */
.ai-instructions {{
    border: 1px solid {BORDER};
    background: #f8fbff;
    border-radius: 10px;
    padding: 10px 12px;
    margin: 8px 12px 10px;
    font-size: 0.74rem;
    line-height: 1.35;
    color: {T_SEC};
}}
.ai-instructions .ai-expand-note {{
    display: block;
    margin-bottom: 6px;
    padding: 6px 8px;
    border: 1px solid #f0d9a7;
    background: #fff8ea;
    border-radius: 8px;
    color: #7a5a1c;
    font-weight: 600;
}}
.ai-instructions .ai-title {{
    display: block;
    font-weight: 700;
    color: {T_PRI};
    margin-bottom: 4px;
}}
.ai-instructions ul {{
    margin: 6px 0 0 14px;
    padding: 0;
}}
.ai-instructions li {{
    margin: 2px 0;
}}
.ai-query-status {{
    border: 1px dashed {BORDER};
    background: #ffffff;
    border-radius: 8px;
    padding: 8px 10px;
    margin: 0 12px 10px;
    font-size: 0.72rem;
    line-height: 1.35;
    color: {T_SEC};
}}
.ai-query-status strong {{
    color: {T_PRI};
}}

/* ── Prompt suggestion chips ── */
.prompt-chips-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 0 12px 10px;
}}
.prompt-chip {{
    background: #eef4ff;
    border: 1px solid #b8d0f7;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.71rem;
    color: #2d5fa6;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    white-space: nowrap;
}}
.prompt-chip:hover {{
    background: #d4e6ff;
    border-color: #5b97e8;
}}

/* ── CARDS ── */
.card {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    overflow: hidden;
}}
.card-header {{
    background: #fff !important;
    border-bottom: 1px solid {BORDER} !important;
    color: {T_SEC} !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 8px 16px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    display: flex;
    align-items: center;
    gap: 7px;
}}

/* ── KPI CARDS ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 12px;
    height: 100%;
}}
.kpi-box {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 18px 16px 14px;

    display: flex;
    flex-direction: column;
    align-items: center;

    justify-content: space-evenly;   /* ⭐ the trick */

    text-align: center;
}}
.kpi-subtitle {{
    font-size: 0.8rem;
    color: #475569;
}}
.kpi-box:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important;
}}

.kpi-icon {{
    font-size: 1.4rem;
    margin-bottom: 8px;
    line-height: 1;
}}
.kpi-value {{
    font-family: inherit !important;
    font-size: 2.1rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin: 6px 0 4px 0;
}}
.kpi-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
}}
.kpi-formula {{
    font-size: 0.68rem;
    color: #94a3b8;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    letter-spacing: 0.3px;
}}
/* ── TABS ── */
.nav-underline {{
    border-bottom: 2px solid {BORDER} !important;
    padding: 0 4px;
    gap: 4px;
    background: transparent;
}}
.nav-underline .nav-item .nav-link {{
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: {T_SEC} !important;
    padding: 10px 18px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px;
    border-radius: 0 !important;
    transition: color 0.15s, border-color 0.15s;
    background: transparent !important;
}}
.nav-underline .nav-item .nav-link:hover {{
    color: {NAVY} !important;
    border-bottom-color: {BORDER} !important;
}}
.nav-underline .nav-item .nav-link.active {{
    color: {NAVY} !important;
    border-bottom: 2px solid {BLUE} !important;
    background: transparent !important;
}}
.tab-content {{ padding-top: 14px !important; }}

/* ── DOWNLOAD BUTTON ── */
#download_ai_csv {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {BLUE} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    padding: 7px 14px !important;
    margin: 10px 14px 8px !important;
    transition: all 0.18s;
    cursor: pointer;
}}
#download_ai_csv:hover {{
    background: {NAVY} !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(26,86,219,0.28);
}}

/* ── EMPTY STATE ── */
.empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 200px;
    color: {T_SEC};
    text-align: center;
    padding: 28px;
    gap: 8px;
}}
.empty-state .es-icon {{ font-size: 2.6rem; opacity: 0.3; }}
.empty-state .es-msg  {{ font-weight: 700; font-size: 0.9rem; color: {T_PRI}; }}
.empty-state .es-hint {{ font-size: 0.75rem; color: {T_MUTED}; }}

/* ── MAIN AREA ── */
.bslib-sidebar-layout > .main {{
    background: {BG} !important;
    padding: 0 !important;
    overflow-y: auto;
}}
.main-inner {{
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}

/* ── FOOTER ── */
#dash-footer {{
    text-align: center;
    color: {T_MUTED};
    font-size: 0.7rem;
    padding: 10px;
    border-top: 1px solid {BORDER};
    background: {CARD};
    font-family: 'Instrument Sans', sans-serif;
}}
#dash-footer a {{ color: {BLUE}; text-decoration: none; font-weight: 600; }}
#dash-footer a:hover {{ text-decoration: underline; }}

/* Visually-hidden labels for accessibility */
label {{
    position: absolute !important;
    width: 1px !important; height: 1px !important;
    padding: 0 !important; margin: -1px !important;
    overflow: hidden !important; clip: rect(0,0,0,0) !important;
    white-space: nowrap !important; border: 0 !important;
}}
"""

# ── UI ─────────────────────────────────────────────────────────────────────────
app_ui = ui.page_fillable(
    ui.tags.head(
        ui.tags.style(CSS),
        ui.tags.script("""
(function() {
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.prompt-chip');
    if (!btn) return;
    var prompt = btn.getAttribute('data-prompt');
    if (!prompt) return;
    // shiny-chat-input renders into itself (no shadow DOM) and exposes setInputValue()
    var chatInput = document.querySelector('shiny-chat-input');
    if (!chatInput) return;
    if (typeof chatInput.setInputValue === 'function') {
      chatInput.setInputValue(prompt, {submit: true});
    } else {
      var ta = chatInput.querySelector('textarea');
      if (!ta) return;
      ta.value = prompt;
      ta.dispatchEvent(new Event('input', {bubbles: true}));
      ta.dispatchEvent(new Event('change', {bubbles: true}));
      ta.focus();
    }
  });
})();
"""),
    ),

    # ── Page Header ────────────────────────────────────────────────────────────
    ui.div(
        ui.div(
            ui.div("🌍", class_="logo"),
            ui.div(
                ui.h1("Disaster Dash"),
                ui.div("Global Disaster Impact & Humanitarian Aid  ·  2018 – 2024", class_="tagline"),
            ),
            class_="brand",
        ),
        ui.div(
            ui.div(
                ui.div(f"{len(df):,}", class_="hs-val"),
                ui.div("Total Records", class_="hs-lbl"),
                class_="header-stat",
            ),
            ui.div(
                ui.div(f"{len(COUNTRIES)}", class_="hs-val"),
                ui.div("Countries", class_="hs-lbl"),
                class_="header-stat",
            ),
            ui.div(
                ui.div(f"{len(DISASTER_TYPES)}", class_="hs-val"),
                ui.div("Disaster Types", class_="hs-lbl"),
                class_="header-stat",
            ),
            class_="header-meta",
        ),
        id="page-header",
    ),

    ui.layout_sidebar(

        # ── Sidebar ────────────────────────────────────────────────────────────
        ui.sidebar(

            ui.panel_conditional(
                "input.main_tabs === 'overview'",
                ui.div(
                    ui.div("Country", class_="sb-label"),
                    ui.input_selectize(
                        "countries", label=None,
                        choices={"_all_": "— All Countries —"} | {c: c for c in COUNTRIES},
                        selected=["Brazil", "Bangladesh", "South Africa"], multiple=True,
                        options={"placeholder": "Select countries…", "plugins": ["remove_button"], "closeAfterSelect": False},
                    ),
                    ui.div(
                        ui.input_action_button("sel_all_c",   "✓ All",  width="50%"),
                        ui.input_action_button("desel_all_c", "✕ None", width="50%"),
                        class_="sb-btns",
                    ),
                    class_="sb-section",
                ),
                ui.div(
                    ui.div("Disaster Type", class_="sb-label"),
                    ui.input_selectize(
                        "disaster_type", label=None,
                        choices={"_all_": "— All Types —"} | {d: d for d in DISASTER_TYPES},
                        selected=DISASTER_TYPES, multiple=True,
                        options={"placeholder": "Select types…", "plugins": ["remove_button"], "closeAfterSelect": False},
                    ),
                    ui.div(
                        ui.input_action_button("sel_all_d",   "✓ All",  width="50%"),
                        ui.input_action_button("desel_all_d", "✕ None", width="50%"),
                        class_="sb-btns",
                    ),
                    class_="sb-section",
                ),
                ui.div(
                    ui.div("Date Range", class_="sb-label"),
                    ui.input_date_range(
                        "date_range", label=None,
                        start="2018-01-01", end="2024-12-31",
                        min="2018-01-01",   max="2024-12-31",
                    ),
                    class_="sb-section",
                ),
                ui.div(
                    ui.div("Map Metric", class_="sb-label"),
                    ui.input_select(
                        "map_metric", label=None,
                        choices=MAP_METRICS, selected="total_loss",
                    ),
                    class_="sb-section",
                ),
                ui.div(
                    ui.div("Bar Chart Statistic", class_="sb-label"),
                    ui.input_select(
                        "summary_stat", label=None,
                        choices=SUMMARY_CHOICES, selected="sum",
                    ),
                    class_="sb-section",
                ),
                ui.input_action_button("reset_button", "↺  Reset All Filters"),
            ),

            ui.panel_conditional(
                "input.main_tabs === 'ai_explorer'",
                ui.div(
                    ui.div("AI Response Style", class_="sb-label"),
                    ui.input_select(
                        "ai_response_style",
                        label=None,
                        choices=AI_STYLE_CHOICES,
                        selected="concise",
                    ),
                    ui.div(
                        "Choose how the assistant writes answers. This changes style, not the underlying data query.",
                        class_="ai-sidebar-note",
                    ),
                    class_="sb-section",
                ),
            ),

            width=236,
            open="desktop",
        ),

        # ── Main Content ───────────────────────────────────────────────────────
        ui.div(
            # Active filter strip
            ui.panel_conditional(
                "input.main_tabs === 'overview'",
                ui.div(ui.output_ui("filter_strip"), id="filter-strip"),
            ),

            ui.navset_underline(

                # ── Tab 1: Overview ──────────────────────────────────────────
                ui.nav_panel(
                    "📊  Overview",
                    ui.div(

                        # Row 1: Map + KPIs
                        ui.layout_columns(
                            ui.card(
                                ui.card_header(ui.output_ui("map_title")),
                                output_widget("map_plot"),
                                full_screen=True,
                            ),
                            ui.output_ui("kpi_grid"),
                            col_widths=[8, 4],
                            style="height:400px; gap:14px;",
                        ),

                        # Row 2: Loss + Aid bar charts
                        ui.layout_columns(
                            ui.card(
                                ui.card_header("📉  Economic Loss by Disaster Type"),
                                output_widget("bar_loss"),
                                full_screen=True,
                            ),
                            ui.card(
                                ui.card_header("💰  Aid Amount by Disaster Type"),
                                output_widget("bar_aid"),
                                full_screen=True,
                            ),
                            col_widths=[6, 6],
                            style="height:330px; gap:14px;",
                        ),

                        class_="main-inner",
                    ),
                    value="overview",
                ),

                # ── Tab 2: AI Explorer ───────────────────────────────────────
                ui.nav_panel(
                    "🤖  AI Explorer",
                    ui.div(

                        # Row 1: Chat + Data Table
                        ui.layout_columns(
                            ui.card(
                                ui.card_header("💬  Ask a Question About the Data"),
                                ui.output_ui("ai_instructions"),
                                ui.output_ui("prompt_chips"),
                                ui.output_ui("ai_query_status"),
                                ui.div(
                                    qc.ui(id="chat", height="100%", fill=True),
                                    style="flex:1; min-height:0;",
                                ),
                                full_screen=True,
                                style="display:flex; flex-direction:column; height:100%;",
                            ),
                            ui.card(
                                ui.card_header("📋  Filtered Results"),
                                ui.output_data_frame("ai_table"),
                                ui.download_button(
                                    "download_ai_csv",
                                    "⬇  Download CSV",
                                ),
                                full_screen=True,
                            ),
                            col_widths=[5, 7],
                            style="height:600px; gap:14px;",
                        ),

                        # Row 2: Two charts driven by AI-filtered data
                        ui.layout_columns(
                            ui.card(
                                ui.card_header("📉  Economic Loss by Disaster Type (AI Filtered)"),
                                output_widget("ai_bar_loss"),
                                full_screen=True,
                            ),
                            ui.card(
                                ui.card_header("💰  Aid Amount by Disaster Type (AI Filtered)"),
                                output_widget("ai_bar_aid"),
                                full_screen=True,
                            ),
                            col_widths=[6, 6],
                            style="height:330px; gap:14px;",
                        ),

                        class_="main-inner",
                    ),
                    value="ai_explorer",
                ),

                id="main_tabs",
            ),

            # Footer
            ui.div(
                ui.span("Disaster Dash (v3)  ·  "),
                ui.span("Ojasv Issar, Joel Nicholas Peterson, Claire Saunders  ·  "),
                ui.a("GitHub", href="https://github.com/UBC-MDS/DSCI-532_2026_18_disasterdash", target="_blank"),
                ui.span(f"  ·  Data through {LAST_UPDATED}"),
                id="dash-footer",
            ),
        ),
    ),
)


# ── Server ─────────────────────────────────────────────────────────────────────
def server(input, output, session):

    # ── Sidebar quick-pick handlers ───────────────────────────────────────────
    @reactive.effect
    def _handle_all_c():
        if "_all_" in list(input.countries()):
            ui.update_selectize("countries", selected=COUNTRIES, session=session)

    @reactive.effect
    def _handle_all_d():
        if "_all_" in list(input.disaster_type()):
            ui.update_selectize("disaster_type", selected=DISASTER_TYPES, session=session)

    @reactive.effect
    @reactive.event(input.sel_all_c)
    def _(): ui.update_selectize("countries",     selected=COUNTRIES,      session=session)

    @reactive.effect
    @reactive.event(input.desel_all_c)
    def _(): ui.update_selectize("countries",     selected=[],             session=session)

    @reactive.effect
    @reactive.event(input.sel_all_d)
    def _(): ui.update_selectize("disaster_type", selected=DISASTER_TYPES, session=session)

    @reactive.effect
    @reactive.event(input.desel_all_d)
    def _(): ui.update_selectize("disaster_type", selected=[],             session=session)

    @reactive.effect
    @reactive.event(input.reset_button)
    def _reset():
        ui.update_selectize("countries",     selected=["Brazil", "Bangladesh", "South Africa"],      session=session)
        ui.update_selectize("disaster_type", selected=DISASTER_TYPES, session=session)
        ui.update_select("summary_stat",     selected="sum",          session=session)
        ui.update_select("map_metric",       selected="total_loss",    session=session)
        ui.update_date_range("date_range", start="2018-01-01", end="2024-12-31", session=session)

    # ── Active filter strip ───────────────────────────────────────────────────
    @render.ui
    def filter_strip():
        countries = [c for c in input.countries()     if c != "_all_"]
        disasters = [d for d in input.disaster_type() if d != "_all_"]
        start, end = input.date_range()

        def fmt(lst, full, label):
            if not lst:               return "None"
            if len(lst) == len(full): return label
            if len(lst) <= 3:         return ", ".join(lst)
            return ", ".join(lst[:2]) + f" +{len(lst)-2} more"

        lbl  = lambda t: ui.span(t, class_="fp-label")
        pill = lambda t: ui.span(t, class_="fp-pill")
        sep  = lambda: ui.span("·", class_="fp-sep")

        return ui.div(
            lbl("Countries:"),  pill(fmt(countries, COUNTRIES, "All Countries")), sep(),
            lbl("Disasters:"),  pill(fmt(disasters, DISASTER_TYPES, "All Types")), sep(),
            lbl("Dates:"),      pill(f"{start} → {end}"), sep(),
            lbl("Bar Chart Stat:"),  pill(SUMMARY_CHOICES[input.summary_stat()]), sep(),
            lbl("Map Metric:"), pill(MAP_METRICS[input.map_metric()]),
        )

    @render.ui
    def ai_instructions():
        style_label = AI_STYLE_CHOICES.get(input.ai_response_style() or "concise", "Concise Analyst")
        return ui.div(
            ui.span(
                "Tip: For the clearest view of full AI replies and query outputs, click Expand on this chat card.",
                class_="ai-expand-note",
            ),
            ui.span("How To Ask Better AI Questions", class_="ai-title"),
            ui.div(f"Current response style: {style_label}"),
            ui.tags.ul(
                ui.tags.li("Be explicit about metric, location, and year range."),
                ui.tags.li("For counts, rankings, and averages, include the exact measure to compute."),
                ui.tags.li("For filtered views, use verbs like show, filter, keep only, and include conditions."),
                ui.tags.li("Ask follow-up questions to refine thresholds, dates, and regions."),
            ),
            class_="ai-instructions",
        )

    @render.ui
    def prompt_chips():
        prompts = [
            "How many flood events occurred in India after 2020?",
            "Which 5 countries had the highest total economic loss in 2024?",
            "Filter events where casualties > 1000 and aid < 10M USD.",
            "Compare total aid for floods vs earthquakes since 2019.",
            "Show only wildfires in Australia between 2021 and 2023.",
            "What is the average economic loss per disaster type?",
            "List countries where aid is below 30% of total losses.",
            "Show all disasters in Bangladesh in 2022.",
        ]
        return ui.div(
            *[
                ui.tags.button(
                    p,
                    class_="prompt-chip",
                    **{"data-prompt": p},
                )
                for p in prompts
            ],
            class_="prompt-chips-wrap",
        )

    # ── Filtered data (Overview tab) ──────────────────────────────────────────
    @reactive.calc
    def filtered_df():
        c = ibis._
        expr = disaster_table

        countries = [x for x in input.countries()     if x != "_all_"]
        if countries:
            expr = expr.filter(c.country.isin(countries))

        disasters = [x for x in input.disaster_type() if x != "_all_"]
        if disasters:
            expr = expr.filter(c.disaster_type.isin(disasters))

        start, end = input.date_range()
        expr = expr.filter(c.date.between(start, end))

        return expr

    # ── Empty figure helper ───────────────────────────────────────────────────
    def _empty_fig(msg="No data to display", hint="Adjust your filters"):
        fig = go.Figure()
        fig.add_annotation(
            text=f"<b>{msg}</b><br><span style='font-size:11px'>{hint}</span>",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=13, color="#94a3b8", family="Instrument Sans"),
            align="center",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    # ── KPI Grid ──────────────────────────────────────────────────────────────
    @render.ui
    def kpi_grid():
        data = filtered_df().execute()
        if data.empty:
            gap_dollar_val = "-"
            gap_pct_val = "-"
        else:
            # Total Funding Gap
            total_loss    = data["economic_loss_usd"].sum()
            total_aid     = data["aid_amount_usd"].sum()
            total_gap     = total_loss - total_aid
            gap_dollar_val = fmt_currency(total_gap)
            # GDP Normalized Median Gap (%)
            agg = (
                data.groupby("country").agg(
                    loss=("economic_loss_usd", "sum"),
                    aid=("aid_amount_usd", "sum")
                ).reset_index()
            )
            agg["gap"] = agg["loss"] - agg["aid"]
            agg["gdp"] = agg["country"].map(GDP)

            if agg.empty:
                gap_pct_val="-"
            else:
                agg["gap_pct_gdp"] = (agg["gap"]/agg["gdp"])*100
                median_gap_pct = agg["gap_pct_gdp"].median()
                gap_pct_val = f"{median_gap_pct:.2f}%"

        def kpi_box(cls, value, title, subtitle=None, formula=None):
            return ui.div(
                ui.div(title, class_="kpi-title"),
                ui.div(value, class_="kpi-value"),
                ui.div(subtitle, class_="kpi-subtitle") if subtitle else None,
                ui.div(formula, class_="kpi-formula") if formula else None,
                class_=f"kpi-box {cls}",
            )

        return ui.div(
            kpi_box("kpi-gap",
                     gap_dollar_val, 
                     "Total Unfunded Disaster Losses", 
                     "Disaster losses not covered by aid",
                     "Loss - Aid", 
                     ),
            kpi_box("kpi-coverage", 
                    gap_pct_val, 
                    "Disaster Burden (% of GDP)",
                    "Typical funding gap relative to GDP", 
                    "Median((Loss − Aid) ÷ GDP)", 
                    ),
            class_="kpi-grid",
            style="height:100%;",
        )
    @render.text
    def map_title():
        return QUESTION_MAP[input.map_metric()]
    # ── Choropleth Map ────────────────────────────────────────────────────────
    @render_widget
    def map_plot():
        data   = filtered_df().execute()
        metric = input.map_metric()

        if data.empty:
            return _empty_fig("No data to display", "Adjust your filters to see disaster locations")

        agg = (
            data.groupby("country")
            .agg(
                disasters=("disaster_type",         "count"),
                casualties=("casualties",            "sum"),
                total_loss=("economic_loss_usd",     "sum"),
                total_aid=("aid_amount_usd",         "sum"),
                avg_severity=("severity_index",      "mean"),
                avg_response=("response_time_hours", "mean"),
            )
            .reset_index()
        )
        agg["iso3"]         = agg["country"].map(ISO3)
        agg["loss_fmt"]     = agg["total_loss"].apply(fmt_currency)
        agg["aid_fmt"]      = agg["total_aid"].apply(fmt_currency)
        agg["cas_fmt"]      = agg["casualties"].apply(lambda x: f"{x:,}")
        agg["sev_fmt"]      = agg["avg_severity"].round(1)
        agg["resp_fmt"]     = agg["avg_response"].round(1).astype(str) + "h"
        agg["coverage_pct"] = (
            agg["total_aid"] / agg["total_loss"].replace(0, float("nan")) * 100
        ).round(1)
        agg["cov_fmt"] = agg["coverage_pct"].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )

        metric_label = MAP_METRICS[metric]
        fig = px.choropleth(
            agg, locations="iso3",
            color=metric,
            hover_name="country",
            range_color=(agg[metric].min(), agg[metric].max()),
            hover_data={
                "iso3": False, metric: False,
                "disasters": True, "cas_fmt": True,
                "loss_fmt": True, "aid_fmt": True,
                "cov_fmt": True, "sev_fmt": True, "resp_fmt": True,
            },
            labels={
                "disasters": "# Events", "cas_fmt": "Casualties",
                "loss_fmt":  "Econ Loss", "aid_fmt": "Aid Amount",
                "cov_fmt":   "Coverage",  "sev_fmt": "Avg Severity",
                "resp_fmt":  "Avg Response",
            },
            color_continuous_scale="viridis",
        )
        # ── Auto zoom to selected countries ──
        fig.update_geos(
            projection_type="natural earth",
            fitbounds="locations",
            scope="world",   
            showframe=False,
            # Borders
            showcountries=True,
            countrycolor="#64748b",
            countrywidth=0.8,

            showcoastlines=True,
            coastlinecolor="#64748b",
            coastlinewidth=0.6,

            # Land & water
            showland=True,
            landcolor="#e8edf4",

            showocean=True,
            oceancolor="#dbeafe",

            showlakes=True,
            lakecolor="#dbeafe",

            bgcolor="rgba(0,0,0,0)",
        )
        fig.update_traces(marker_line_color="#94a3b8", marker_line_width=0.5)
        fig.update_layout(
            margin=dict(l=0, r=80, t=0, b=0),
            height=360,
            coloraxis_colorbar=dict(
                title=dict(text=metric_label, font=dict(size=9, color=T_SEC, family="Instrument Sans")),
                orientation="v", x=1.02, xanchor="left", y=0.5, yanchor="middle",
                thickness=11, len=0.55,
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                outlinewidth=0,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hoverlabel=dict(
                bgcolor="#fff", font_color=T_PRI, font_size=11,
                font_family="Instrument Sans", bordercolor=NAVY,
            ),
            geo=dict(domain=dict(x=[0, 0.96], y=[0.1, 1])),
        )
        return fig

    # ── Overview Bar Chart Helper ─────────────────────────────────────────────
    def _make_bar(column, y_label):
        data = filtered_df().execute()
        if data.empty:
            return _empty_fig("No data to display", "Select countries and disaster types to view")

        stat     = input.summary_stat()
        stat_lbl = SUMMARY_CHOICES[stat]
        grp = (
            data.groupby("disaster_type")[column]
            .agg(stat).reset_index()
            .sort_values(column, ascending=False)
        )
        grp["fmt"] = grp[column].apply(fmt_currency)
        n       = len(grp)
        palette = pc.sample_colorscale("teal", [i / max(n - 1, 1) for i in range(n)])

        y_max   = grp[column].max()
        y_range = [0, y_max * 1.25]

        fig = go.Figure(go.Bar(
            x=grp["disaster_type"],
            y=grp[column],
            orientation="v",
            marker=dict(color=palette, line=dict(width=0)),
            customdata=grp[["fmt"]],
            hovertemplate="<b>%{x}</b><br>" + f"{y_label}: %{{customdata[0]}}<extra></extra>",
            text=grp["fmt"],
            textposition="outside",
            textfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
        ))
        fig.update_layout(
            annotations=[dict(
                text=f"({stat_lbl})", xref="paper", yref="paper",
                x=1, y=1.05, xanchor="right", yanchor="bottom",
                showarrow=False, font=dict(size=9, color=T_SEC, family="Instrument Sans"),
            )],
            yaxis=dict(
                title=dict(text=y_label, font=dict(size=9, color=T_SEC, family="Instrument Sans")),
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                gridcolor=BORDER, showgrid=True, zeroline=False, showline=False,
                range=y_range,
            ),
            xaxis=dict(
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                showgrid=False, zeroline=False, showline=True, linecolor=BORDER,
                automargin=True,
                autorange=True,  # let Plotly calculate range naturally
            ),
            margin=dict(l=60, r=20, t=22, b=80),
            height=274,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            hoverlabel=dict(
                bgcolor="#fff", font_color=T_PRI,
                font_size=11, font_family="Instrument Sans", bordercolor=NAVY,
            ),
        )
        return fig
    
    @render_widget
    def bar_loss():
        return _make_bar("economic_loss_usd", "Economic Loss (USD)")

    @render_widget
    def bar_aid():
        return _make_bar("aid_amount_usd", "Aid Amount (USD)")

    # =========================================================================
    # ── AI Explorer Tab ───────────────────────────────────────────────────────
    # =========================================================================

    # Wire up querychat server.
    # Returns a dict: chat["df"]() → filtered dataframe, chat["sql"]() → SQL string
    qc_vals = qc.server(id="chat")

    tool_audit = reactive.value([])
    ai_runtime_status = reactive.value("Awaiting first AI query.")
    ai_sync_status = reactive.value("No AI query has been executed yet.")

    # Plain Python lists/dicts for collecting data inside the Extended Task
    # (reactive values cannot be read or written inside Extended Tasks).
    _pending_audit: list = []
    _pending_status: list = []  # holds at most the latest status string

    def _append_audit_entry(entry):
        _pending_audit.append(entry)

    def _tool_result_row_count(value):
        if isinstance(value, list):
            return len(value)
        if isinstance(value, pd.DataFrame):
            return int(value.shape[0])
        return None

    def _on_tool_request(request):
        tool_name = request.name
        args = dict(request.arguments) if isinstance(request.arguments, dict) else {}
        original_query = str(args.get("query", ""))
        final_query = original_query
        transformed = False

        if tool_name not in {
            "querychat_query",
            "querychat_update_dashboard",
            "querychat_reset_dashboard",
        }:
            raise chatlas.ToolRejectError(f"Unsupported tool requested: {tool_name}")

        if tool_name in {"querychat_query", "querychat_update_dashboard"}:
            final_query = normalize_sql(original_query)
            if not final_query:
                raise chatlas.ToolRejectError("Tool request was rejected because SQL query was empty.")

            if not is_read_only_sql(final_query):
                raise chatlas.ToolRejectError(
                    "Tool request was rejected because SQL must be read-only SELECT or WITH."
                )

            if tool_name == "querychat_query":
                intent = str(args.get("_intent", ""))
                if is_count_intent(intent, final_query):
                    count_query = force_count_query(final_query)
                    transformed = count_query != final_query
                    final_query = count_query

            args["query"] = final_query
            request.arguments = args

        _pending_status.clear()
        _pending_status.append(f"Validated tool request: {tool_name}")
        _append_audit_entry(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stage": "request",
                "tool": tool_name,
                "query_before": normalize_sql(original_query) if original_query else "",
                "query_after": final_query,
                "transformed": transformed,
            }
        )

    def _on_tool_result(result):
        tool_name = result.request.name if result.request is not None else "unknown"
        row_count = _tool_result_row_count(result.value)
        error_text = str(result.error) if result.error is not None else ""

        if error_text:
            status = f"Tool error in {tool_name}: {error_text}"
        elif row_count is None:
            status = f"Tool executed: {tool_name}"
        else:
            status = f"Tool executed: {tool_name} ({row_count} rows returned)"

        _pending_status.clear()
        _pending_status.append(status)
        _append_audit_entry(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stage": "result",
                "tool": tool_name,
                "rows": row_count,
                "error": error_text,
            }
        )

    qc_vals.client.on_tool_request(_on_tool_request)
    qc_vals.client.on_tool_result(_on_tool_result)

    # Flush pending tool data into reactive values after each chat turn completes.
    # qc_vals.df() changes whenever QueryChat finishes a turn — use it as the trigger.
    @reactive.effect
    def _flush_tool_state():
        qc_vals.df()  # invalidate whenever a new AI result is available
        if _pending_status:
            ai_runtime_status.set(_pending_status[-1])
            _pending_status.clear()
        if _pending_audit:
            history = list(tool_audit.get() or [])
            history.extend(_pending_audit)
            tool_audit.set(history[-40:])
            _pending_audit.clear()

    @reactive.effect
    @reactive.event(input.ai_response_style)
    def _update_prompt_for_style():
        # @reactive.event already isolates the body; read the input directly.
        style = input.ai_response_style() or "concise"
        qc_vals.client.system_prompt = QC_BASE_SYSTEM_PROMPT + style_prompt_suffix(style)

    @render.ui
    def ai_query_status():
        sql_text = normalize_sql(qc_vals.sql() or "")
        history = tool_audit.get() or []
        last_event = history[-1] if history else None
        last_event_text = "No tool call yet."
        if last_event is not None:
            stage = last_event.get("stage", "event")
            tool_name = last_event.get("tool", "unknown")
            rows = last_event.get("rows")
            if rows is None:
                last_event_text = f"{stage} -> {tool_name}"
            else:
                last_event_text = f"{stage} -> {tool_name} ({rows} rows)"

        return ui.div(
            ui.div(ui.tags.strong("Tool pipeline:"), f" {ai_runtime_status()}"),
            ui.div(ui.tags.strong("Dataframe sync:"), f" {ai_sync_status()}"),
            ui.div(ui.tags.strong("Active SQL:"), f" {sql_text if sql_text else 'None'}"),
            ui.div(ui.tags.strong("Last event:"), f" {last_event_text}"),
            class_="ai-query-status",
        )
    
    @reactive.calc
    def ai_df():
        return qc_vals.df()

    @reactive.effect
    def _verify_ai_sync():
        data = ai_df()
        row_count = len(data) if hasattr(data, "__len__") else 0
        has_sql = bool(normalize_sql(qc_vals.sql() or ""))
        if has_sql:
            ai_sync_status.set(
                f"Verified shared ai_df with {row_count:,} rows. The AI table and both AI charts read this same filtered dataframe."
            )
        else:
            ai_sync_status.set(
                f"Current ai_df size: {row_count:,} rows. No persistent AI dashboard filter is active yet."
            )

    # Filtered data table
    @render.data_frame
    def ai_table():
        data = ai_df()
        if data.empty:
            return render.DataGrid(
                pd.DataFrame({"message": ["No results — try a different query."]}),
                filters=False,
            )
        return render.DataGrid(data.head(500), filters=True)

    # CSV download
    @render.download(filename="disaster_ai_filtered.csv")
    def download_ai_csv():
        data = ai_df()
        with io.StringIO() as buf:
            data.to_csv(buf, index=False)
            yield buf.getvalue()

    # AI bar chart helper (always uses sum; independent of Overview summary_stat)
    def _make_ai_bar(column, y_label):
        data = ai_df()
        if data.empty:
            return _empty_fig("No data yet", "Ask a question above to filter the dataset")
        if "disaster_type" not in data.columns or data["disaster_type"].isna().all():
            return _empty_fig("No disaster_type column", "Check your query")

        grp = (
            data.groupby("disaster_type")[column]
            .sum().reset_index()
            .sort_values(column, ascending=False)
        )
        grp["fmt"] = grp[column].apply(fmt_currency)
        n = len(grp)
        palette = pc.sample_colorscale("teal", [i / max(n - 1, 1) for i in range(n)])

        y_max   = grp[column].max()
        y_range = [0, y_max * 1.25]

        fig = go.Figure(go.Bar(
            x=grp["disaster_type"],
            y=grp[column],
            orientation="v",
            marker=dict(color=palette, line=dict(width=0)),
            customdata=grp[["fmt"]],
            hovertemplate="<b>%{x}</b><br>" + f"{y_label}: %{{customdata[0]}}<extra></extra>",
            text=grp["fmt"],
            textposition="outside",
            textfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
        ))
        fig.update_layout(
            yaxis=dict(
                title=dict(text=y_label, font=dict(size=9, color=T_SEC, family="Instrument Sans")),
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                gridcolor=BORDER, showgrid=True, zeroline=False, showline=False,
                range=y_range,
            ),
            xaxis=dict(
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                showgrid=False, zeroline=False, showline=True, linecolor=BORDER,
                automargin=True,
                autorange=True,  # let Plotly calculate range naturally
            ),
            margin=dict(l=60, r=20, t=10, b=80),
            height=274,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            hoverlabel=dict(
                bgcolor="#fff", font_color=T_PRI,
                font_size=11, font_family="Instrument Sans", bordercolor=NAVY,
            ),
        )
        return fig

    @render_widget
    def ai_bar_loss():
        return _make_ai_bar("economic_loss_usd", "Economic Loss (USD)")

    @render_widget
    def ai_bar_aid():
        return _make_ai_bar("aid_amount_usd", "Aid Amount (USD)")


app = App(app_ui, server)