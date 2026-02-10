# DSCI-532_2025_18_DisasterDash

## About

Disaster Dash is an interactive dashboard for exploring global disaster data through simple, clear visualizations. Users can filter by disaster type and time range to view heat maps showing disaster frequency by country, along with other metrics.

This dashboard is a group project for the Master of Data Science program at the University of British Columbia, DSCI 532: Data Visualization.

## Running the Dashboard Locally

1. Clone this repository
```bash
git clone https://github.com/UBC-MDS/DSCI-532_2025_18_DisasterDash.git
cd DSCI-532_2025_18_DisasterDash
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

5. Open your browser to the URL shown in the terminal (typically `http://localhost:8000`)

## License
Licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.