from shiny import App, ui, render, reactive
import pandas as pd

# Load Data
df = pd.read_csv("../data/raw/global_disaster_response_2018_2024.csv",
                 parse_dates=["date"])
# Utility Function
def format_currency(value):
    """Format a numeric value as a human-readable currency string."""

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

COUNTRIES = ["Australia",
            "Bangladesh",
            "Brazil", 
            "Canada",
            "Chile",
            "China",
            "France", 
            "Germany",
            "Greece",
            "India",
            "Indonesia", 
            "Italy",
            "Japan",
            "Mexico",
            "Nigeria",
            "Philippines",
            "South Africa",
            "Spain", 
            "Turkey",
            "United States"
            ]

DISASTER_TYPES = ["Drought", 
                  "Earthquake",
                  "Extreme Heat",
                  "Flood",
                  "Hurricane",
                  "Landslide",
                  "Storm Surge",
                  "Tornado",
                  "Volcanic Eruption",
                  "Wildfire"
                ]

app_ui = ui.page_fillable(
    ui.panel_title("Disaster Dash"),
    ui.layout_sidebar(
        ui.sidebar(
            # Input: User can Check/Uncheck countries
            ui.input_checkbox_group(
                id="countries", 
                label="Countries", 
                choices={c: c for c in COUNTRIES},
                selected=COUNTRIES,
            ),
            # Buttons for All or None Countries 
            ui.div(
                ui.input_action_button(
                    id="select_all_countries",
                    label="All", 
                    width="50%"
                ),
                ui.input_action_button(
                    id="deselect_all_countries",
                    label="None", 
                    width="50%"
                ),
                style="display: flex; gap: 5px;"
            ),
            # Date Range Toggle
            ui.input_date_range(
                id="date_range", 
                label="Date Range",
                start="2018-01-01",
                end="2024-12-31",
                min="2018-01-01",
                max="2024-12-31"
            ),
            # Input: User can check/uncheck disaster boxes
            ui.input_checkbox_group(
                id="disaster_type",
                label="Disaster Type",
                choices={d: d for d in DISASTER_TYPES},
                selected=DISASTER_TYPES,
            ),
            # All or None buttons for disaster types 
            ui.div(
                ui.input_action_button(
                    id="select_all_disasters",
                    label="All", 
                    width="50%"
                ),
                ui.input_action_button(
                    id="deselect_all_disasters",
                    label="None", 
                    width="50%"
                ),
                style="display: flex; gap:5px;"
            ),
            # Summary Statistic Drop Down Menu 
            ui.input_select(
                id="summary_stat", 
                label="Summary Statistic",
                choices={
                    "mean": "Average", 
                    "sum": "Total Sum", 
                    "min": "Minimum", 
                    "max": "Maximum"
                },
                selected="mean"
            ),
            ui.input_action_button(
                id="reset_button", 
                label="Reset Filters"
                ),
            open="desktop",
        ),
        # Outputs 
        ui.layout_columns(
            #  World Map 
            ui.card("World Map: Countries coloured by number of disasters", full_screen=True),
            # KPI Cards 
            ui.layout_columns(
                ui.card(
                    ui.output_ui("kpi_ratio"),
                    title="Aid Coverage"
                ),
                ui.card(
                    ui.output_ui("kpi_gap"),
                    title="Aid Gap"
                ), 
                col_widths=[12, 12],
                row_heights=[1, 1]
            ),
            col_widths=[9,3]
        ),
        ui.layout_columns(
            # Bar Charts 
            ui.card("Bar Chart of Economic Loss by Disaster Type ($)"),
            ui.card("Bar Chart of Economic Aid by Disaster Type ($)"),
            col_widths=[6, 6]
        ),
    )
)

def server(input, output, session):
    # button handling! 
    @reactive.effect
    @reactive.event(input.select_all_countries)
    def select_all_countries():
        ui.update_checkbox_group(
            id="countries", 
            selected=COUNTRIES,
            session=session
        )
    @reactive.effect
    @reactive.event(input.deselect_all_countries)
    def deselect_all_countries():
        ui.update_checkbox_group(
            id="countries", 
            selected=[],
            session=session
        )
    @reactive.effect
    @reactive.event(input.select_all_disasters)
    def select_all_disasters():
        ui.update_checkbox_group(
            id="disaster_type", 
            selected=DISASTER_TYPES,
            session=session
        )
    @reactive.effect
    @reactive.event(input.deselect_all_disasters)
    def deselect_all_disasters():
        ui.update_checkbox_group(
            id="disaster_type",
            selected=[],
            session=session
        )
    @reactive.effect
    @reactive.event(input.reset_button)
    def reset_filters():
        ui.update_checkbox_group(
            id="countries", 
            selected=COUNTRIES,
            session=session
        )
        ui.update_checkbox_group(
            id="disaster_type",
            selected=DISASTER_TYPES, 
            session=session
        )
        ui.update_select(
            id="summary_stat", 
            selected="mean",
            session=session
        )
    # Filtered Dataframe 
    @reactive.calc
    def filtered_df():
        filtered = df[
            (df["country"].isin(input.countries())) &
            (df["disaster_type"].isin(input.disaster_type())) &
            (df["date"] >= pd.to_datetime(input.date_range()[0])) &
            (df["date"] <= pd.to_datetime(input.date_range()[1]))
        ]
        return filtered
    @render.ui
    def kpi_ratio():
        data = filtered_df()

        total_loss = data["economic_loss_usd"].sum()
        total_aid = data['aid_amount_usd'].sum()

        if total_loss == 0:
            ratio = 0
        else:
            ratio = (total_aid / total_loss) * 100
        
        return ui.h3(f"{ratio:.1f}% Loss Covered")
    
    @render.ui
    def kpi_gap():
        data = filtered_df()

        total_loss = data["economic_loss_usd"].sum()
        total_aid = data["aid_amount_usd"].sum()
        gap = total_loss - total_aid

        return ui.h3(f"{format_currency(gap)} Aid Gap")


app = App(app_ui, server)