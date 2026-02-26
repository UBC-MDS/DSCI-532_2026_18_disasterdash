# CHANGELOG 

## [0.2.0] - 2026-02-28


## Added:

- Deployed stable (`main`) and preview (`dev`) builds to Posit Connect Cloud.
- Implemented global filtering (country, disaster type, date range).
- Added reactive `filtered_df` used by multiple outputs.
- Wired up bar chart and world map visualizations
- Implemented KPI cards (Aid Coverage %, Aid Gap).
- Added summary statistic selector (mean, sum, min, max).
- Reactivity Diagram: Mermaid markup flowchart based on the app sketch and skeleton. 


## Changed:

- The Bar charts were decided to be total sums by default, but also decided to add avg, max, and min cost amounts. 
- The group decided that cividis is the default pallet that we'll use for charting - with possibility of user choice in later versions. 
- Group decided to add an additional filter option to allow the user to select whether they want to view the average, minimum, maximum, or total sum of the economic loss and economic aid for the visualized bar charts. This will allow the policy makers to get a sense of both the central trends of the data and the extreme values in order to inform their policy decisions. 
- The decision was made to add a country's GDP as a tool-tip
- We decided to change our KPI cards from showing the average economic loss and average economic aid across selected disaster types. Because we now have the average shown in the bar chart, and average of the averages isn't particularly meaningful, we pivoted to showing the economic aid to economic loss ratio, and the total amount loss to aid gap as two kpi cards that immediately show the percent of the economic loss covered by aid, and the total amount of money that corresponds to. 

## Fixed:

- Corrected reactive dependency issues in filtered dataset.
- Fixed reset button to restore date range and summary statistic.

## Known Issues:

- Data is limited to only countries surveyed
- Data only goes up to 2024
- Some subsets may produce stable KPI ratios due to proportional aid-loss relationship.

### Reflection:

- Job Stories 1–3 are fully implemented (global filtering and reactive summaries).
- Map and bar chart components are implemented as prototype versions and will be refined in M3.
- Layout evolved from original M1 sketch to improve information hierarchy and align with dashboard best practices.
- Reactive architecture follows Lecture 3 guidance: one central `@reactive.calc` feeding multiple outputs.
- Strength: Strong reactive separation and modular structure.
- Limitation: Visual polish and advanced interactivity deferred to M3.

At this stage, the dashboard successfully demonstrates full reactivity and deployment workflow, though additional visual refinement and deeper interactivity are planned for M3. Overall, the milestone strengthened our understanding of reactive design patterns and deployment structure.

## Future Upgrades: 

- Potential user choice for charting color themes. 