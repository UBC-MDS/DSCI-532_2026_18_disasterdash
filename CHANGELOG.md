# CHANGELOG 

## [0.4.0] - 2026-03-15

### Added

- **AI tab conditional rendering:** sidebar filter controls and the active filter strip are now hidden when the AI Explorer tab is active and restored when returning to the Overview tab (`ui.panel_conditional` keyed on `input.main_tabs`).
- **AI response style control:** added `ai_response_style` dropdown (`Concise Analyst` / `Policy Brief` / `Step-by-Step`) in the AI sidebar; changes live-update the QueryChat system prompt via `_update_prompt_for_style()` reactive effect.
- **Strengthened system prompt:** `AI_EXTRA_INSTRUCTIONS` injects full column schema, dataset date range, user-goal framing ("policy analyst studying aid gaps"), and explicit tool-use rules (tool call required for all count/filter/rank queries; no fabricated numbers).
- **Improved AI greeting and examples:** `AI_GREETING` contains 8 intent-diverse example prompts covering count, filter, compare, rank, and trend questions.
- **Improved in-tab usage instructions:** `ai_instructions()` render function shows style-aware usage tips and explains how results propagate to the data table and charts below the chat.
- **`on_tool_request` interception:** `_on_tool_request()` enforces an allowlist of permitted tool names, blocks SQL mutation statements (DROP/INSERT/UPDATE/DELETE/ALTER/CREATE), and transforms ambiguous "how many" queries to `SELECT COUNT(*)` via `force_count_query()`.
- **Tool result auditing:** `_on_tool_result()` logs each tool response (row count, success/error) into `tool_audit` reactive value; `ai_query_status` panel in the AI tab surfaces the last tool event, active SQL, and dataframe sync status.
- **Dataframe synchronisation verification:** `_verify_ai_sync()` reactive effect compares `ai_df()` row count against the active SQL from `qc_vals.sql()` and sets `ai_sync_status` warning when they diverge.
- **SQL helper utilities:** `normalize_sql()`, `is_read_only_sql()`, `is_count_intent()`, `force_count_query()` added as standalone pure functions for testability.
- **Experiments notebook:** `notebooks/ai_assistant_experiments.ipynb` — 9 cells covering 3 experiments (prompt strategy, tool interception policy, user-facing control), each with scoring criteria, weighted score tables, and narrative motivation for the selected option.
- **Spec decision table:** `reports/m2_spec.md` updated with experiment-backed "Decision Summary" table recording the selected option and motivation for all four design dimensions.
- **Auto-load `.env` at startup:** `load_dotenv()` (python-dotenv) called before the API key check so developers can store `ANTHROPIC_API_KEY` in a gitignored `.env` file instead of exporting it in every shell session.
- **ibis-framework installed:** added `ibis-framework[duckdb]` to the environment so the app can start (`ibis` was missing from the `disaster-dash` conda environment despite being used in the data-loading layer).

### Changed

- Migrated AI backend from GROQ to **Anthropic Claude Haiku** (`claude-3-haiku-20240307`) via `chatlas.ChatAnthropic`; environment variable changed from `GROQ_API_KEY` to `ANTHROPIC_API_KEY`.
- `QC_BASE_SYSTEM_PROMPT` now captures QueryChat's default prompt at startup so style overrides can append to it rather than replace it entirely, preserving QueryChat's built-in tool descriptions.
- Addressed: AI Explorer tab shows non-AI sidebar controls and filter strip when on the AI tab — resolved by `ui.panel_conditional` wrapping the overview sidebar section and the `filter_strip` row.
- Addressed: AI assistant produces hallucinated numeric answers — resolved via `AI_EXTRA_INSTRUCTIONS` strict tool-use rules and `_on_tool_request` count-query transformation.
- Addressed: No user control over AI response style — resolved by `ai_response_style` dropdown and `_update_prompt_for_style()`.
- Addressed: Design decisions lacked documented experiment rationale — resolved by `notebooks/ai_assistant_experiments.ipynb` and the spec decision table.

### Fixed

- Startup crash when `ANTHROPIC_API_KEY` is not exported in the shell — fixed by calling `load_dotenv()` before the key check so `.env` is read automatically.
- Argument ordering `SyntaxError` in `ui.nav_panel` call introduced during initial AI tab wiring — corrected before commit `529d814`.

