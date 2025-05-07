"""
Data processor for Indeed job listings

This script cleans and processes the raw job data collected from Indeed,
extracting relevant features and preparing it for analysis.

Author: Thinh Nguyen Van
Date: April 14, 2025
"""

import json
import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processing.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_processor")

# Common skills to look for in job descriptions
COMMON_SKILLS = [
    "SQL", "Python", "R", "Excel", "Tableau", "Power BI", "SAS", "SPSS", 
    "Java", "C#", "C\\+\\+", "JavaScript", "Scala", "MATLAB", "Hadoop", "Spark",
    "AWS", "Azure", "Google Cloud", "ETL", "Machine Learning", "AI", 
    "Deep Learning", "NLP", "Natural Language Processing", "Data Mining",
    "Data Visualization", "Statistical Analysis", "A/B Testing", "Data Modeling",
    "Data Warehousing", "Big Data", "NoSQL", "MongoDB", "Cassandra", "MySQL",
    "PostgreSQL", "Oracle", "SQL Server", "Teradata", "Snowflake", "Redshift",
    "Looker", "Qlik", "Alteryx", "KNIME", "RapidMiner", "TensorFlow", "PyTorch",
    "Keras", "scikit-learn", "pandas", "NumPy", "Matplotlib", "Seaborn", "ggplot2",
    "Jupyter", "Git", "Docker", "Kubernetes", "Airflow", "Luigi", "Databricks",
    "Agile", "Scrum", "Jira", "Confluence", "Microsoft Office", "VBA", "DAX",
    "Power Query", "SharePoint", "Salesforce", "Dynamics", "SAP", "Oracle EBS"
]

# Education levels for standardization
EDUCATION_LEVELS = {
    "bachelor": "Bachelor's degree",
    "bs": "Bachelor's degree",
    "ba": "Bachelor's degree",
    "undergraduate": "Bachelor's degree",
    "master": "Master's degree",
    "ms": "Master's degree",
    "ma": "Master's degree",
    "graduate": "Master's degree",
    "phd": "PhD",
    "doctorate": "PhD",
    "doctoral": "PhD",
    "associate": "Associate's degree",
    "aa": "Associate's degree",
    "as": "Associate's degree",
    "high school": "High School Diploma",
    "ged": "High School Diploma",
    "certificate": "Certification",
    "certification": "Certification"
}

