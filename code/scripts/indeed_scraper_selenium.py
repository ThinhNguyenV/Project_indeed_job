"""
Indeed Job Scraper using Selenium

This script scrapes job listings from Indeed.com using Selenium to bypass anti-scraping measures.
It simulates real user behavior and extracts job data from the pages.

Author: Thinh Nguyen Van
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

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

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
logger = logging.getLogger("indeed_scraper_selenium")

# List of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

class IndeedScraperSelenium:
    """
    A class to scrape job listings from Indeed.com using Selenium
    """
    
    def __init__(self, job_titles, locations, results_per_page=15, max_pages_per_search=5, 
                 delay_between_requests=5, timeout=30, max_retries=3, retry_delay=10):
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
        
        # Create data directories if they don't exist
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw"), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed"), exist_ok=True)
        
        # Initialize the webdriver
        self.driver = self._setup_driver()
        
        logger.info(f"Initialized Indeed scraper with {len(job_titles)} job titles and {len(locations)} locations")
    
    def _setup_driver(self):
        """
        Set up the Selenium WebDriver with appropriate options
        
        Returns:
            WebDriver: Configured Chrome WebDriver
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set window size to simulate a real browser
        driver.set_window_size(1920, 1080)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        
        return driver
    
    def _rotate_user_agent(self):
        """
        Rotate the user agent by restarting the WebDriver with a new user agent
        """
        if self.driver:
            self.driver.quit()
        
        self.driver = self._setup_driver()
    
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
    
    def _extract_job_data_from_search_page(self):
        """
        Extract job data from the current search page
        
        Returns:
            list: List of job data dictionaries
        """
        job_cards = []
        
        try:
            # Wait for job cards to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
            )
            
            # Extract job data from the page
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            
            for job in job_elements:
                try:
                    # Extract job data
                    job_id = job.get_attribute("id") or ""
                    job_id = job_id.replace("job_", "")
                    
                    title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                    title = title_element.text if title_element else "N/A"
                    
                    company_element = job.find_element(By.CSS_SELECTOR, "span.companyName")
                    company = company_element.text if company_element else "N/A"
                    
                    location_element = job.find_element(By.CSS_SELECTOR, "div.companyLocation")
                    location = location_element.text if location_element else "N/A"
                    
                    # Try to extract salary if available
                    try:
                        salary_element = job.find_element(By.CSS_SELECTOR, "div.salary-snippet-container")
                        salary = salary_element.text
                    except NoSuchElementException:
                        salary = "N/A"
                    
                    # Try to extract job description snippet
                    try:
                        description_element = job.find_element(By.CSS_SELECTOR, "div.job-snippet")
                        description = description_element.text
                    except NoSuchElementException:
                        description = "N/A"
                    
                    # Get job URL
                    try:
                        url_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                        job_url = url_element.get_attribute("href")
                    except NoSuchElementException:
                        job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                    
                    job_data = {
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "description_snippet": description,
                        "url": job_url
                    }
                    
                    job_cards.append(job_data)
                    
                except Exception as e:
                    logger.warning(f"Error extracting job data: {e}")
                    continue
            
            return job_cards
            
        except TimeoutException:
            logger.warning("Timeout waiting for job cards to load")
            return []
        except Exception as e:
            logger.error(f"Error extracting job data from search page: {e}")
            return []
    
    def _extract_job_details(self, job_url):
        """
        Extract detailed job information from job page
        
        Args:
            job_url (str): URL of the job page
            
        Returns:
            dict: Dictionary containing job details
        """
        try:
            # Navigate to job page
            self.driver.get(job_url)
            
            # Add random delay to simulate human behavior
            time.sleep(random.uniform(2, 5))
            
            # Wait for job details to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobsearch-JobComponent"))
            )
            
            # Extract job details
            job_details = {}
            
            # Job title
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title")
                job_details["title"] = title_element.text
            except NoSuchElementException:
                job_details["title"] = "N/A"
            
            # Company
            try:
                company_element = self.driver.find_element(By.CSS_SELECTOR, "div.jobsearch-InlineCompanyRating div")
                job_details["company"] = company_element.text
            except NoSuchElementException:
                job_details["company"] = "N/A"
            
            # Location
            try:
                location_element = self.driver.find_element(By.CSS_SELECTOR, "div.jobsearch-JobInfoHeader-subtitle div")
                job_details["location"] = location_element.text
            except NoSuchElementException:
                job_details["location"] = "N/A"
            
            # Salary
            try:
                salary_element = self.driver.find_element(By.CSS_SELECTOR, "span.jobsearch-JobMetadataHeader-item")
                if "salary" in salary_element.text.lower():
                    job_details["salary"] = salary_element.text
                else:
                    job_details["salary"] = "N/A"
            except NoSuchElementException:
                job_details["salary"] = "N/A"
            
            # Job description
            try:
                description_element = self.driver.find_element(By.CSS_SELECTOR, "div#jobDescriptionText")
                job_details["description"] = description_element.text
            except NoSuchElementException:
                job_details["description"] = "N/A"
            
            # Job type
            try:
                job_type_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.jobsearch-JobDescriptionSection-sectionItem")
                for element in job_type_elements:
                    if "job type" in element.text.lower():
                        job_details["job_type"] = element.text.replace("Job Type:", "").strip()
                        break
                else:
                    job_details["job_type"] = "N/A"
            except NoSuchElementException:
                job_details["job_type"] = "N/A"
            
            # URL
            job_details["url"] = job_url
            
            return job_details
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for job details to load: {job_url}")
            return {"url": job_url, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return {"url": job_url, "error": str(e)}
    
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
        
        # Rotate user agent for each search
        self._rotate_user_agent()
        
        # Get first page
        first_page_url = self._make_search_url(job_title, location)
        
        try:
            # Navigate to search page
            self.driver.get(first_page_url)
            
            # Add random delay to simulate human behavior
            time.sleep(random.uniform(3, 7))
            
            # Extract job data from first page
            first_page_results = self._extract_job_data_from_search_page()
            
            if first_page_results:
                # Add search parameters to results
                for result in first_page_results:
                    result["search_job_title"] = job_title
                    result["search_location"] = location
                
                all_results.extend(first_page_results)
                logger.info(f"Scraped {len(first_page_results)} jobs from first page")
            else:
                logger.warning(f"No jobs found on first page for '{job_title}' in '{location}'")
                return all_results
            
            # Check if there are more pages
            try:
                pagination = self.driver.find_elements(By.CSS_SELECTOR, "nav[role='navigation'] div a")
                if not pagination:
                    logger.info(f"No pagination found, only one page of results for '{job_title}' in '{location}'")
                    return all_results
                
                # Determine number of pages to scrape
                total_pages = min(len(pagination) + 1, self.max_pages_per_search)
                logger.info(f"Found pagination, scraping up to {total_pages} pages")
                
                # Scrape remaining pages
                for page in range(1, total_pages):
                    # Calculate start index for pagination
                    start_index = page * self.results_per_page
                    page_url = self._make_search_url(job_title, location, start=start_index)
                    
                    # Add random delay between page requests
                    delay = self.delay_between_requests + random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.2f} seconds before requesting next page")
                    time.sleep(delay)
                    
                    # Rotate user agent occasionally
                    if random.random() < 0.3:
                        self._rotate_user_agent()
                    
                    # Navigate to next page
                    self.driver.get(page_url)
                    
                    # Add random delay to simulate human behavior
                    time.sleep(random.uniform(3, 7))
                    
                    # Extract job data from page
                    page_results = self._extract_job_data_from_search_page()
                    
                    if page_results:
                        # Add search parameters to results
                        for result in page_results:
                            result["search_job_title"] = job_title
                            result["search_location"] = location
                        
                        all_results.extend(page_results)
                        logger.info(f"Scraped {len(page_results)} jobs from page {page+1}")
                    else:
                        logger.warning(f"No jobs found on page {page+1} for '{job_title}' in '{location}'")
                        break
            
            except Exception as e:
                logger.error(f"Error handling pagination: {e}")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error scraping search for '{job_title}' in '{location}': {e}")
            return all_results
    
    def scrape_job_details(self, job_urls):
        """
        Scrape detailed information for specific job listings
        
        Args:
            job_urls (list): List of job URLs to scrape details for
            
        Returns:
            list: List of detailed job information
        """
        logger.info(f"Scraping details for {len(job_urls)} jobs")
        job_details = []
        
        for i, job_url in enumerate(job_urls):
            # Add delay between requests
            if i > 0:
                delay = self.delay_between_requests + random.uniform(2, 5)
                logger.info(f"Waiting {delay:.2f} seconds before requesting next job details")
                time.sleep(delay)
            
            # Rotate user agent occasionally
            if random.random() < 0.3:
                self._rotate_user_agent()
            
            # Extract job details
            details = self._extract_job_details(job_url)
            
            if details:
                job_details.append(details)
                logger.info(f"Scraped details for job {i+1}/{len(job_urls)}")
            else:
                logger.warning(f"Failed to scrape details for job {i+1}/{len(job_urls)}")
        
        return job_details
    
    def run(self):
        """
        Run the scraper for all job titles and locations
        
        Returns:
            tuple: (search_results, job_details)
        """
        logger.info("Starting Indeed job scraper with Selenium")
        
        all_search_results = []
        all_job_urls = set()
        
        # Scrape search results for all job titles and locations
        for job_title in self.job_titles:
            for location in self.locations:
                search_results = self.scrape_search(job_title, location)
                all_search_results.extend(search_results)
                
                # Extract job URLs for detailed scraping
                job_urls = [result.get("url") for result in search_results if result.get("url")]
                all_job_urls.update(job_urls)
                
                # Add delay between searches
                delay = self.delay_between_requests * 2 + random.uniform(5, 10)
                logger.info(f"Waiting {delay:.2f} seconds before next search")
                time.sleep(delay)
        
        logger.info(f"Scraped {len(all_search_results)} total job listings")
        
        # Save search results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_results_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "raw", f"indeed_search_results_{timestamp}.json"
        )
        
        with open(search_results_file, "w") as f:
            json.dump(all_search_results, f, indent=2)
        
        logger.info(f"Saved search results to {search_results_file}")
        
        # Scrape job details
        all_job_urls = list(all_job_urls)
        job_details = self.scrape_job_details(all_job_urls)
        
        # Save job details
        job_details_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "raw", f"indeed_job_details_{timestamp}.json"
        )
        
        with open(job_details_file, "w") as f:
            json.dump(job_details, f, indent=2)
        
        logger.info(f"Saved job details to {job_details_file}")
        
        # Clean up
        self.driver.quit()
        
        return all_search_results, job_details


def main():
    """
    Main function to run the scraper
    """
    # Create scraper instance with configuration
    scraper = IndeedScraperSelenium(
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