### Known Issues

- The app requires `ANTHROPIC_API_KEY` to start; without it the process exits immediately. There is no graceful degradation mode that allows the Overview tab to function without the AI key.
- `_verify_ai_sync()` logs a mismatch warning when the user has not yet run any AI query (initial state: `ai_df` is the full dataset, `qc_vals.sql()` is empty). This is a false-positive on first load.
- The experiments notebook contains manually recorded scores (no automated re-run harness); scores are representative of observed behaviour during development, not a reproducible benchmark suite.
- Demo GIF in README is still from M3 and does not show the AI tab enhancements.

### Release Highlight: AI Explorer Tab — Enhanced Conversational Data Analysis

The AI Explorer tab allows policy analysts to ask natural-language questions about the global disaster aid dataset (2018–2024) and receive grounded, reproducible answers backed by live DuckDB queries. This milestone hardened the AI layer: the system prompt now gives the LLM full schema context and strict tool-use rules, a response style dropdown lets users switch between concise, policy-brief, and step-by-step formats, and an `on_tool_request` interceptor both validates SQL safety and transforms ambiguous count queries into explicit `SELECT COUNT(*)` calls. The result is an assistant that answers "how many flood events occurred in India after 2020?" with an actual database count rather than a hallucinated number.

- **Option chosen:** Option D (AI-powered natural language querying with QueryChat + chatlas)
- **PR:** `ai_tab` branch → commits `529d814`, `062ee57`, `72f024a`, `9de62b8`, `ccfa07d`
- **Why this option over the others:** Options A–C were conventional filter or chart extensions. Option D adds a fundamentally different analysis mode — natural-language SQL generation against the live dataset — that supports open-ended policy questions the fixed filter UI cannot express. The experiment notebook (`notebooks/ai_assistant_experiments.ipynb`) documents why the strengthened system prompt and `on_tool_request` transform were selected over simpler alternatives.
- **Feature prioritization issue link:** <!-- link to your feature prioritization issue -->

### Collaboration

This milestone focused on improving documentation discipline and reducing large-batch commits. The `ai_tab` branch used six focused commits rather than a single integration PR, each scoped to one logical change (UI changes, prompt/server logic, notebook, spec, dotenv fix). All design decisions were recorded in the spec before implementation.

- **CONTRIBUTING.md:** Updated during M3 with Milestone 3 retrospective and Milestone 4 collaboration norms (atomic PRs, design-before-code, consistent peer review, clear PR descriptions). See commit history on `main`.
- **M3 retrospective:** After M3 collaboration feedback we identified that large integration PRs and spec lag were the main friction points. We addressed both: specs are now updated alongside code changes, and the M4 feature branch uses commit-per-logical-unit rather than one large merge commit.
- **M4:** Applied design-before-code discipline — the spec's "AI Assistant Enhancements" section was written first, then each feature was implemented and immediately committed with a reference message, keeping the spec and code in sync throughout.

### Reflection

Disaster Dash successfully communicates the global disaster aid gap story at a glance: the choropleth, KPI cards, and bar charts give policy analysts an immediate comparative view across countries, disaster types, and years. The AI Explorer adds an open-ended layer for questions the fixed filter UI cannot express. Current limitations include dataset coverage (only surveyed countries, only through 2024), the lack of trend/time-series charts on the Overview tab, and the hard dependency on an Anthropic API key at startup. We intentionally omit statistical uncertainty bands on bar aggregates — the dataset is a survey sample, not a census, but adding confidence intervals would require assumptions about the sampling design we cannot verify from the raw data alone.

The biggest trade-off this milestone was depth over breadth: we invested heavily in making the AI layer reliable (prompt engineering, tool interception, sync verification) rather than adding new chart types. Full rationale is in `notebooks/ai_assistant_experiments.ipynb` and the Decision Summary table in `reports/m2_spec.md`.

The most formative materials this milestone were the chatlas/QueryChat documentation (understanding `on_tool_request` hook semantics) and the in-class discussion of prompt engineering for structured outputs. We would have benefited from earlier coverage of how to test LLM-backed components in a reactive Shiny context — there is currently no automated test harness for the AI tab's tool interception logic.


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