class JobDataProcessor:
    """
    A class to clean and process job data from Indeed
    """
    
    def __init__(self, raw_data_dir, processed_data_dir):
        """
        Initialize the processor with data directories
        
        Args:
            raw_data_dir (str): Directory containing raw data files
            processed_data_dir (str): Directory to save processed data files
        """
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        
        # Create processed data directory if it doesn't exist
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        logger.info(f"Initialized job data processor with raw data from {raw_data_dir}")
    
    def _find_latest_data_files(self):
        """
        Find the latest data files in the raw data directory
        
        Returns:
            tuple: (search_results_file, job_details_file, summary_file)
        """
        # Find all collection summary files
        summary_files = [f for f in os.listdir(self.raw_data_dir) if f.startswith("collection_summary_")]
        
        if not summary_files:
            logger.error("No collection summary files found in raw data directory")
            return None, None, None
        
        # Sort by timestamp (part of filename) to get the latest
        latest_summary = sorted(summary_files)[-1]
        
        # Load the summary file to get the associated data files
        summary_path = os.path.join(self.raw_data_dir, latest_summary)
        with open(summary_path, "r") as f:
            summary = json.load(f)
        
        # Get the paths to the data files
        search_results_file = os.path.join(self.raw_data_dir, summary["search_results_file"])
        job_details_file = os.path.join(self.raw_data_dir, summary["job_details_file"])
        
        logger.info(f"Found latest data files from {summary.get('timestamp', 'unknown date')}")
        
        return search_results_file, job_details_file, summary_path
    
    def load_raw_data(self):
        """
        Load the raw data from JSON files
        
        Returns:
            tuple: (search_results_df, job_details_df)
        """
        # Find the latest data files
        search_results_file, job_details_file, _ = self._find_latest_data_files()
        
        if not search_results_file or not job_details_file:
            logger.error("Could not find data files")
            return None, None
        
        # Load search results
        try:
            with open(search_results_file, "r") as f:
                search_results = json.load(f)
            search_results_df = pd.DataFrame(search_results)
            logger.info(f"Loaded {len(search_results_df)} search results from {search_results_file}")
        except Exception as e:
            logger.error(f"Error loading search results: {e}")
            search_results_df = None
        
        # Load job details
        try:
            with open(job_details_file, "r") as f:
                job_details = json.load(f)
            job_details_df = pd.DataFrame(job_details)
            logger.info(f"Loaded {len(job_details_df)} job details from {job_details_file}")
        except Exception as e:
            logger.error(f"Error loading job details: {e}")
            job_details_df = None
        
        return search_results_df, job_details_df
    
    def clean_search_results(self, df):
        """
        Clean and standardize the search results dataframe
        
        Args:
            df (DataFrame): Raw search results dataframe
            
        Returns:
            DataFrame: Cleaned search results dataframe
        """
        if df is None or df.empty:
            logger.warning("No search results to clean")
            return None
        
        logger.info("Cleaning search results data")
        
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Handle missing values
        cleaned_df["salary"] = cleaned_df["salary"].fillna("Not specified")
        cleaned_df["description_snippet"] = cleaned_df["description_snippet"].fillna("")
        
        # Standardize location format
        if "location" in cleaned_df.columns:
            # Extract city and state where possible
            def standardize_location(loc):
                if pd.isna(loc) or loc == "N/A":
                    return "Not specified"
                
                # Handle "Remote" as a special case
                if "remote" in loc.lower():
                    return "Remote"
                
                # Try to extract city and state
                match = re.search(r"([^,]+),\s*([A-Z]{2})", loc)
                if match:
                    city, state = match.groups()
                    return f"{city.strip()}, {state.strip()}"
                
                return loc
            
            cleaned_df["location"] = cleaned_df["location"].apply(standardize_location)
        
        # Extract salary information where available
        if "salary" in cleaned_df.columns:
            # Extract minimum and maximum salary where possible
            def extract_salary_range(salary_text):
                if pd.isna(salary_text) or salary_text == "N/A" or salary_text == "Not specified":
                    return pd.NA, pd.NA, "Not specified"
                
                # Look for patterns like "$40,000 - $60,000 a year" or "$20 - $30 an hour"
                match = re.search(r"\$([0-9,.]+)\s*-\s*\$([0-9,.]+)\s*(?:a|an|per)\s*(\w+)", salary_text)
                if match:
                    min_salary = float(match.group(1).replace(",", ""))
                    max_salary = float(match.group(2).replace(",", ""))
                    period = match.group(3).lower()
                    
                    # Convert hourly to yearly (assuming 2080 hours per year)
                    if period == "hour":
                        min_salary *= 2080
                        max_salary *= 2080
                        period = "year"
                    
                    return min_salary, max_salary, period
                
                return pd.NA, pd.NA, "Not specified"
            
            # Apply the extraction function
            salary_info = cleaned_df["salary"].apply(extract_salary_range)
            cleaned_df["min_salary"] = salary_info.apply(lambda x: x[0])
            cleaned_df["max_salary"] = salary_info.apply(lambda x: x[1])
            cleaned_df["salary_period"] = salary_info.apply(lambda x: x[2])
            
            # Calculate average salary
            cleaned_df["avg_salary"] = cleaned_df.apply(
                lambda row: (row["min_salary"] + row["max_salary"]) / 2 
                if not pd.isna(row["min_salary"]) and not pd.isna(row["max_salary"]) 
                else pd.NA, 
                axis=1
            )
        
        # Add date processed column
        cleaned_df["date_processed"] = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Cleaned {len(cleaned_df)} search results")
        
        return cleaned_df
    
    def clean_job_details(self, df):
        """
        Clean and standardize the job details dataframe
        
        Args:
            df (DataFrame): Raw job details dataframe
            
        Returns:
            DataFrame: Cleaned job details dataframe
        """
        if df is None or df.empty:
            logger.warning("No job details to clean")
            return None
        
        logger.info("Cleaning job details data")
        
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Handle missing values
        cleaned_df["description"] = cleaned_df["description"].fillna("")
        cleaned_df["salary"] = cleaned_df["salary"].fillna("Not specified")
        
        # Standardize job types
        if "job_type" in cleaned_df.columns:
            def standardize_job_type(job_type):
                if pd.isna(job_type) or job_type == "N/A":
                    return "Not specified"
                
                job_type = job_type.lower()
                
                if "full" in job_type and "time" in job_type:
                    return "Full-time"
                elif "part" in job_type and "time" in job_type:
                    return "Part-time"
                elif "contract" in job_type:
                    return "Contract"
                elif "temp" in job_type:
                    return "Temporary"
                elif "intern" in job_type:
                    return "Internship"
                elif "remote" in job_type:
                    return "Remote"
                
                return job_type.capitalize()
            
            cleaned_df["job_type"] = cleaned_df["job_type"].apply(standardize_job_type)
        
        # Extract education requirements from description
        def extract_education(description):
            if pd.isna(description) or description == "":
                return "Not specified"
            
            description = description.lower()
            
            for key, value in EDUCATION_LEVELS.items():
                if key in description:
                    return value
            
            return "Not specified"
        
        cleaned_df["education_required"] = cleaned_df["description"].apply(extract_education)
        
        # Extract years of experience from description
        def extract_experience(description):
            if pd.isna(description) or description == "":
                return "Not specified"
            
            description = description.lower()
            
            # Look for patterns like "X+ years" or "X years of experience"
            matches = re.findall(r"(\d+)(?:\+)?\s*(?:-\s*\d+)?\s*years?(?:\s+of)?\s+experience", description)
            if matches:
                return min([int(x) for x in matches])
            
            # Look for experience levels
            if "senior" in description or "sr." in description:
                return 5
            elif "mid" in description or "intermediate" in description:
                return 3
            elif "junior" in description or "jr." in description or "entry" in description:
                return 1
            
            return "Not specified"
        
        cleaned_df["years_experience"] = cleaned_df["description"].apply(extract_experience)
        
        # Add date processed column
        cleaned_df["date_processed"] = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Cleaned {len(cleaned_df)} job details")
        
        return cleaned_df
    
    def extract_skills(self, df):
        """
        Extract mentioned skills from job descriptions
        
        Args:
            df (DataFrame): Job details dataframe with descriptions
            
        Returns:
            DataFrame: Dataframe with extracted skills
        """
        if df is None or df.empty or "description" not in df.columns:
            logger.warning("No job descriptions to extract skills from")
            return None
        
        logger.info("Extracting skills from job descriptions")
        
        # Make a copy to avoid modifying the original
        skills_df = df.copy()
        
        # Create a dictionary to store skill presence for each job
        skill_columns = {}
        
        # Check for each skill in the description
        for skill in COMMON_SKILLS:
            # Create a regex pattern that matches the skill as a whole word
            pattern = r'\b' + skill + r'\b'
            
            # Check if the skill is mentioned in the description
            skill_columns[skill] = skills_df["description"].str.contains(
                pattern, case=False, regex=True
            ).fillna(False).astype(int)
        
        # Add skill columns to the dataframe
        for skill, values in skill_columns.items():
            skills_df[f"skill_{skill.lower()}"] = values
        
        # Count total skills mentioned for each job
        skills_df["skills_mentioned_count"] = sum(skill_columns.values())
        
        # Create a list of mentioned skills for each job
        def get_mentioned_skills(row):
            return [skill for skill in COMMON_SKILLS if row[f"skill_{skill.lower()}"] == 1]
        
        skills_df["skills_mentioned"] = skills_df.apply(get_mentioned_skills, axis=1)
        
        logger.info(f"Extracted skills from {len(skills_df)} job descriptions")
        
        return skills_df
    
    def merge_and_process_data(self, search_df, details_df):
        """
        Merge search results and job details, and perform final processing
        
        Args:
            search_df (DataFrame): Cleaned search results dataframe
            details_df (DataFrame): Cleaned job details dataframe with extracted skills
            
        Returns:
            DataFrame: Final processed dataframe
        """
        if search_df is None or details_df is None:
            logger.warning("Cannot merge data: missing dataframes")
            return None
        
        logger.info("Merging and performing final data processing")
        
        # Identify common key for merging
        common_keys = set(search_df.columns).intersection(set(details_df.columns))
        merge_key = "job_id" if "job_id" in common_keys else "url" if "url" in common_keys else None
        
        if not merge_key:
            logger.warning("No common key found for merging dataframes")
            # If no common key, just return the details dataframe as it's more comprehensive
            return details_df
        
        # Merge the dataframes
        merged_df = pd.merge(
            details_df, 
            search_df, 
            on=merge_key, 
            how="left", 
            suffixes=("", "_search")
        )
        
        # Clean up duplicate columns
        for col in merged_df.columns:
            if col.endswith("_search"):
                base_col = col[:-7]  # Remove "_search" suffix
                if base_col in merged_df.columns:
                    # If the base column has missing values, fill them from the search column
                    merged_df[base_col] = merged_df[base_col].fillna(merged_df[col])
                    # Drop the duplicate column
                    merged_df = merged_df.drop(columns=[col])
        
        # Add derived features
        
        # Job level based on title and experience
        def determine_job_level(row):
            title = row["title"].lower() if not pd.isna(row["title"]) else ""
            experience = row["years_experience"] if not pd.isna(row["years_experience"]) and row["years_experience"] != "Not specified" else 0
            
            if isinstance(experience, str):
                experience = 0
            
            if "senior" in title or "sr" in title or "lead" in title or "principal" in title or experience >= 5:
                return "Senior"
            elif "junior" in title or "jr" in title or "entry" in title or experience <= 1:
                return "Junior"
            else:
                return "Mid-level"
        
        merged_df["job_level"] = merged_df.apply(determine_job_level, axis=1)
        
        # Remote work indicator
        merged_df["is_remote"] = merged_df["location"].str.contains("Remote", case=False).fillna(False)
        
        # Salary competitiveness (compared to average)
        if "avg_salary" in merged_df.columns:
            avg_salary = merged_df["avg_salary"].median()
            
            def salary_competitiveness(salary):
                if pd.isna(salary) or salary == 0:
                    return "Unknown"
                
                ratio = salary / avg_salary
                
                if ratio > 1.2:
                    return "High"
                elif ratio < 0.8:
                    return "Low"
                else:
                    return "Average"
            
            merged_df["salary_competitiveness"] = merged_df["avg_salary"].apply(salary_competitiveness)
        
        # Drop any remaining duplicate rows
        merged_df = merged_df.drop_duplicates(subset=[merge_key])
        
        logger.info(f"Created final processed dataset with {len(merged_df)} rows and {len(merged_df.columns)} columns")
        
        return merged_df
    
    def save_processed_data(self, df, filename="processed_indeed_jobs.csv"):
        """
        Save the processed dataframe to CSV
        
        Args:
            df (DataFrame): Processed dataframe to save
            filename (str): Name of the output file
            
        Returns:
            str: Path to the saved file
        """
        if df is None or df.empty:
            logger.warning("No processed data to save")
            return None
        
        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"{filename.split('.')[0]}_{timestamp}.csv"
        
        # Save to CSV
        output_path = os.path.join(self.processed_data_dir, filename_with_timestamp)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Saved processed data to {output_path}")
        
        # Also save a copy as JSON for easier loading in analysis
        json_path = os.path.join(self.processed_data_dir, f"{filename.split('.')[0]}_{timestamp}.json")
        df.to_json(json_path, orient="records", indent=2)
        
        logger.info(f"Saved processed data as JSON to {json_path}")
        
        return output_path
    
    def run(self):
        """
        Run the complete data processing pipeline
        
        Returns:
            tuple: (processed_df, output_path)
        """
        logger.info("Starting job data processing pipeline")
        
        # Load raw data
        search_results_df, job_details_df = self.load_raw_data()
        
        # Clean data
        cleaned_search_df = self.clean_search_results(search_results_df)
        cleaned_details_df = self.clean_job_details(job_details_df)
        
        # Extract skills
        details_with_skills_df = self.extract_skills(cleaned_details_df)
        
        # Merge and process data
        processed_df = self.merge_and_process_data(cleaned_search_df, details_with_skills_df)
        
        # Save processed data
        output_path = self.save_processed_data(processed_df)
        
        logger.info("Job data processing pipeline completed successfully")
        
        return processed_df, output_path


def main():
    """
    Main function to run the data processing
    """
    # Set up data directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    raw_data_dir = os.path.join(project_dir, "data", "raw")
    processed_data_dir = os.path.join(project_dir, "data", "processed")
    
    # Create processor instance
    processor = JobDataProcessor(raw_data_dir, processed_data_dir)
    
    # Run processing pipeline
    processed_df, output_path = processor.run()
    
    # Print summary statistics
    if processed_df is not None:
        print("\nProcessed Data Summary:")
        print(f"Number of job listings: {len(processed_df)}")
        print(f"Number of unique companies: {processed_df['company'].nunique()}")
        print(f"Number of unique locations: {processed_df['location'].nunique()}")
        
        if "avg_salary" in processed_df.columns:
            valid_salaries = processed_df["avg_salary"].dropna()
            if not valid_salaries.empty:
                print(f"Average salary: ${valid_salaries.mean():,.2f}")
                print(f"Median salary: ${valid_salaries.median():,.2f}")
        
        if "skills_mentioned_count" in processed_df.columns:
            print(f"Average number of skills mentioned: {processed_df['skills_mentioned_count'].mean():.2f}")
        
        print(f"\nProcessed data saved to: {output_path}")


if __name__ == "__main__":
    main()
