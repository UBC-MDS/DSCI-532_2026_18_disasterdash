# M2 Specification — Disaster Dash

## Updated Job Stories

| # | Job Story | Status | Notes |
|---|-----------|--------|-------|
| 1 | When I am analyzing disaster aid policy, I want to filter disasters by type (floods, earthquakes, hurricanes, droughts) so I can identify which disaster types receive disproportionate or insufficient aid responses and develop type-specific funding policies. | ✅ Implemented | Multi-select disaster type filter with quick select/deselect buttons.|
| 2 | When I am reviewing long-term disaster trends, I want to view disaster frequency over time using adjustable date ranges so I can detect if disaster frequency is increasing in certain regions and proactively adjust long-term aid commitments. | ✅ Implemented | Adjustable date range filter in the sidebar. |
| 3 | When I am comparing regional disaster impacts, I want to view disaster frequency and impacts across countries on an interactive choropleth map so I can identify systematically underserved regions that may need dedicated aid frameworks or bilateral agreements. | ✅ Implemented | Map metric selector allows switching between frequency, aid coverage %, casualties, and economic loss. |
| 4 | When I am building evidence-based policy recommendations, I want to compare economic losses directly against aid contributions using side-by-side bar charts with configurable summary statistics (average, minimum, maximum, or total) and summary KPIs so I can quantify aid gaps from multiple analytical perspectives and identify underfunded disaster responses. | ✅ Implemented | Bar charts are vertical for clear comparison.  Summary statistic selector (mean, sum, min, max).  |
| 5 | When I want to explore the dataset more flexibly, I want to ask natural language questions about disasters so I can quickly generate filtered views of the data without manually adjusting multiple filters. | ✅ Implemented | Implemented via the AI Explorer tab using QueryChat. |


## Component Inventory

| ID | Type | Shiny widget / renderer | Depends on | Job story |
|----|------|------------------------|------------|-----------|
| `countries` | Input | `ui.input_selectize()` (multi-select) | — | #2, #3 |
| `sel_all_c` | Input | `ui.input_action_button()` | — | #2, #3 |
| `desel_all_c` | Input | `ui.input_action_button()` | — | #2, #3 |
| `date_range` | Input | `ui.input_date_range()` | — | #2 |
| `disaster_type` | Input | `ui.input_selectize()` (multi-select) | — | #1 |
| `sel_all_d` | Input | `ui.input_action_button()` | — | #1 |
| `desel_all_d` | Input | `ui.input_action_button()` | — | #1 |
| `summary_stat` | Input | `ui.input_select()` | — | #1, #2, #3, #4 |
| `map_metric` | Input | `ui.input_select()` | — | #3 |
| `reset_button` | Input | `ui.input_action_button()` | — | #1, #2, #3, #4 |
| `disaster_table` | Data source | ibis table backed by DuckDB | parquet dataset | #1, #2, #3, #4 |
| `filtered_query` | Reactive calc | `@reactive.calc` (lazy ibis query) | `countries`, `date_range`, `disaster_type` | #1, #2, #3, #4 |
| `filtered_df` | Reactive calc | `@reactive.calc` (query execution) | `filtered_query` | #1, #2, #3, #4 |
| `filter_strip` | Output | `@render.ui` | `countries`, `date_range`, `disaster_type`, `summary_stat`, `map_metric` | #1, #2, #3, #4 |
| `kpi_grid` | Output | `@render.ui` | `filtered_df` | #1, #3, #4 |
| `map_plot` | Output | `@render_widget` (Plotly choropleth) | `filtered_df`, `map_metric` | #2, #3 |
| `bar_loss` | Output | `@render_widget` (Plotly bar) | `filtered_df`, `summary_stat` | #1, #3, #4 |
| `bar_aid` | Output | `@render_widget` (Plotly bar) | `filtered_df`, `summary_stat` | #1, #3, #4 |
| `chat` | Output | `querychat` UI component | — | #5 |
| `ai_df` | Reactive calc | QueryChat filtered dataframe | `chat` | #5 |
| `ai_table` | Output | `@render.data_frame` | `ai_df` | #5 |
| `download_ai_csv` | Output | `@render.download` | `ai_df` | #5 |
| `ai_bar_loss` | Output | `@render_widget` (Plotly bar) | `ai_df` | #5 |
| `ai_bar_aid` | Output | `@render_widget` (Plotly bar) | `ai_df` | #5 |


## Reactivity Diagram

```mermaid
flowchart TD
    A[/countries/] --> Q{{filtered_query}}
    B[/date_range/] --> Q
    C[/disaster_type/] --> Q

    Q --> F{{filtered_df}}

    D[/map_metric/] --> Map
    D --> Strip
    E[/summary_stat/] --> BarLoss
    E --> BarAid
    E --> Strip

    F --> Map([map_plot: Choropleth])
    F --> KPI([kpi_grid: KPI Cards])
    F --> BarLoss([bar_loss: Economic Loss by Type])
    F --> BarAid([bar_aid: Aid Amount by Type])
    F --> Strip([filter_strip: Active Filter Banner])


    Chat[/QueryChat Interface/] --> AI{{ai_df}}
    AI --> Table([ai_table: Filtered Data Table])
    AI --> AILoss([ai_bar_loss])
    AI --> AIAid([ai_bar_aid])
    AI --> Download([download_ai_csv])
```

