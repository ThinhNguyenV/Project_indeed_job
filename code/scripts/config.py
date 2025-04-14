"""
Configuration file for Indeed Job Analysis project.
Contains parameters for web scraping and data analysis.
"""

# Web scraping configuration
SCRAPING_CONFIG = {
    # Search parameters
    'job_titles': [
        'Data Analyst',
        'Business Analyst',
        'Data Scientist',
        'Business Intelligence Analyst'
    ],
    'locations': [
        'Remote',
        'New York, NY',
        'San Francisco, CA',
        'Seattle, WA',
        'Austin, TX',
        'Chicago, IL'
    ],
    
    # Scraping parameters
    'results_per_page': 15,
    'max_pages_per_search': 5,
    'delay_between_requests': 3,  # seconds
    'timeout': 30,  # seconds
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    
    # Retry configuration
    'max_retries': 3,
    'retry_delay': 5,  # seconds
}

# Data storage configuration
DATA_CONFIG = {
    'raw_data_dir': '../data/raw',
    'processed_data_dir': '../data/processed',
    'output_dir': '../data/output',
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'min_job_count': 50,  # Minimum number of job listings to analyze
    'top_skills_count': 20,  # Number of top skills to analyze
    'salary_bins': 10,  # Number of bins for salary histograms
}

# Visualization configuration
VIZ_CONFIG = {
    'chart_style': 'seaborn',
    'color_palette': 'viridis',
    'fig_width': 12,
    'fig_height': 8,
    'dpi': 100,
    'save_format': 'png',
}
