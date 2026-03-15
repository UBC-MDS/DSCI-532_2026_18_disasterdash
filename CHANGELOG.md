# CHANGELOG 

## [0.3.0] - 2026-03-08

## Added:

- Implemented a new **AI Explorer tab** featuring a QueryChat interface for natural-language filtering of the disaster dataset.
- Added a reactive dataframe output displaying the AI-filtered dataset.
- Added a data download button to export the AI-filtered dataframe.
- Added CSV export functionality for AI-filtered query results.
- Added GDP-normalized disaster burden metric using **World Bank 2024 GDP data**.
- Added explanatory subtitles and formulas to KPI cards to clarify metric calculations.

## Changed:

- Replaced **Aid Coverage %** and **Funding Gap** KPI cards with:
  - **Total Unfunded Disaster Losses**
  - **Disaster Burden (% of GDP)**
- Default setting for filters updated to be just the top three countries with the highest total economic losses from disasters for a clearer comparative story. 
- Relabeled side panel option "Summary Statistic" to "Bar Chart Statistic" to clarify it only corresponds to the Bar Chart. Updated in the active filter panel as well. 
- Reordered filters to be more logically clear for the user: Countries -> Disasters -> Dates -> Map Metric -> Bar Chart Summary
- Changed the map colour scheme from cividis to viridis so that there is more visual difference across the continuous scale 
- Updated default dashboard behaviour so the map automatically centers and zooms based on filtered countries rather than showing the full world extent
- Updated ReadMe document to reflect new AI integration panel requiring a .env file for developers to run the app locally
- Added support for `GROQ_API_KEY` environment variable to enable the AI QueryChat interface locally and in deployment environments.
- Added automatic map zoom to selected countries to improve visual function of the map
- Added active map titles that adjusted based upon the selected map metric to more clearly demonstrate the policy quesion answered by the map visual
- Flipped all bar charts vertically aligned with some scaling
- Changed the bar chart color themes to the more moderate 'teal' 

## Fixed:

- Removed decorative KPI icons that were not tied to meaningful analytical comparisons.
- Updated KPI cards to improve interpretability based on instructor feedback.
- Refined KPI typography and spacing to improve readability and visual hierarchy.
- Improved layout margins and colorbar spacing to prevent overlap with the map canvas
- Improved scaling and granularity in bar charts for easier interpretability

## Known Issues:

- Data is limited to only countries surveyed.
- Data only goes up to 2024.
- Demo GIF performs demo on posit cloud build with some lag and lower resolution from browser recording
- Demo GIF out of date with current dashboard


## Reflection:

This milestone focused on integrating an AI-powered exploration interface and improving the interpretability of our key metrics. The new AI Explorer tab uses QueryChat to allow natural-language filtering of the dataset, reinforcing our understanding of reactive data flows and how to isolate multiple reactive pipelines within a single Shiny application.

We also redesigned the KPI cards, defualt filters and some visual elements of our map display based on instructor feedback. We replaced Aid Coverage % and Funding Gap with Total Unfunded Disaster Losses and Disaster Burden (% of GDP) to provide clearer context about both the absolute funding gap and the relative economic impact of disasters. We adjusted the map to automatically zoom in to the selected countries, and set a clear title to frame the policy question that the map visual answers for clear storytelling. Finally, we updated our default filters to show the top three countries with high disaster losses as the default selection, with total loss as the default metric. This supports an immediate policy comparison of the top three countries with the largest disaster losses, it shows the regional spread and the countries most in need of aid policy efforts. 

Finally, integrating the AI assistant required managing environment variables for the GROQ API key, highlighting the importance of handling external service dependencies securely across local and deployed environments.

## Future Upgrades 

- Demo run locally with higher quality screen recording software on our latest version


## [0.2.0] - 2026-02-28


## Added:

- Deployed stable (`main`) and preview (`dev`) builds to Posit Connect Cloud.
- Implemented global filtering (country, disaster type, date range).
- Added reactive `filtered_df` used by multiple outputs.
- Wired up bar chart and world map visualizations.
- Implemented KPI cards (Aid Coverage %, Aid Gap).
- Added summary statistic selector (mean, sum, min, max).
- Reactivity Diagram: Mermaid markup flowchart based on the app sketch and skeleton.
- Added map metric selector to switch choropleth between disaster frequency, aid coverage %, casualties, and economic loss.
- Added active filter strip banner displaying current filter state at a glance.
- Added "None" deselect buttons alongside existing "All" buttons for country and disaster type filters.
- Added empty state placeholders across all chart panels when no data matches the current filters.
- Implemented optional complexity enhancement: Reset All Filters button using `@reactive.event` and `@reactive.effect` to programmatically restore all inputs to default values.


## Changed:

- The bar charts were decided to be total sums by default, but also decided to add avg, max, and min cost amounts.
- The group decided that cividis is the default palette that we'll use for charting — with possibility of user choice in later versions.
- Group decided to add an additional filter option to allow the user to select whether they want to view the average, minimum, maximum, or total sum of the economic loss and economic aid for the visualized bar charts. This will allow the policy makers to get a sense of both the central trends of the data and the extreme values in order to inform their policy decisions.
- The decision was made to add a country's GDP as a tool-tip.
- We decided to change our KPI cards from showing the average economic loss and average economic aid across selected disaster types. Because we now have the average shown in the bar chart, and average of the averages isn't particularly meaningful, we pivoted to showing the economic aid to economic loss ratio, and the total amount loss to aid gap as two KPI cards that immediately show the percent of the economic loss covered by aid, and the total amount of money that corresponds to.
- Switched country and disaster type inputs from checkbox groups to searchable multi-select (selectize) widgets.
- Bar charts converted from vertical to horizontal orientation for improved disaster type label readability.
- KPI cards reduced from 4 to 2 — removed Disaster Events and Casualties cards, retained Aid Coverage % and Funding Gap.
- Updated typography to Syne (display) and Instrument Sans (body).
- Page header updated to display live dataset-level stats (total records, countries, disaster types).


## Fixed:

- Corrected reactive dependency issues in filtered dataset.
- Fixed reset button to restore date range and summary statistic.
- Fixed accessibility issue where input labels were set to `display:none` — now visually hidden but readable by screen readers.


## Known Issues:

- Data is limited to only countries surveyed.
- Data only goes up to 2024.
- Some subsets may produce stable KPI ratios due to proportional aid-loss relationship.
- Demo GIF performs demo on posit cloud build with some lag and lower resolution from browser recording


## Reflection:

- Job Stories 1–4 are fully implemented (global filtering, reactive summaries, bar charts with configurable statistics, and KPI cards).
- Map and bar chart components are implemented as prototype versions and will be refined in M3.
- Layout evolved from the original M1 sketch to a single-page overview design with a dominant choropleth map, two KPI cards (Aid Coverage % and Funding Gap), and horizontally oriented bar charts for improved readability and clearer emphasis on aid gaps.
- Reactive architecture follows Lecture 3 guidance: a central `filtered_df` reactive calc feeds multiple outputs, with bar chart aggregation applied inline per chart.
- Strength: Strong reactive separation and modular structure.
- Limitation: Visual polish and advanced interactivity deferred to M3.
- Implemented the optional complexity enhancement (Reset All Filters button) to improve workflow and demonstrate event-based reactivity.

At this stage, the dashboard successfully demonstrates full reactivity and deployment workflow, though additional visual refinement and deeper interactivity are planned for M3. Overall, the milestone strengthened our understanding of reactive design patterns and deployment structure.


## Future Upgrades: 

- Potential user choice for charting color themes.
- Demo run locally with higher quality screen recording software