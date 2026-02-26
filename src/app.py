"""
Disaster Dash: An interactive Shiny dashboard for exploring global disaster
impacts and humanitarian aid (2018–2024).

Features:
- Interactive filtering by country, disaster type, and date range
- KPI cards for Aid Coverage and Aid Gap
- Aggregated bar charts of economic loss and aid
- World map visualization of disaster counts
- Dynamic summary of active filters

All visualizations are powered by a reactive filtered dataset.
"""
from shiny import App, ui, render, reactive
from pathlib import Path
import pandas as pd


# Load Data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "global_disaster_response_2018_2024.csv"
df = pd.read_csv(DATA_PATH,
                 parse_dates=["date"])
# Helper Function for kpi_gap() 
def format_currency(value):
    """
    Format a numeric value as a human-readable USD currency string.

    Converts large values into abbreviated format:
    K (thousands), M (millions), B (billions), T (trillions).

    Parameters
    ----------
    value : float or int

    Returns
    -------
    str
        Formatted currency string.
    """
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
    
# Global Variables
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
<<<<<<< Updated upstream
=======
SUMMARY_CHOICES = {
                    "mean": "Average", 
                    "sum": "Total Sum", 
                    "min": "Minimum", 
                    "max": "Maximum"
                }

LAST_UPDATED = datetime.today().strftime("%B %d, %Y")
>>>>>>> Stashed changes

# Dashboard 
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
                ui.value_box(
                    "Aid Coverage",
                    ui.output_text("kpi_ratio")
                ),
                ui.value_box(
                    "Aid Gap",
                    ui.output_text("kpi_gap")
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
    """
    Server logic for the Disaster Dash application.

    Responsibilities:
    - Handle filter selection controls (select all, deselect all, reset)
    - Maintain a reactive filtered dataset
    - Compute KPI metrics (aid coverage and aid gap)
    - Generate aggregated data for bar charts
    - Generate country-level summaries for map visualization
    - Render active filter summaries
    """
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
        ui.update_date_range(
            id="date_range",
            start="2018-01-01",
            end="2024-12-31",
            session=session
        )
    # Filtered Dataframe 
    @reactive.calc
    def filtered_df():
        """
        Return a filtered version of the disaster dataset based on
        current user input selections.

        Filters applied:
        - Selected countries
        - Selected disaster types
        - Selected date range

        This reactive dataset is used by:
        - KPI calculations
        - Bar chart aggregations
        - Map visualizations

        Returns
        -------
        pandas.DataFrame
            Filtered disaster dataset.
        """
        filtered = df[
            (df["country"].isin(input.countries())) &
            (df["disaster_type"].isin(input.disaster_type())) &
            (df["date"] >= pd.to_datetime(input.date_range()[0])) &
            (df["date"] <= pd.to_datetime(input.date_range()[1]))
        ]
        return filtered
    # KPI Cards 
    @render.text
    def kpi_ratio():
        """
        Calculate the percentage of total economic loss covered by aid
        for the currently filtered dataset.

        Returns
        -------
        str
            Percentage formatted to one decimal place.
        """
        data = filtered_df()
        total_loss = data["economic_loss_usd"].sum()
        total_aid = data['aid_amount_usd'].sum()

        if total_loss == 0:
            return "0.0%"
        
        return f"{(total_aid / total_loss) * 100:.1f}%"
    @render.text
    def kpi_gap():
        """
        Calculate the Aid Gap for the filtered dataset.

        Aid Gap = total economic loss − total aid received.

        Returns
        -------
        str
            Formatted currency string representing the gap.
        """
        data = filtered_df()
        total_loss = data["economic_loss_usd"].sum()
        total_aid = data["aid_amount_usd"].sum()
        gap = total_loss - total_aid
        return format_currency(gap)


app = App(app_ui, server)