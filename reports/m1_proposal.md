# Disaster Dash: Proposal

## Section 1: Motivation and Purpose

**Our role:** Emergency management data analysts  
**Target audience:** Global aid policy workers analyzing disaster responses worldwide

Global aid policy workers face a critical challenge: understanding where disaster aid responses are insufficient compared to actual economic losses and humanitarian needs. Without clear visibility into the gaps between disaster impacts and aid contributions, policymakers struggle to develop effective policies for improved global disaster response. The complexity of comparing economic losses, aid allocations, and disaster frequency across different regions and disaster types makes it difficult to identify systematic underfunding patterns.

We propose Disaster Dash, an interactive dashboard for exploring global disaster data (2018-2024). Our app will demonstrate global disaster frequency across time with an interactive map (togglable time ranges and disaster type selections), provide direct comparisons of economic losses versus aid responses through dual bar graphs, and display average statistics for immediate benchmarking. This empowers policy workers to identify where aid responses are insufficient, compare regional disparities, and develop evidence-based policies to support improved global disaster response.

## Section 2: Description of the Data

We will visualize a global disaster response dataset (2018-2024) containing thousands of disaster events worldwide with 12 key variables per observation. The dataset includes approximately 50,000+ disaster events. Key variables include:

- **Geographic data** (`country`, `latitude`, `longitude`) - location information for mapping disasters globally
- **Temporal data** (`date`) - when disasters occurred for trend analysis
- **Disaster characteristics** (`disaster_type`, `severity_index`) - classification (Earthquake, Flood, Hurricane, Extreme Heat, Landslide) and intensity rating (0-10 scale)
- **Impact metrics** (`casualties`, `economic_loss_usd`) - human toll and financial losses from disasters
- **Response data** (`response_time_hours`, `aid_amount_usd`, `response_efficiency_score`) - how quickly aid arrived, total aid contributed, and response quality rating
- **Recovery metrics** (`recovery_days`) - time required for affected areas to recover

We will derive key analytical variables including disaster frequency per country, **aid-to-loss ratio** (aid_amount_usd as percentage of economic_loss_usd), **aid coverage gap** (difference between losses and aid), average response time by disaster type and region, and correlation between response_efficiency_score and recovery time to enable policy workers to benchmark aid adequacy and response effectiveness.

## Section 3: Research Questions & Usage Scenarios

### Usage Scenario

Fatima is a policy analyst at a global humanitarian organization preparing recommendations for the 2026 International Disaster Response Framework. She needs to identify where disaster aid responses are systematically insufficient to [explore] the relationship between economic losses and aid contributions, [compare] disaster frequency and aid adequacy across regions, and [identify] policy interventions needed to close aid gaps.

When Fatima opens Disaster Dash, she sees a world heat map showing disaster frequency by country (2018-2024). She filters for floods and observes high frequency in South Asia. Using the economic comparison charts, she notices that while Bangladesh experienced $2.3B in flood losses, international aid contributions totaled only $450M (19.5% coverage). She compares this to the global average aid-to-loss ratio of 32% shown in the summary statistics, revealing a significant underfunding gap.

Based on these findings, Fatima recommends policy changes to increase rapid-response funding mechanisms for flood-prone South Asian regions and advocates for pre-positioned aid agreements that trigger automatically when losses exceed local response capacity.

### User Stories

**User Story 1:**  
As a **global aid policy worker**, I want to **filter disasters by type (floods, earthquakes, hurricanes, droughts)** in order to **identify which disaster types receive disproportionate or insufficient aid responses and develop type-specific funding policies**.

**User Story 2:**  
As a **global aid policy worker**, I want to **view disaster trends over time using adjustable time ranges** in order to **detect if disaster frequency is increasing in certain regions and proactively adjust long-term aid commitments before crises occur**.

**User Story 3:**  
As a **global aid policy worker**, I want to **compare disaster frequency and impacts across countries on a heat map** in order to **identify systematically underserved regions that may need dedicated aid frameworks or bilateral agreements**.

**User Story 4:**  
As a **global aid policy worker**, I want to **compare economic losses directly against aid contributions using side-by-side bar charts with average benchmarks** in order to **quantify aid gaps, identify underfunded disaster responses, and build evidence-based policy recommendations for closing those gaps**.

## Section 4: Exploratory Data Analysis

*Addressing User Story 1 (Filtering by disaster type), we analyzed disaster type distribution globally.*

