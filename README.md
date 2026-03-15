<p align="center">
<img width="894" height="77" alt="DASH" src="https://github.com/user-attachments/assets/f17f67b4-3ce2-4588-b95e-7ea74aa049ab" />
<br><br>
<img src="https://github.com/user-attachments/assets/8bf34fc7-8ff1-417c-b6de-e034403306ed" width="600" height="400" />
</p>

## About

Global aid policy workers face a critical challenge: understanding where disaster aid responses are insufficient compared to actual economic losses. Without a clear understanding of the aid gaps, policymakers may struggle to develop effective responses to global disasters.

**Disaster Dash** is an interactive dashboard that makes these gaps visible. Users can explore global disaster frequency on a World Map, filter by disaster type, dates, and countries, and directly compare economic losses against aid responses through coordinated visualizations.

The dashboard also includes an **AI Explorer** that allows users to query the dataset using natural language.

This dashboard is a group project for the Master of Data Science program at the University of British Columbia, DSCI 532: Data Visualization, 2025-26 Cohort.

## Live Dashboard

| Build | URL |
|-------|-----|
| Stable (main) | [disasterdash-stable](https://clr-saunders-dsci-532-2026-18-disasterdash-stable.share.connect.posit.cloud)|
| Preview (dev) | [disasterdash-preview](https://clr-saunders-dsci-532-2026-18-disasterdash-preview.share.connect.posit.cloud)|


## Running the Dashboard Locally

1. Clone this repository

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_18_disasterdash.git
cd DSCI-532_2026_18_disasterdash
```

2. Create the conda environment
```bash
conda env create -f environment.yml
```

3. Activate the environment
```bash
conda activate disaster-dash
```

4. Configure environment variables

The **AI Explorer** tab uses the **Anthropic API** to power natural-language queries.

To run the dashboard locally, you must provide an Anthropic API key.

- Create an API key at:  
  https://console.anthropic.com/

- In the project root, create a `.env` file:

```bash
touch .env
```

- Add your API key to the file:

```bash
ANTHROPIC_API_KEY=your_key_here
```

The application automatically loads this key using `python-dotenv`.

> **Note:** 
The `.env` step is required to run the dashboard locally. 
The `.env` file is listed in `.gitignore` and should **never be committed to the repository**.


5. Run the dashboard

```bash
shiny run src/app.py
```

6. Open your browser to the URL shown in the terminal.


## Running Tests

The test suite verifies core dashboard behaviors including filtering logic, aggregation correctness, and UI interactions.

1) Install Playwright browser dependencies (required once):

```bash
playwright install
```

2) Run all tests:

```bash 
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Contributors

| Name | GitHub |
|------|--------|
| Ojasv Issar | [@Ojasv-Issar](https://github.com/Ojasv-Issar) |
| Joel Nicholas Peterson | [@j031nich0145](https://github.com/j031nich0145) |
| Claire Saunders | [@clr-saunders](https://github.com/clr-saunders) |

## License

Software licensed under the MIT License. Content licensed under CC BY 4.0. See [LICENSE.md](LICENSE.md) for details.
