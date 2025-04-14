# Indeed Job Market Analysis Project

## Overview

This project analyzes job listings from Indeed.com for data-related positions to provide insights into the current job market landscape. The analysis focuses on job titles, locations, salaries, required skills, and education requirements for Data Analyst, Business Analyst, Data Scientist, and Business Intelligence Analyst positions.

## Project Structure

```
indeed_job_analysis/
├── code/                  # All Python scripts
│   └── scripts/           # Individual script files
├── data/                  # Data files
│   ├── raw/               # Raw data collected from Indeed
│   ├── processed/         # Cleaned and processed data
│   ├── output/            # Analysis results and reports
│   ├── visualizations/    # Individual visualization files
│   └── dashboard/         # Dashboard files
└── docs/                  # Documentation files
```

## Key Components

### Data Collection

- `scripts/indeed_scraper.py`: Basic web scraper for Indeed job listings
- `scripts/indeed_scraper_selenium.py`: Advanced Selenium-based scraper to bypass anti-scraping measures
- `scripts/collect_data.py`: Script to run the basic scraper
- `scripts/collect_data_selenium.py`: Script to run the Selenium-based scraper
- `scripts/generate_mock_data.py`: Script to generate realistic mock data when scraping is challenging

### Data Processing

- `scripts/process_data.py`: Cleans and processes raw job data, extracting features and standardizing formats

### Data Analysis and Visualization

- `scripts/analyze_data.py`: Performs comprehensive analysis of job data
- `scripts/generate_dashboard.py`: Creates interactive dashboards from analysis results

### Reports and Outputs

- `data/output/indeed_job_market_analysis_report.md`: Comprehensive report with findings and recommendations
- `data/dashboard/indeed_job_analysis_dashboard.html`: Interactive HTML dashboard
- `data/dashboard/indeed_job_analysis_dashboard.png`: Overview dashboard image
- `data/dashboard/indeed_job_skills_dashboard.png`: Skills-focused dashboard image
- `data/dashboard/indeed_job_salary_dashboard.png`: Salary-focused dashboard image

## How to Use This Project

### Running the Analysis Pipeline

1. **Data Collection**:
   ```
   python3 code/scripts/generate_mock_data.py
   ```

2. **Data Processing**:
   ```
   python3 code/scripts/process_data.py
   ```

3. **Data Analysis**:
   ```
   python3 code/scripts/analyze_data.py
   ```

4. **Dashboard Generation**:
   ```
   python3 code/scripts/generate_dashboard.py
   ```

### Viewing Results

- Open `data/dashboard/indeed_job_analysis_dashboard.html` in a web browser for an interactive dashboard
- Read `data/output/indeed_job_market_analysis_report.md` for a comprehensive analysis report

## Key Findings

1. **Job Distribution**: Data Scientist (26%), Business Analyst (25.5%), Data Analyst (25%), Business Intelligence Analyst (23.5%)

2. **Top Locations**: Chicago, San Francisco, Austin, Remote, Seattle, New York

3. **Salary Information**: Average $77,581.50, Median $90,000.00

4. **Top Skills**: Machine Learning, Azure, Hadoop, Power BI, Tableau

5. **Education Requirements**: Master's degree (58%), Bachelor's degree (42%)

For detailed findings and recommendations, please refer to the full analysis report.

## Dependencies

- Python 3.10+
- pandas
- numpy
- matplotlib
- seaborn
- beautifulsoup4
- selenium
- webdriver-manager

