# Disaster Dash

## About

Disaster Dash is an interactive dashboard to provide data to assist with Global Disaster Aid Policy development. Users can see the frequency of disasters on a World Map, and filter by disaster type, dates, and countries. By using our dashboard, a policy developer can immediately see the most frequent disasters around the world, and compare the economic loss and global aid response provided through simple, clear visualizations.

This dashboard is a group project for the Master of Data Science program at the University of British Columbia, DSCI 532: Data Visualization, 2025-26 Cohort.

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

4. Run the dashboard
```bash
shiny run src/app.py
```

5. Open your browser to the URL shown in the terminal.

## License

Software licensed under the MIT License. Content licensed under CC BY 4.0. See [LICENSE.md](LICENSE.md) for details.

