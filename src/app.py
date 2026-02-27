"""
Disaster Dash: An interactive Shiny dashboard for exploring global disaster
impacts and humanitarian aid (2018–2024).

Features:
- Interactive filtering by country, disaster type, and date range
- KPI cards for Aid Coverage and Aid Gap
- Aggregated bar charts of economic loss and aid (Plotly, cividis, tooltips)
- World choropleth map coloured by number of disasters (cividis)
- Dynamic summary of active filters
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
from pathlib import Path
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


# ── Load Data ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "global_disaster_response_2018_2024.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["date"])


# ── Country → ISO-3 mapping (for choropleth) ───────────────────────────────────
ISO3 = {
    "Australia":      "AUS",
    "Bangladesh":     "BGD",
    "Brazil":         "BRA",
    "Canada":         "CAN",
    "Chile":          "CHL",
    "China":          "CHN",
    "France":         "FRA",
    "Germany":        "DEU",
    "Greece":         "GRC",
    "India":          "IND",
    "Indonesia":      "IDN",
    "Italy":          "ITA",
    "Japan":          "JPN",
    "Mexico":         "MEX",
    "Nigeria":        "NGA",
    "Philippines":    "PHL",
    "South Africa":   "ZAF",
    "Spain":          "ESP",
    "Turkey":         "TUR",
    "United States":  "USA",
}


# ── Helpers ────────────────────────────────────────────────────────────────────
def format_currency(value):
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1e12:
        return f"{sign}${value/1e12:.1f}T"
    elif value >= 1e9:
        return f"{sign}${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{sign}${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{sign}${value/1e3:.1f}K"
    else:
        return f"{sign}${value:.0f}"


PLOTLY_CONFIG = {"displayModeBar": False}   # hide plotly toolbar for cleanliness


# ── Global constants ───────────────────────────────────────────────────────────
COUNTRIES = sorted(ISO3.keys())

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

LAST_UPDATED = datetime.today().strftime("%B %d, %Y")


# ── UI ─────────────────────────────────────────────────────────────────────────
app_ui = ui.page_fillable(
    ui.tags.head(
        ui.tags.style("""
            .value-box-value { font-size: 1.6rem !important; }
            .sidebar { font-size: 0.85rem; }
            .card { border-radius: 8px; }
            .badge { font-size: 0.78rem; }
        """)
    ),

    ui.panel_title(ui.h5("Disaster Dash", style="margin:0; padding:0;")),

    ui.div(
        ui.output_ui("active_filters"),
        class_="mb-1",
        style="padding: 4px 8px;",
    ),

    ui.layout_sidebar(
        ui.sidebar(
            ui.input_checkbox_group(
                id="countries",
                label="Countries",
                choices={c: c for c in COUNTRIES},
                selected=COUNTRIES,
            ),
            ui.div(
                ui.input_action_button("select_all_countries", "All",  width="50%"),
                ui.input_action_button("deselect_all_countries", "None", width="50%"),
                style="display:flex; gap:5px;",
            ),
            ui.hr(),
            ui.input_date_range(
                id="date_range",
                label="Date Range",
                start="2018-01-01", end="2024-12-31",
                min="2018-01-01",   max="2024-12-31",
            ),
            ui.hr(),
            ui.input_checkbox_group(
                id="disaster_type",
                label="Disaster Type",
                choices={d: d for d in DISASTER_TYPES},
                selected=DISASTER_TYPES,
            ),
            ui.div(
                ui.input_action_button("select_all_disasters",   "All",  width="50%"),
                ui.input_action_button("deselect_all_disasters", "None", width="50%"),
                style="display:flex; gap:5px;",
            ),
            ui.hr(),
            ui.input_select(
                id="summary_stat",
                label="Summary Statistic",
                choices=SUMMARY_CHOICES,
                selected="sum",
            ),
            ui.input_action_button("reset_button", "Reset Filters", width="100%"),
            open="desktop",
        ),

        # ── Row 1: Map + KPI cards ─────────────────────────────────────────────
        ui.layout_columns(
            ui.card(
                ui.card_header("World Map — Countries coloured by number of disasters"),
                output_widget("map_plot"),
                full_screen=True,
            ),
            ui.layout_columns(
                ui.value_box(
                    "Aid Coverage",
                    ui.output_text("kpi_ratio"),
                ),
                ui.value_box(
                    "Aid Gap",
                    ui.output_text("kpi_gap"),
                ),
                col_widths=[12, 12],
            ),
            col_widths=[8, 4],
            style="height:420px;",
        ),

        # ── Row 2: Bar charts ──────────────────────────────────────────────────
        ui.layout_columns(
            ui.card(
                ui.card_header("Economic Loss by Disaster Type"),
                output_widget("bar_loss"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Aid Amount by Disaster Type"),
                output_widget("bar_aid"),
                full_screen=True,
            ),
            col_widths=[6, 6],
            style="height:420px;",
        ),

        style="flex:1 1 0; min-height:0; overflow:hidden;",
    ),

    # Footer
    ui.div(
        ui.span("Global Disaster Impact & Aid Dashboard  •  "),
        ui.span("Ojasv Issar, Joel Nicholas Peterson, Claire Saunders  •  "),
        ui.a("GitHub", href="https://github.com/UBC-MDS/DSCI-532_2026_18_disasterdash", target="_blank"),
        ui.span(f"  •  Updated {LAST_UPDATED}"),
        style="text-align:center; color:#888; font-size:0.75rem; padding:6px;",
    ),
)


# ── Server ─────────────────────────────────────────────────────────────────────
def server(input, output, session):

    # ── Button handlers ────────────────────────────────────────────────────────
    @reactive.effect
    @reactive.event(input.select_all_countries)
    def _(): ui.update_checkbox_group("countries",    selected=COUNTRIES,     session=session)

    @reactive.effect
    @reactive.event(input.deselect_all_countries)
    def _(): ui.update_checkbox_group("countries",    selected=[],            session=session)

    @reactive.effect
    @reactive.event(input.select_all_disasters)
    def _(): ui.update_checkbox_group("disaster_type", selected=DISASTER_TYPES, session=session)

    @reactive.effect
    @reactive.event(input.deselect_all_disasters)
    def _(): ui.update_checkbox_group("disaster_type", selected=[],           session=session)

    @reactive.effect
    @reactive.event(input.reset_button)
    def _():
        ui.update_checkbox_group("countries",     selected=COUNTRIES,      session=session)
        ui.update_checkbox_group("disaster_type", selected=DISASTER_TYPES, session=session)
        ui.update_select("summary_stat",          selected="sum",          session=session)
        ui.update_date_range("date_range", start="2018-01-01", end="2024-12-31", session=session)

    # ── Active filter banner ───────────────────────────────────────────────────
    @render.ui
    def active_filters():
        countries = input.countries()
        disasters = input.disaster_type()
        start, end = input.date_range()

        def fmt_list(lst, full, full_label):
            if len(lst) == 0:          return "None"
            if len(lst) == len(full):  return full_label
            if len(lst) <= 4:          return ", ".join(lst)
            return ", ".join(lst[:3]) + f" +{len(lst)-3} more"

        return ui.div(
            ui.span("Countries:",  class_="fw-semibold me-1"),
            ui.span(fmt_list(countries, COUNTRIES,     "All Countries"), class_="badge bg-secondary-subtle text-dark me-3"),
            ui.span("Disasters:",  class_="fw-semibold me-1"),
            ui.span(fmt_list(disasters, DISASTER_TYPES,"All Types"),     class_="badge bg-secondary-subtle text-dark me-3"),
            ui.span("Dates:",      class_="fw-semibold me-1"),
            ui.span(f"{start} → {end}",                                  class_="badge bg-secondary-subtle text-dark me-3"),
            ui.span("Statistic:",  class_="fw-semibold me-1"),
            ui.span(SUMMARY_CHOICES[input.summary_stat()],               class_="badge bg-secondary-subtle text-dark me-3"),
        )

    # ── Reactive filtered dataframe ────────────────────────────────────────────
    @reactive.calc
    def filtered_df():
        return df[
            (df["country"].isin(input.countries())) &
            (df["disaster_type"].isin(input.disaster_type())) &
            (df["date"] >= pd.to_datetime(input.date_range()[0])) &
            (df["date"] <= pd.to_datetime(input.date_range()[1]))
        ]

    # ── KPI cards ──────────────────────────────────────────────────────────────
    @render.text
    def kpi_ratio():
        data = filtered_df()
        total_loss = data["economic_loss_usd"].sum()
        total_aid  = data["aid_amount_usd"].sum()
        if total_loss == 0:
            return "N/A"
        return f"{(total_aid / total_loss) * 100:.1f}%"

    @render.text
    def kpi_gap():
        data = filtered_df()
        gap = data["economic_loss_usd"].sum() - data["aid_amount_usd"].sum()
        return format_currency(gap)

    # ── World Map (choropleth) ─────────────────────────────────────────────────
    @render_widget
    def map_plot():
        data = filtered_df()

        # Aggregate: count events + extra info per country
        agg = (
            data.groupby("country")
            .agg(
                disasters=("disaster_type", "count"),
                casualties=("casualties", "sum"),
                total_loss=("economic_loss_usd", "sum"),
                total_aid=("aid_amount_usd", "sum"),
            )
            .reset_index()
        )
        agg["iso3"]      = agg["country"].map(ISO3)
        agg["loss_fmt"]  = agg["total_loss"].apply(format_currency)
        agg["aid_fmt"]   = agg["total_aid"].apply(format_currency)
        agg["coverage"]  = (agg["total_aid"] / agg["total_loss"] * 100).round(1).astype(str) + "%"

        fig = px.choropleth(
            agg,
            locations="iso3",
            color="disasters",
            hover_name="country",
            hover_data={
                "iso3":       False,
                "disasters":  True,
                "casualties": True,
                "loss_fmt":   True,
                "aid_fmt":    True,
                "coverage":   True,
            },
            labels={
                "disasters":  "# Disasters",
                "casualties": "Casualties",
                "loss_fmt":   "Economic Loss",
                "aid_fmt":    "Aid Amount",
                "coverage":   "Aid Coverage",
            },
            color_continuous_scale="cividis",
            title="",
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(
                title="# Disasters",
                thickness=12,
                len=0.6,
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#444",
                showland=True,
                landcolor="#f0f0f0",
                showocean=True,
                oceancolor="#d6e8f5",
                projection_type="natural earth",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # ── Bar chart helper ───────────────────────────────────────────────────────
    def _bar_chart(column: str, y_label: str, title_prefix: str):
        data = filtered_df()
        stat = input.summary_stat()
        stat_label = SUMMARY_CHOICES[stat]

        grouped = (
            data.groupby("disaster_type")[column]
            .agg(stat)
            .reset_index()
            .sort_values(column, ascending=False)
        )
        grouped["formatted"] = grouped[column].apply(format_currency)

        # cividis discrete colours mapped to sorted values
        n = len(grouped)
        import plotly.colors as pc
        palette = pc.sample_colorscale("cividis", [i / max(n - 1, 1) for i in range(n)])

        fig = go.Figure(
            go.Bar(
                x=grouped["disaster_type"],
                y=grouped[column],
                marker_color=palette,
                customdata=grouped[["formatted"]],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{y_label}: %{{customdata[0]}}<br>"
                    "<extra></extra>"
                ),
                text=grouped["formatted"],
                textposition="outside",
                textfont_size=10,
            )
        )

        fig.update_layout(
            title=dict(text=f"{title_prefix} ({stat_label})", font_size=13),
            xaxis=dict(title="Disaster Type", tickangle=-35),
            yaxis=dict(title=y_label, showgrid=True, gridcolor="#eee"),
            margin=dict(l=60, r=20, t=45, b=80),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        return fig

    @render_widget
    def bar_loss():
        return _bar_chart("economic_loss_usd", "Economic Loss (USD)", "Economic Loss by Disaster Type")

    @render_widget
    def bar_aid():
        return _bar_chart("aid_amount_usd", "Aid Amount (USD)", "Aid Amount by Disaster Type")


app = App(app_ui, server)