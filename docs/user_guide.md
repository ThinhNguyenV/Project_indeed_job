# Indeed Job Market Analysis - User Guide

This guide provides instructions for using and extending the Indeed Job Market Analysis project.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - beautifulsoup4
  - selenium
  - webdriver-manager

### Installation

1. Unzip the project archive to your desired location
2. Navigate to the project directory
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Using the Project

### Viewing Existing Results

1. **Dashboard**: Open `data/dashboard/indeed_job_analysis_dashboard.html` in any web browser to view the interactive dashboard.

2. **Analysis Report**: Open `data/output/indeed_job_market_analysis_report.md` in a Markdown viewer or text editor to read the comprehensive analysis.

3. **Visualizations**: Browse individual visualization files in the `data/visualizations/` directory.

### Running the Analysis Pipeline

To rerun the analysis with existing data:

1. **Process Data**:
   ```
   python code/scripts/process_data.py
   ```

2. **Analyze Data**:
   ```
   python code/scripts/analyze_data.py
   ```

3. **Generate Dashboards**:
   ```
   python code/scripts/generate_dashboard.py
   ```

### Collecting New Data

To collect fresh data from Indeed:

1. **Using Mock Data Generator** (recommended for testing):
   ```
   python code/scripts/generate_mock_data.py
   ```

2. **Using Web Scraper** (may be limited by Indeed's anti-scraping measures):
   ```
   python code/scripts/collect_data.py
   ```

3. **Using Selenium Scraper** (more robust but slower):
   ```
   python code/scripts/collect_data_selenium.py
   ```

## Customizing the Analysis

### Modifying Search Parameters

To change the job titles or locations being analyzed:

1. Edit the `SCRAPING_CONFIG` dictionary in `code/scripts/config.py`
2. Update the job titles and locations lists
3. Rerun the data collection and analysis pipeline

### Adding New Visualizations

To create additional visualizations:

1. Modify `code/scripts/analyze_data.py` to add new analysis functions
2. Update `code/scripts/generate_dashboard.py` to include the new visualizations in the dashboards

### Extending the Report

To add new sections to the analysis report:

1. Edit `data/output/indeed_job_market_analysis_report.md` directly
2. Or modify the report generation code if you're creating it programmatically

## Troubleshooting

### Common Issues

1. **Scraper Blocked by Indeed**:
   - Use the mock data generator instead
   - Increase delay between requests in config.py
   - Try using different user agents

2. **Visualization Errors**:
   - Ensure seaborn and matplotlib are properly installed
   - Check that the data files exist in the expected locations

3. **Dashboard Not Loading**:
   - Verify that all referenced image files exist
   - Check HTML file for correct paths to images

### Getting Help

For additional assistance or to report issues, please contact the project maintainer.

## Advanced Usage

### Adding New Job Platforms

To extend the analysis to other job platforms:

1. Create a new scraper module following the pattern in `indeed_scraper.py`
2. Ensure the output format matches the expected structure
3. Modify the processing script to handle any platform-specific data formats

### Custom Dashboards

To create specialized dashboards for specific analysis needs:

1. Use the existing dashboard generator as a template
2. Modify the layout and included visualizations
3. Update the HTML template for interactive dashboards

## Data Dictionary

### Raw Data Fields

- `job_id`: Unique identifier for the job listing
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `salary`: Salary information (when available)
- `description`: Full job description
- `url`: URL of the job listing
- `date_posted`: Date the job was posted
- `job_type`: Type of employment (full-time, part-time, etc.)

### Processed Data Fields

- `min_salary`: Extracted minimum salary
- `max_salary`: Extracted maximum salary
- `avg_salary`: Average of min and max salary
- `skills_mentioned`: List of skills mentioned in the description
- `education_required`: Extracted education requirement
- `years_experience`: Extracted years of experience required
- `job_level`: Derived job level (Junior, Mid-level, Senior)
- `is_remote`: Boolean indicating if the job is remote

## Acknowledgments

This project uses data from Indeed.com for educational and research purposes only.
