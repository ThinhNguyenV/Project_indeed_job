"""
Script to run the Indeed job scraper and collect job data.

This script executes the Indeed scraper to collect job listings based on
the parameters defined in the configuration file.

Author: Manus
Date: April 14, 2025
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.indeed_scraper import IndeedScraper
from scripts.config import SCRAPING_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "collection.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_collection")

def main():
    """
    Main function to run the data collection process
    """
    logger.info("Starting job data collection process")
    
    # Log the search parameters
    logger.info(f"Job titles to search: {SCRAPING_CONFIG['job_titles']}")
    logger.info(f"Locations to search: {SCRAPING_CONFIG['locations']}")
    logger.info(f"Max pages per search: {SCRAPING_CONFIG['max_pages_per_search']}")
    
    # Create timestamp for this collection run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create scraper instance with configuration
    scraper = IndeedScraper(
        job_titles=SCRAPING_CONFIG["job_titles"],
        locations=SCRAPING_CONFIG["locations"],
        results_per_page=SCRAPING_CONFIG["results_per_page"],
        max_pages_per_search=SCRAPING_CONFIG["max_pages_per_search"],
        delay_between_requests=SCRAPING_CONFIG["delay_between_requests"],
        timeout=SCRAPING_CONFIG["timeout"],
        max_retries=SCRAPING_CONFIG["max_retries"],
        retry_delay=SCRAPING_CONFIG["retry_delay"]
    )
    
    # Run scraper
    logger.info("Running Indeed scraper to collect job data")
    search_results, job_details = scraper.run()
    
    # Log collection statistics
    logger.info(f"Data collection completed:")
    logger.info(f"  - Collected {len(search_results)} search results")
    logger.info(f"  - Collected {len(job_details)} detailed job listings")
    
    # Create summary file with collection metadata
    summary = {
        "timestamp": timestamp,
        "job_titles": SCRAPING_CONFIG["job_titles"],
        "locations": SCRAPING_CONFIG["locations"],
        "search_results_count": len(search_results),
        "job_details_count": len(job_details),
        "search_results_file": f"indeed_search_results_{timestamp}.json",
        "job_details_file": f"indeed_job_details_{timestamp}.json"
    }
    
    # Save summary to file
    summary_file = f"../data/raw/collection_summary_{timestamp}.json"
    import json
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Saved collection summary to {summary_file}")
    logger.info("Job data collection process completed successfully")

if __name__ == "__main__":
    main()
