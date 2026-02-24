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

app = App(app_ui, server)