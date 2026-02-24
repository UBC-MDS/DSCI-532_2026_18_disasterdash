from shiny import App, ui, render, reactive

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
            ui.input_checkbox_group(
                id="countries", 
                label="Countries", 
                choices={c: c for c in COUNTRIES},
                selected=COUNTRIES,
            ),
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
            ui.input_date_range(
                id="date_range", 
                label="Date Range",
                start="2018-01-01",
                end="2024-12-31",
                min="2018-01-01",
                max="2024-12-31"
            ),
            ui.input_checkbox_group(
                id="disaster_type",
                label="Disaster Type",
                choices={d: d for d in DISASTER_TYPES},
                selected=DISASTER_TYPES,
            ),
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
        ui.layout_columns(
            #  World Map and KPI's
            ui.card("World Map: Countries coloured by number of disasters", full_screen=True),
            ui.layout_columns(
                ui.card('Kpi Card: Loss Ratio $'),
                ui.card('Kpi Card: Aid Gap $'), 
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
    pass

app = App(app_ui, server)