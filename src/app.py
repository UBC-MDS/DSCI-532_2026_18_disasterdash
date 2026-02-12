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
            # Full Width Main Map Visual
            ui.card(
                ui.card_header("World Map"),
                ui.output_text("world_map"), # Reminder: change to output_plot when ready to actually plot! 
                full_screen=True
            ),
            # Two Bar Charts Visual's for Comparison with KPI Cards
            ui.layout_columns(
                ui.layout_columns(
                    ui.value_box(
                        "Avg Loss ($)",
                        ui.output_text("kpi_average_loss"),
                        fill=False
                    ),
                    ui.card(
                        ui.card_header("Avg Loss ($)"),
                        ui.output_text("plot_loss") # Reminder: change to output_plot when ready to actually plot! 
                    ),
                    col_widths=[12, 12],
                    row_heights=[1, 3]
                ),
                ui.layout_columns(
                    ui.value_box(
                        "Avg Aid ($)",
                        ui.output_text("kpi_average_aid"),
                        fill=False
                    ),
                    ui.card(
                        ui.card_header("Avg Aid ($)"),
                        ui.output_text("plot_aid") # Reminder: change to output_plot when ready to build the code to plot!
                    ),
                    col_widths=[12, 12],
                    row_heights=[1, 3]
                    
                ),
                col_widths=[6, 6]
            ),
            row_heights=[1, 1],
            col_widths=[12, 12]
        )
    ) 
)


def server(input, output, session):
    # World Map Placeholder for Milestone 1

    @output
    @render.text
    def world_map():
        return "World Map with countries coloured by frequency of disaster"
    
    @output
    @render.text
    def plot_loss():
        return "Bar Chart Showing Economic Loss in USD$ by Disaster Type"
    
    @output
    @render.text
    def plot_aid():
        return "Bar Chart Showing Aid Provided in USD$ by Disaster Type"

    @output
    @render.text
    def kpi_average_loss():
        return "$0.00"
    
    @output
    @render.text
    def kpi_average_aid():
        return "$0.00"


app = App(app_ui, server)