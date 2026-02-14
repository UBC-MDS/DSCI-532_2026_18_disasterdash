from shiny import App, ui, render

app_ui = ui.page_fillable(
    ui.panel_title("Disaster Dash"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_selectize(
                id="countries", 
                label="Countries", 
                choices=["Australia", "Bangladesh", "Brazil","Canada", "Chile", "China", "France", "Germany", "Greece", "India", 
                         "Indonesia", "Italy", "Japan", "Mexico", "Nigeria", "Philippines", "South Africa", "Spain", "Turkey", "United States"],
                selected=["Australia", "Bangladesh", "Brazil","Canada", "Chile", "China", "France", "Germany", "Greece", "India", 
                         "Indonesia", "Italy", "Japan", "Mexico", "Nigeria", "Philippines", "South Africa", "Spain", "Turkey", "United States"],
                multiple=True
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
                id="checkbox_group",
                label="Disaster Type",
                choices={
                    "Drought": "Drought", 
                    "Earthquake": "Earthquake", 
                    "Extreme Heat": "Extreme Heat", 
                    "Flood": "Flood",
                    "Hurricane": "Hurricane",
                    "Landslide": "Landslide",
                    "Storm Surge": "Storm Surge",
                    "Tornado": "Tornado",
                    "Volcanic Eruption": "Volcanic Eruption",
                    "Wildfire": "Wildfire"
                },
                selected=[
                    "Drought", 
                    "Earthquake",
                    "Extreme Heat",
                    "Flood",
                    "Hurricane",
                    "Landslide",
                    "Storm Surge",
                    "Tornado",
                    "Volcanic Eruption",
                    "Wildfire"
                ],
            ),
            ui.input_action_button("action_button", "Reset filter"),
            open="desktop",
        ),
        ui.layout_columns(
            #  World Map and KPI's
            ui.card("World Map: Countries coloured by number of disasters", full_screen=True),
            ui.layout_columns(
                ui.card('Kpi Card: Avg Loss $'),
                ui.card('Kpi Card: Avg Aid $'), 
                col_widths=[12, 12],
                row_heights=[1, 1]
            ),
            col_widths=[9,3]
        ),
        ui.layout_columns(
            # Bar Charts 
            ui.card("Bar Chart of Economic Loss by Disaster Type($)"),
            ui.card("Bar Chart of Economic Aid by Disaster Type ($)"),
            col_widths=[6, 6]
        ),
    )
)


def server(input, output, session):
    pass

app = App(app_ui, server)