## Calculation Details

### `filtered_query`
- **Depends on:** `countries`, `date_range`, `disaster_type`
- **Transformation:** Constructs a lazy DuckDB query using ibis that filters the Parquet dataset according to the selected countries, disaster types, and date range.
- **Execution:** No computation occurs at this stage. The query remains lazy and represents a database expression that will only be executed when consumed by a downstream reactive.
- **Consumed by:** `filtered_df`

### `filtered_df`
- **Depends on:** `filtered_query`
- **Transformation:** Executes the lazy DuckDB query using `.execute()` and materializes the filtered result as a pandas DataFrame.
- **Purpose:** This reactive caches the query result so that multiple outputs (map, bar charts, and KPIs) can reuse the same dataframe without triggering repeated database queries.
- **Consumed by:** `kpi_grid`, `map_plot`, `bar_loss`, `bar_aid`, `filter_strip`

### Bar Chart Aggregation (inline)
- **Depends on:** `filtered_df`, `summary_stat`
- **Transformation:** Groups the filtered dataset by `disaster_type` and applies the selected summary statistic (`mean`, `sum`, `min`, or `max`) to `economic_loss_usd` (for `bar_loss`) and `aid_amount_usd` (for `bar_aid`). 
- **Consumed by:** `bar_loss`, `bar_aid`

### KPI Calculations

### `kpi_grid` — Average Unfunded Loss per Disaster
- **Formula:** `mean(loss − aid)` where `loss = economic_loss_usd` and `aid = aid_amount_usd`
- **Meaning:** Represents the typical funding gap per disaster event within the filtered selection.
- **Baseline comparison:** The filtered value is compared to the **global historical average disaster funding gap**, computed as the mean disaster funding gap across all disaster events in the dataset (2018–2024).

### `kpi_grid` — Disaster Burden (% of GDP)
- **Formula:** `median((economic_loss_usd - aid_amount_usd) / GDP × 100)` computed at the country level.
- **Meaning:** Represents the typical disaster funding gap relative to a country's economic size, allowing comparison between large and small economies.
- **Baseline comparison:** The filtered value is compared to the **global median disaster burden**, computed as the median country-level disaster burden across all countries in the dataset (2018–2024).

These KPI calculations are independent of the `summary_stat` selection used in the bar charts. The first KPI computes the **average disaster funding gap**, while the second KPI computes the **median disaster burden relative to GDP**.

The dashboard displays ▲ or ▼ indicators to show whether the selected disasters exhibit **larger or smaller funding gaps relative to global historical baselines**.

### Map Aggregation (inline)
- **Depends on:** `filtered_df`, `map_metric`
- **Transformation:** Groups by `country`, computes disaster count, total casualties, total economic loss, total aid, average severity, average response time, and aid coverage %. The selected `map_metric` controls which variable drives the choropleth colour scale.


## Complexity Enhancement

### Reset All Filters Button

To improve usability and demonstrate event-driven reactivity, we implemented a **Reset All Filters** button that restores every global input to its default state.

This feature uses `@reactive.event()` in combination with `@reactive.effect()` to programmatically update all filter widgets when the reset button is clicked.

### Why This Enhances the Dashboard

* Allows users to quickly recover from overly restrictive filter combinations
* Prevents “empty state” traps during exploratory analysis
* Improves workflow efficiency when comparing multiple scenarios
* Demonstrates correct event-based reactive architecture

## Data Access Architecture

To improve performance and scalability, the dashboard reads data from a **Parquet dataset** using **DuckDB via ibis**.

Instead of loading the entire dataset into memory, user-selected filters are translated into a database query that is executed lazily. Only rows matching the selected filters are materialized into a pandas DataFrame when required by downstream reactive components.

This approach ensures that filtering occurs at the database level and allows the dashboard to scale to larger datasets while keeping memory usage low.

To avoid repeated database execution across multiple outputs, the dashboard uses a two-stage reactive pipeline:

1. `filtered_query` constructs a lazy ibis query that applies user-selected filters at the DuckDB level.
2. `filtered_df` executes this query once and caches the resulting pandas DataFrame.

This ensures that DuckDB executes the query only once per reactive update cycle even when multiple visual components depend on the same filtered dataset.

## AI Explorer Tab

To extend the analytical capabilities of the dashboard, Milestone 3 introduced an **AI Explorer tab** powered by QueryChat.

This feature allows users to interact with the disaster dataset using **natural language queries**. The system translates user queries into SQL filters that dynamically update the dataset used for visualization.

Example queries include:

- "Show floods in India after 2020"
- "Which country had the highest economic loss?"
- "Filter events with over 1000 casualties"

### AI Outputs

The AI Explorer tab produces:

- A **filtered data table** showing query results
- A **CSV download button** for exporting filtered results
- Two bar charts summarizing:
  - Economic loss by disaster type
  - Aid amount by disaster type

These charts are computed using **sum aggregation** and update automatically based on the AI-filtered dataset.
