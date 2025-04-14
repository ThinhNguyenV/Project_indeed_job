"""
Indeed Job Scraper

This script scrapes job listings from Indeed.com based on specified search parameters.
It extracts job data from embedded JavaScript variables in the HTML using regex patterns.

Author: Manus
Date: April 14, 2025
"""

import re
import json
import time
import random
import logging
import os
import sys
from urllib.parse import urlencode
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import SCRAPING_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scraper.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("indeed_scraper")

class IndeedScraper:
    """
    A class to scrape job listings from Indeed.com
    """
    
    def __init__(self, job_titles, locations, results_per_page=15, max_pages_per_search=5, 
                 delay_between_requests=3, timeout=30, max_retries=3, retry_delay=5):
        """
        Initialize the scraper with configuration parameters
        
        Args:
            job_titles (list): List of job titles to search for
            locations (list): List of locations to search in
            results_per_page (int): Number of results per page
            max_pages_per_search (int): Maximum number of pages to scrape per search
            delay_between_requests (int): Delay between requests in seconds
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retries for failed requests
            retry_delay (int): Delay between retries in seconds
        """
        self.job_titles = job_titles
        self.locations = locations
        self.results_per_page = results_per_page
        self.max_pages_per_search = max_pages_per_search
        self.delay_between_requests = delay_between_requests
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # User agent for requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Create data directories if they don't exist
        os.makedirs("../data/raw", exist_ok=True)
        os.makedirs("../data/processed", exist_ok=True)
        
        logger.info(f"Initialized Indeed scraper with {len(job_titles)} job titles and {len(locations)} locations")
    
    def _make_search_url(self, job_title, location, start=0):
        """
        Create a search URL for Indeed.com
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            start (int): Result offset for pagination
            
        Returns:
            str: Search URL
        """
        params = {
            "q": job_title,
            "l": location,
            "filter": 0,
            "start": start
        }
        return f"https://www.indeed.com/jobs?{urlencode(params)}"
    
    def _parse_search_page(self, html):
        """
        Parse job listings from search page HTML
        
        Args:
            html (str): HTML content of search page
            
        Returns:
            dict: Dictionary containing job results and metadata
        """
        try:
            # Extract job data from embedded JavaScript
            data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
            if not data:
                logger.warning("No job data found in HTML")
                return {"results": [], "meta": []}
            
            data = json.loads(data[0])
            return {
                "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
                "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing search page: {e}")
            return {"results": [], "meta": []}
    
    def _parse_job_page(self, html):
        """
        Parse detailed job information from job page HTML
        
        Args:
            html (str): HTML content of job page
            
        Returns:
            dict: Dictionary containing job details
        """
        try:
            # Extract job data from embedded JavaScript
            data = re.findall(r'window._initialData=(\{.+?\});', html)
            if not data:
                logger.warning("No job details found in HTML")
                return {}
            
            data = json.loads(data[0])
            return data["jobInfoWrapperModel"]["jobInfoModel"]
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing job page: {e}")
            return {}
    
    def _make_request(self, url):
        """
        Make an HTTP request with retry logic
        
        Args:
            url (str): URL to request
            
        Returns:
            str: HTML content of response
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Requesting URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.text
                
                logger.warning(f"Request failed with status code {response.status_code}")
                
                # If we get blocked (403), wait longer
                if response.status_code == 403:
                    time.sleep(self.retry_delay * 2)
                else:
                    time.sleep(self.retry_delay)
                    
            except requests.RequestException as e:
                logger.warning(f"Request error (attempt {attempt+1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay)
        
        logger.error(f"Failed to retrieve {url} after {self.max_retries} attempts")
        return ""
    
    def scrape_search(self, job_title, location):
        """
        Scrape job listings for a specific job title and location
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            
        Returns:
            list: List of job listings
        """
        logger.info(f"Scraping jobs for '{job_title}' in '{location}'")
        all_results = []
        
        # Get first page
        first_page_url = self._make_search_url(job_title, location)
        first_page_html = self._make_request(first_page_url)
        
        if not first_page_html:
            logger.error(f"Failed to retrieve first page for {job_title} in {location}")
            return all_results
        
        # Parse first page
        first_page_data = self._parse_search_page(first_page_html)
        all_results.extend(first_page_data["results"])
        
        # Calculate total pages to scrape
        total_results = sum(category["jobCount"] for category in first_page_data["meta"]) if first_page_data["meta"] else 0
        total_pages = min(self.max_pages_per_search, (total_results + self.results_per_page - 1) // self.results_per_page)
        
        logger.info(f"Found {total_results} results, scraping up to {total_pages} pages")
        
        # Scrape remaining pages
        for page in range(1, total_pages):
            start_index = page * self.results_per_page
            page_url = self._make_search_url(job_title, location, start=start_index)
            
            # Add delay between requests
            time.sleep(self.delay_between_requests + random.uniform(0, 1))
            
            page_html = self._make_request(page_url)
            if not page_html:
                continue
                
            page_data = self._parse_search_page(page_html)
            all_results.extend(page_data["results"])
            
            logger.info(f"Scraped page {page+1}/{total_pages} for '{job_title}' in '{location}'")
        
        return all_results
    
    def scrape_job_details(self, job_keys):
        """
        Scrape detailed information for specific job listings
        
        Args:
            job_keys (list): List of job keys to scrape details for
            
        Returns:
            list: List of detailed job information
        """
        logger.info(f"Scraping details for {len(job_keys)} jobs")
        job_details = []
        
        for i, job_key in enumerate(job_keys):
            url = f"https://www.indeed.com/viewjob?jk={job_key}"
            
            # Add delay between requests
            if i > 0:
                time.sleep(self.delay_between_requests + random.uniform(0, 1))
            
            html = self._make_request(url)
            if not html:
                continue
                
            details = self._parse_job_page(html)
            if details:
                job_details.append(details)
                
            logger.info(f"Scraped details for job {i+1}/{len(job_keys)}")
        
        return job_details
    
    def run(self):
        """
        Run the scraper for all job titles and locations
        
        Returns:
            tuple: (search_results, job_details)
        """
        logger.info("Starting Indeed job scraper")
        
        all_search_results = []
        all_job_keys = set()
        
        # Scrape search results for all job titles and locations
        for job_title in self.job_titles:
            for location in self.locations:
                search_results = self.scrape_search(job_title, location)
                
                # Add job title and location to each result
                for result in search_results:
                    result["search_job_title"] = job_title
                    result["search_location"] = location
                
                all_search_results.extend(search_results)
                
                # Extract job keys for detailed scraping
                job_keys = [result.get("jobkey") for result in search_results if result.get("jobkey")]
                all_job_keys.update(job_keys)
        
        logger.info(f"Scraped {len(all_search_results)} total job listings")
        
        # Save search results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_results_file = f"../data/raw/indeed_search_results_{timestamp}.json"
        with open(search_results_file, "w") as f:
            json.dump(all_search_results, f, indent=2)
        
        logger.info(f"Saved search results to {search_results_file}")
        
        # Scrape job details
        all_job_keys = list(all_job_keys)
        job_details = self.scrape_job_details(all_job_keys)
        
        # Save job details
        job_details_file = f"../data/raw/indeed_job_details_{timestamp}.json"
        with open(job_details_file, "w") as f:
            json.dump(job_details, f, indent=2)
        
        logger.info(f"Saved job details to {job_details_file}")
        
        return all_search_results, job_details


def main():
    """
    Main function to run the scraper
    """
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
    search_results, job_details = scraper.run()
    
    logger.info(f"Scraping completed. Collected {len(search_results)} search results and {len(job_details)} job details.")


if __name__ == "__main__":
    main()