**Analysis:** The bar chart in `notebooks/eda_analysis.ipynb` reveals remarkably even distribution across all ten disaster types (2018-2024), ranging from 4,896 to 5,130 events (only 5% variation). Landslides are slightly most frequent, droughts least frequent, but no single type dominates.

**Reflection:** This even distribution makes disaster type filtering critical for policy analysis. Since each type occurs at similar frequencies but receives different aid coverage rates, filtering enables identification of systematically underfunded disaster types. Policy workers can identify aid inequities that cannot be explained by disaster rarity, supporting evidence-based recommendations for equitable aid allocation across all disaster categories.

*Key visualizations: (1) Bar chart of disaster type frequency, (2) Geographic heat map of landslides by country, (3) Time series of disaster trends 2018-2024.*

## Section 5: App Sketch & Description

![Disaster Dash App Sketch](../img/sketch.png)

### Dashboard Layout and Components

Disaster Dash features a comprehensive interface designed for rapid data exploration during emergency planning sessions.

**Left Sidebar (Collapsible Control Panel):**

The sidebar houses all filtering controls in an organized menu that can be collapsed via a hamburger menu icon to maximize visualization space.

- **App Header:** "Disaster Dash" branding with toggle collapse menu for expanding/collapsing the control panel
- **Filters Section:**
  - **Country Filter:** Dropdown menu allowing users to select specific countries or "All" for global view
  - **Date Range Selector:** Dual calendar interface with start and end date pickers, enabling precise temporal filtering across the 2018-2024 dataset. Users can select custom date ranges for focused analysis.
  - **Disaster Type Filter:** Radio button selection for filtering by specific disaster categories (earthquake, landslide, flood, hurricane, extreme heat). Radio buttons ensure single-type selection for focused analysis.

**Top Dashboard Area (Summary Statistics Cards):**

Three prominent stat cards display key aggregate metrics:
- **Avg Number of Casualties:** Shows average human toll across selected disasters
- **Avg Recovery Time:** Displays average recovery duration in days
- **Avg Economic Loss in $:** Presents average financial impact in USD

These cards update dynamically based on filter selections, providing immediate context.

**Main Visualization Area (Center):**

- **World Heatmap Visualization:** 
  - Interactive choropleth map showing global disaster data by country
  - Legend displayed on the right showing the gradient scale (0.0 to 1.0 normalized values)
  - Countries shaded by selected metric intensity
  - Supports hover interactions for detailed tooltips
  
- **Economic Loss Bar Chart (Bottom Left):**
  - Vertical bar chart displaying comparative economic losses across four categories (Items 1-4)
  - Y-axis scaled from 0-20 units
  - Clear visual comparison of financial impacts
  
- **Global Economic Aid Bar Chart (Bottom Right):**
  - Vertical bar chart showing aid contributions across four categories (Items 1-4)
  - Y-axis scaled from 0-1000 units
  - Direct comparison with loss chart enables immediate aid gap identification
  - Legend indicates what each item represents

**Navigation Features:**

- **Scroll Bar:** Vertical scroll bar on the right enables navigation through all visualizations without page changes
- **Responsive Legend:** Fixed legend beside the heatmap for constant reference while exploring data

**User Interaction Flow:**

1. User opens dashboard → sees global heatmap with all disasters (2018-2024) and summary stat cards
2. User selects country from dropdown → all visualizations filter to that country
3. User picks date range using dual calendar pickers → map, charts, and stat cards refresh to selected timeframe
4. User selects disaster type via radio button → all components update to show only that disaster type
5. User scrolls down to examine economic loss vs. aid bar charts side-by-side
6. User compares bar chart heights to immediately identify aid coverage gaps
7. User references stat cards for average benchmarks to assess if specific observations are above/below average

**Design Rationale:**

- **Collapsible Sidebar:** Maximizes screen space for visualizations during presentations while keeping all controls accessible
- **Stat Cards Prominence:** Placing average metrics at the top provides immediate context before users dive into detailed visualizations
- **Side-by-Side Bar Charts:** Positioning loss and aid charts adjacently enables instant visual comparison—the core insight for policy workers
- **Radio Button Disaster Filter:** Single-selection prevents overlapping data series, reducing cognitive load and making patterns clearer
- **Integrated Scrollable View:** All visualizations remain on one canvas, eliminating the need to switch between tabs or pages during analysis

This dashboard design empowers global aid policy workers to rapidly identify where disaster aid responses are insufficient, compare losses against aid contributions, and build evidence-based policy recommendations for closing systematic funding gaps.