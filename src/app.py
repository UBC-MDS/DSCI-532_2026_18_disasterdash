"""
Disaster Dash (v2) — Improved UI/UX & Functionality
Global Disaster Impact & Humanitarian Aid (2018–2024)

Features:
  • Single-page Overview layout (map, KPI cards, bar charts)
  • 2 KPI cards: Aid Coverage %, Funding Gap
  • Choropleth map with switchable metric (frequency, coverage, casualties, loss)
  • Horizontal bar charts: Economic Loss & Aid Amount by disaster type
  • Configurable summary statistic (mean, sum, min, max) for bar charts
  • Active filter strip banner
  • Searchable multi-select inputs for country and disaster type
  • Better typography (Syne + Instrument Sans)
  • Accessible labels (visually hidden, not display:none)
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
from pathlib import Path
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

# ── Load Data ──────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "global_disaster_response_2018_2024.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

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
MAP_METRICS = {
    "disasters":   "Disaster Frequency",
    "coverage_pct": "Aid Coverage (%)",
    "casualties":  "Total Casualties",
    "total_loss":  "Economic Loss (USD)",
}
LAST_UPDATED = datetime.today().strftime("%B %d, %Y")

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
    background: linear-gradient(135deg, {AMBER} 0%, #f97316 100%);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 4px 14px rgba(245,158,11,0.35);
    flex-shrink: 0;
}}
#page-header h1 {{
    font-family: 'Syne', sans-serif;
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
    margin: 18px 14px 14px !important;
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
    padding: 10px 16px !important;
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
    justify-content: center;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.15s, box-shadow 0.15s;
}}
.kpi-box:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important;
}}
.kpi-box::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}}
.kpi-events::before   {{ background: linear-gradient(90deg, {BLUE}, #60a5fa); }}
.kpi-cas::before      {{ background: linear-gradient(90deg, {RED}, #f87171); }}
.kpi-coverage::before {{ background: linear-gradient(90deg, {GREEN}, #34d399); }}
.kpi-gap::before      {{ background: linear-gradient(90deg, {AMBER}, #fcd34d); }}

.kpi-icon {{
    font-size: 1.4rem;
    margin-bottom: 8px;
    line-height: 1;
}}
.kpi-value {{
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: {T_PRI};
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 5px;
}}
.kpi-title {{
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: {T_SEC};
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

/* ── DATA TABLE ── */
.dataframe-table-container {{ overflow-x: auto; }}
.shiny-data-frame-output .data-table-container {{
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
}}

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
    ui.tags.head(ui.tags.style(CSS)),

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
                ui.div("Date Range", class_="sb-label"),
                ui.input_date_range(
                    "date_range", label=None,
                    start="2018-01-01", end="2024-12-31",
                    min="2018-01-01",   max="2024-12-31",
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
                ui.div("Summary Statistic", class_="sb-label"),
                ui.input_select(
                    "summary_stat", label=None,
                    choices=SUMMARY_CHOICES, selected="sum",
                ),
                class_="sb-section",
            ),

            ui.div(
                ui.div("Map Metric", class_="sb-label"),
                ui.input_select(
                    "map_metric", label=None,
                    choices=MAP_METRICS, selected="disasters",
                ),
                class_="sb-section",
            ),

            ui.input_action_button("reset_button", "↺  Reset All Filters"),

            width=236,
            open="desktop",
        ),

        # ── Main Content ───────────────────────────────────────────────────────
        ui.div(
            # Active filter strip
            ui.div(ui.output_ui("filter_strip"), id="filter-strip"),

            # Tabs
            ui.navset_underline(

                # ── Tab 1: Overview ──────────────────────────────────────────
                ui.nav_panel(
                    "📊  Overview",
                    ui.div(

                        # Row 1: Map + 4 KPIs
                        ui.layout_columns(
                            ui.card(
                                ui.card_header("🗺️  Disaster Map"),
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
                ),

                id="main_tabs",
            ),

            # Footer
            ui.div(
                ui.span("Disaster Dash v3  ·  "),
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
        ui.update_select("map_metric",       selected="disasters",    session=session)
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

        lbl = lambda t: ui.span(t, class_="fp-label")
        pill = lambda t: ui.span(t, class_="fp-pill")
        sep = lambda: ui.span("·", class_="fp-sep")

        return ui.div(
            lbl("Countries:"),  pill(fmt(countries, COUNTRIES, "All Countries")), sep(),
            lbl("Disasters:"),  pill(fmt(disasters, DISASTER_TYPES, "All Types")), sep(),
            lbl("Dates:"),      pill(f"{start} → {end}"), sep(),
            lbl("Statistic:"),  pill(SUMMARY_CHOICES[input.summary_stat()]), sep(),
            lbl("Map Metric:"), pill(MAP_METRICS[input.map_metric()]),
        )

    # ── Filtered data ─────────────────────────────────────────────────────────
    @reactive.calc
    def filtered_df():
        countries = [c for c in input.countries()     if c != "_all_"]
        disasters = [d for d in input.disaster_type() if d != "_all_"]
        mask = (
            df["country"].isin(countries) &
            df["disaster_type"].isin(disasters) &
            (df["date"] >= pd.to_datetime(input.date_range()[0])) &
            (df["date"] <= pd.to_datetime(input.date_range()[1]))
        )
        return df[mask].copy()

    # ── Empty state helper ────────────────────────────────────────────────────
    def empty_state(icon, msg, hint=""):
        return ui.HTML(f'''
            <div class="empty-state">
                <div class="es-icon">{icon}</div>
                <div class="es-msg">{msg}</div>
                {"" if not hint else f'<div class="es-hint">{hint}</div>'}
            </div>
        ''')


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
        data = filtered_df()
        if data.empty:
            cov_val = "—"; gap_val = "—"
        else:
            loss    = data["economic_loss_usd"].sum()
            aid     = data["aid_amount_usd"].sum()
            cov     = (aid / loss * 100) if loss > 0 else 0.0
            gap     = loss - aid
            cov_val = f"{cov:.1f}%"
            gap_val = fmt_currency(gap)

        def kpi_box(cls, icon, value, title):
            return ui.div(
                ui.div(icon, class_="kpi-icon"),
                ui.div(value, class_="kpi-value"),
                ui.div(title, class_="kpi-title"),
                class_=f"kpi-box {cls}",
            )

        return ui.div(
            kpi_box("kpi-coverage", "🛡️", cov_val, "Aid Coverage"),
            kpi_box("kpi-gap",      "⚠️", gap_val, "Funding Gap"),
            class_="kpi-grid",
            style="height:100%;",
        )

    # ── Map ───────────────────────────────────────────────────────────────────
    @render_widget
    def map_plot():
        data   = filtered_df()
        metric = input.map_metric()

        if data.empty:
            return _empty_fig("No data to display", "Adjust your filters to see disaster locations")

        agg = (
            data.groupby("country")
            .agg(
                disasters=("disaster_type",      "count"),
                casualties=("casualties",         "sum"),
                total_loss=("economic_loss_usd",  "sum"),
                total_aid=("aid_amount_usd",      "sum"),
                avg_severity=("severity_index",   "mean"),
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
        agg["cov_fmt"]      = agg["coverage_pct"].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )

        metric_label = MAP_METRICS[metric]
        fig = px.choropleth(
            agg, locations="iso3",
            color=metric,
            hover_name="country",
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
            color_continuous_scale="cividis",
        )
        fig.update_geos(
            projection_type="natural earth",
            showframe=False,
            showcoastlines=True,  coastlinecolor="#94a3b8",
            showland=True,        landcolor="#e8edf4",
            showocean=True,       oceancolor="#d4e5f7",
            showlakes=True,       lakecolor="#d4e5f7",
            showcountries=True,   countrycolor="#94a3b8",
            lataxis_range=[-58, 80], lonaxis_range=[-170, 180],
            bgcolor="rgba(0,0,0,0)",
        )
        fig.update_traces(marker_line_color="#94a3b8", marker_line_width=0.5)
        fig.update_layout(
            margin=dict(l=0, r=80, t=0, b=0),
            height=340,
            coloraxis_colorbar=dict(
                title=dict(text=metric_label, font=dict(size=9, color=T_SEC, family="Instrument Sans")),
                orientation="v", x=1.01, xanchor="left", y=0.5, yanchor="middle",
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
            geo=dict(domain=dict(x=[0, 0.93], y=[0, 1])),
        )
        return fig

    # ── Bar chart helper ──────────────────────────────────────────────────────
    def _make_bar(column, y_label):
        data = filtered_df()
        if data.empty:
            return _empty_fig("No data to display", "Select countries and disaster types to view")

        stat     = input.summary_stat()
        stat_lbl = SUMMARY_CHOICES[stat]
        grp = (
            data.groupby("disaster_type")[column]
            .agg(stat).reset_index()
            .sort_values(column, ascending=True)   # ascending for bottom-up readability
        )
        grp["fmt"] = grp[column].apply(fmt_currency)
        n       = len(grp)
        palette = pc.sample_colorscale("cividis", [i / max(n - 1, 1) for i in range(n)])

        fig = go.Figure(go.Bar(
            y=grp["disaster_type"],
            x=grp[column],
            orientation="h",
            marker=dict(color=palette, line=dict(width=0)),
            customdata=grp[["fmt"]],
            hovertemplate="<b>%{y}</b><br>" + f"{y_label}: %{{customdata[0]}}<extra></extra>",
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
            xaxis=dict(
                title=dict(text=y_label, font=dict(size=9, color=T_SEC, family="Instrument Sans")),
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                gridcolor=BORDER, showgrid=True, zeroline=False, showline=False,
            ),
            yaxis=dict(
                tickfont=dict(size=8, color=T_SEC, family="Instrument Sans"),
                showgrid=False, zeroline=False, showline=True, linecolor=BORDER,
                automargin=True,
            ),
            margin=dict(l=10, r=70, t=22, b=42),
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


app = App(app_ui, server)