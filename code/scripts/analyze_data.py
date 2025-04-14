"""
Job data analysis script

This script performs exploratory data analysis on the processed Indeed job data,
identifying trends and patterns in job requirements, skills, and salaries.

Author: Thinh Nguyen Van
Date: April 14, 2025
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "analysis.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_analysis")

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

class JobDataAnalyzer:
    """
    A class to analyze processed job data from Indeed
    """
    
    def __init__(self, processed_data_dir, output_dir):
        """
        Initialize the analyzer with data directories
        
        Args:
            processed_data_dir (str): Directory containing processed data files
            output_dir (str): Directory to save analysis results
        """
        self.processed_data_dir = processed_data_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create visualizations directory if it doesn't exist
        self.viz_dir = os.path.join(os.path.dirname(self.output_dir), "visualizations")
        os.makedirs(self.viz_dir, exist_ok=True)
        
        logger.info(f"Initialized job data analyzer with processed data from {processed_data_dir}")
    
    def _find_latest_processed_file(self):
        """
        Find the latest processed data file
        
        Returns:
            str: Path to the latest processed data file
        """
        # Find all processed data files (JSON format for easier loading)
        processed_files = [f for f in os.listdir(self.processed_data_dir) if f.startswith("processed_indeed_jobs_") and f.endswith(".json")]
        
        if not processed_files:
            logger.error("No processed data files found")
            return None
        
        # Sort by timestamp (part of filename) to get the latest
        latest_file = sorted(processed_files)[-1]
        
        file_path = os.path.join(self.processed_data_dir, latest_file)
        logger.info(f"Found latest processed data file: {file_path}")
        
        return file_path
    
    def load_data(self):
        """
        Load the processed data
        
        Returns:
            DataFrame: Processed job data
        """
        # Find the latest processed data file
        data_file = self._find_latest_processed_file()
        
        if not data_file:
            logger.error("Could not find processed data file")
            return None
        
        # Load the data
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} job listings from {data_file}")
            return df
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return None
    
    def analyze_job_titles(self, df):
        """
        Analyze job titles distribution
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty or "title" not in df.columns:
            logger.warning("No job titles to analyze")
            return {}
        
        logger.info("Analyzing job titles distribution")
        
        # Count job titles
        title_counts = df["title"].value_counts().reset_index()
        title_counts.columns = ["title", "count"]
        
        # Group similar titles
        def categorize_title(title):
            title_lower = title.lower()
            if "data analyst" in title_lower:
                return "Data Analyst"
            elif "business analyst" in title_lower:
                return "Business Analyst"
            elif "data scientist" in title_lower:
                return "Data Scientist"
            elif "business intelligence" in title_lower or "bi " in title_lower:
                return "Business Intelligence Analyst"
            else:
                return "Other"
        
        df["title_category"] = df["title"].apply(categorize_title)
        category_counts = df["title_category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        sns.barplot(x="count", y="category", data=category_counts)
        plt.title("Job Title Categories Distribution")
        plt.xlabel("Number of Job Listings")
        plt.ylabel("Job Category")
        plt.tight_layout()
        
        # Save the plot
        plot_path = os.path.join(self.viz_dir, "job_title_distribution.png")
        plt.savefig(plot_path, dpi=300)
        plt.close()
        
        logger.info(f"Saved job title distribution plot to {plot_path}")
        
        # Return analysis results
        return {
            "title_counts": title_counts.to_dict("records"),
            "category_counts": category_counts.to_dict("records"),
            "plot_path": plot_path
        }
    
    def analyze_locations(self, df):
        """
        Analyze job locations distribution
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty or "location" not in df.columns:
            logger.warning("No job locations to analyze")
            return {}
        
        logger.info("Analyzing job locations distribution")
        
        # Count locations
        location_counts = df["location"].value_counts().reset_index()
        location_counts.columns = ["location", "count"]
        
        # Analyze remote vs. on-site
        if "is_remote" in df.columns:
            remote_counts = df["is_remote"].value_counts().reset_index()
            remote_counts.columns = ["is_remote", "count"]
            remote_counts["is_remote"] = remote_counts["is_remote"].map({True: "Remote", False: "On-site"})
        else:
            # Create from location field
            df["is_remote_derived"] = df["location"].str.contains("Remote", case=False)
            remote_counts = df["is_remote_derived"].value_counts().reset_index()
            remote_counts.columns = ["is_remote", "count"]
            remote_counts["is_remote"] = remote_counts["is_remote"].map({True: "Remote", False: "On-site"})
        
        # Create visualization for locations
        plt.figure(figsize=(10, 6))
        sns.barplot(x="count", y="location", data=location_counts)
        plt.title("Job Locations Distribution")
        plt.xlabel("Number of Job Listings")
        plt.ylabel("Location")
        plt.tight_layout()
        
        # Save the plot
        locations_plot_path = os.path.join(self.viz_dir, "job_locations_distribution.png")
        plt.savefig(locations_plot_path, dpi=300)
        plt.close()
        
        # Create visualization for remote vs. on-site
        plt.figure(figsize=(8, 6))
        sns.barplot(x="is_remote", y="count", data=remote_counts)
        plt.title("Remote vs. On-site Jobs")
        plt.xlabel("Job Type")
        plt.ylabel("Number of Job Listings")
        plt.tight_layout()
        
        # Save the plot
        remote_plot_path = os.path.join(self.viz_dir, "remote_vs_onsite_distribution.png")
        plt.savefig(remote_plot_path, dpi=300)
        plt.close()
        
        logger.info(f"Saved job locations distribution plots to {self.viz_dir}")
        
        # Return analysis results
        return {
            "location_counts": location_counts.to_dict("records"),
            "remote_counts": remote_counts.to_dict("records"),
            "locations_plot_path": locations_plot_path,
            "remote_plot_path": remote_plot_path
        }
    
    def analyze_salaries(self, df):
        """
        Analyze salary distributions and trends
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty:
            logger.warning("No salary data to analyze")
            return {}
        
        logger.info("Analyzing salary distributions and trends")
        
        # Check if we have salary data
        salary_columns = [col for col in df.columns if "salary" in col.lower()]
        if not salary_columns:
            logger.warning("No salary columns found in the data")
            return {}
        
        # Use avg_salary if available, otherwise try other salary columns
        if "avg_salary" in salary_columns:
            salary_col = "avg_salary"
        elif "min_salary" in salary_columns and "max_salary" in salary_columns:
            # Create avg_salary if it doesn't exist
            df["avg_salary"] = df.apply(
                lambda row: (row["min_salary"] + row["max_salary"]) / 2 
                if not pd.isna(row["min_salary"]) and not pd.isna(row["max_salary"]) 
                else pd.NA, 
                axis=1
            )
            salary_col = "avg_salary"
        else:
            # Use the first salary column found
            salary_col = salary_columns[0]
        
        # Filter out missing salaries
        salary_df = df[~pd.isna(df[salary_col])].copy()
        
        if salary_df.empty:
            logger.warning("No valid salary data found")
            return {}
        
        # Calculate basic statistics
        salary_stats = {
            "mean": salary_df[salary_col].mean(),
            "median": salary_df[salary_col].median(),
            "min": salary_df[salary_col].min(),
            "max": salary_df[salary_col].max(),
            "std": salary_df[salary_col].std()
        }
        
        # Create salary distribution histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(salary_df[salary_col], bins=20, kde=True)
        plt.title("Salary Distribution")
        plt.xlabel("Salary ($)")
        plt.ylabel("Number of Job Listings")
        plt.axvline(salary_stats["median"], color='r', linestyle='--', label=f"Median: ${salary_stats['median']:,.0f}")
        plt.axvline(salary_stats["mean"], color='g', linestyle='--', label=f"Mean: ${salary_stats['mean']:,.0f}")
        plt.legend()
        plt.tight_layout()
        
        # Save the plot
        salary_dist_path = os.path.join(self.viz_dir, "salary_distribution.png")
        plt.savefig(salary_dist_path, dpi=300)
        plt.close()
        
        # Analyze salaries by job title
        if "title_category" in salary_df.columns:
            # Calculate average salary by job title category
            salary_by_title = salary_df.groupby("title_category")[salary_col].agg(["mean", "median", "count"]).reset_index()
            
            # Create visualization
            plt.figure(figsize=(10, 6))
            sns.barplot(x="mean", y="title_category", data=salary_by_title)
            plt.title("Average Salary by Job Title")
            plt.xlabel("Average Salary ($)")
            plt.ylabel("Job Title")
            plt.tight_layout()
            
            # Save the plot
            salary_by_title_path = os.path.join(self.viz_dir, "salary_by_job_title.png")
            plt.savefig(salary_by_title_path, dpi=300)
            plt.close()
        else:
            salary_by_title = None
            salary_by_title_path = None
        
        # Analyze salaries by location
        if "location" in salary_df.columns:
            # Calculate average salary by location
            salary_by_location = salary_df.groupby("location")[salary_col].agg(["mean", "median", "count"]).reset_index()
            
            # Create visualization
            plt.figure(figsize=(10, 6))
            sns.barplot(x="mean", y="location", data=salary_by_location)
            plt.title("Average Salary by Location")
            plt.xlabel("Average Salary ($)")
            plt.ylabel("Location")
            plt.tight_layout()
            
            # Save the plot
            salary_by_location_path = os.path.join(self.viz_dir, "salary_by_location.png")
            plt.savefig(salary_by_location_path, dpi=300)
            plt.close()
        else:
            salary_by_location = None
            salary_by_location_path = None
        
        # Analyze salaries by experience level
        if "years_experience" in salary_df.columns:
            # Filter out non-numeric experience values
            exp_salary_df = salary_df[pd.to_numeric(salary_df["years_experience"], errors="coerce").notna()].copy()
            exp_salary_df["years_experience"] = pd.to_numeric(exp_salary_df["years_experience"])
            
            if not exp_salary_df.empty:
                # Create scatter plot
                plt.figure(figsize=(10, 6))
                sns.scatterplot(x="years_experience", y=salary_col, data=exp_salary_df)
                plt.title("Salary vs. Years of Experience")
                plt.xlabel("Years of Experience")
                plt.ylabel("Salary ($)")
                
                # Add trend line
                sns.regplot(x="years_experience", y=salary_col, data=exp_salary_df, scatter=False, color="red")
                
                plt.tight_layout()
                
                # Save the plot
                salary_by_exp_path = os.path.join(self.viz_dir, "salary_by_experience.png")
                plt.savefig(salary_by_exp_path, dpi=300)
                plt.close()
            else:
                salary_by_exp_path = None
        else:
            salary_by_exp_path = None
        
        logger.info(f"Saved salary analysis plots to {self.viz_dir}")
        
        # Return analysis results
        return {
            "salary_stats": salary_stats,
            "salary_by_title": salary_by_title.to_dict("records") if salary_by_title is not None else None,
            "salary_by_location": salary_by_location.to_dict("records") if salary_by_location is not None else None,
            "salary_dist_path": salary_dist_path,
            "salary_by_title_path": salary_by_title_path,
            "salary_by_location_path": salary_by_location_path,
            "salary_by_exp_path": salary_by_exp_path
        }
    
    def analyze_skills(self, df):
        """
        Analyze skills mentioned in job listings
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty:
            logger.warning("No skills data to analyze")
            return {}
        
        logger.info("Analyzing skills mentioned in job listings")
        
        # Check if we have skills data
        if "skills_mentioned" not in df.columns:
            logger.warning("No skills_mentioned column found in the data")
            return {}
        
        # Extract all skills
        all_skills = []
        for skills_list in df["skills_mentioned"]:
            if isinstance(skills_list, list):
                all_skills.extend(skills_list)
        
        # Count skill occurrences
        skill_counts = Counter(all_skills)
        
        # Convert to dataframe for visualization
        skill_df = pd.DataFrame(skill_counts.items(), columns=["skill", "count"])
        skill_df = skill_df.sort_values("count", ascending=False)
        
        # Get top skills
        top_skills = skill_df.head(20).copy()
        
        # Create visualization for top skills
        plt.figure(figsize=(12, 8))
        sns.barplot(x="count", y="skill", data=top_skills)
        plt.title("Top 20 Skills Mentioned in Job Listings")
        plt.xlabel("Number of Mentions")
        plt.ylabel("Skill")
        plt.tight_layout()
        
        # Save the plot
        top_skills_path = os.path.join(self.viz_dir, "top_skills.png")
        plt.savefig(top_skills_path, dpi=300)
        plt.close()
        
        # Analyze skills by job title
        if "title_category" in df.columns:
            # Create a dictionary to store skills by job title
            skills_by_title = {}
            
            for title in df["title_category"].unique():
                title_skills = []
                for skills_list in df[df["title_category"] == title]["skills_mentioned"]:
                    if isinstance(skills_list, list):
                        title_skills.extend(skills_list)
                
                skills_by_title[title] = Counter(title_skills)
            
            # Create visualizations for each job title
            for title, skill_counter in skills_by_title.items():
                if not skill_counter:
                    continue
                
                # Convert to dataframe
                title_skill_df = pd.DataFrame(skill_counter.items(), columns=["skill", "count"])
                title_skill_df = title_skill_df.sort_values("count", ascending=False).head(15)
                
                plt.figure(figsize=(12, 8))
                sns.barplot(x="count", y="skill", data=title_skill_df)
                plt.title(f"Top 15 Skills for {title} Positions")
                plt.xlabel("Number of Mentions")
                plt.ylabel("Skill")
                plt.tight_layout()
                
                # Save the plot
                title_skills_path = os.path.join(self.viz_dir, f"skills_{title.lower().replace(' ', '_')}.png")
                plt.savefig(title_skills_path, dpi=300)
                plt.close()
            
            logger.info(f"Saved skills by job title plots to {self.viz_dir}")
        
        # Analyze skill co-occurrence
        if len(all_skills) > 0:
            # Create a matrix of skill co-occurrences
            top_10_skills = [skill for skill, _ in skill_counts.most_common(10)]
            
            # Initialize co-occurrence matrix
            co_occurrence = np.zeros((len(top_10_skills), len(top_10_skills)))
            
            # Fill the matrix
            for skills_list in df["skills_mentioned"]:
                if not isinstance(skills_list, list):
                    continue
                
                for i, skill1 in enumerate(top_10_skills):
                    if skill1 in skills_list:
                        for j, skill2 in enumerate(top_10_skills):
                            if skill2 in skills_list:
                                co_occurrence[i, j] += 1
            
            # Create heatmap
            plt.figure(figsize=(12, 10))
            sns.heatmap(co_occurrence, annot=True, fmt="g", xticklabels=top_10_skills, yticklabels=top_10_skills)
            plt.title("Skill Co-occurrence Matrix (Top 10 Skills)")
            plt.tight_layout()
            
            # Save the plot
            co_occurrence_path = os.path.join(self.viz_dir, "skill_co_occurrence.png")
            plt.savefig(co_occurrence_path, dpi=300)
            plt.close()
            
            logger.info(f"Saved skill co-occurrence matrix to {co_occurrence_path}")
        else:
            co_occurrence_path = None
        
        logger.info(f"Saved skills analysis plots to {self.viz_dir}")
        
        # Return analysis results
        return {
            "top_skills": top_skills.to_dict("records"),
            "skill_counts": skill_df.to_dict("records"),
            "top_skills_path": top_skills_path,
            "co_occurrence_path": co_occurrence_path
        }
    
    def analyze_education_requirements(self, df):
        """
        Analyze education requirements in job listings
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty or "education_required" not in df.columns:
            logger.warning("No education data to analyze")
            return {}
        
        logger.info("Analyzing education requirements in job listings")
        
        # Count education levels
        education_counts = df["education_required"].value_counts().reset_index()
        education_counts.columns = ["education", "count"]
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        sns.barplot(x="count", y="education", data=education_counts)
        plt.title("Education Requirements in Job Listings")
        plt.xlabel("Number of Job Listings")
        plt.ylabel("Education Level")
        plt.tight_layout()
        
        # Save the plot
        education_path = os.path.join(self.viz_dir, "education_requirements.png")
        plt.savefig(education_path, dpi=300)
        plt.close()
        
        # Analyze education by job title
        if "title_category" in df.columns:
            # Create a cross-tabulation
            edu_by_title = pd.crosstab(df["title_category"], df["education_required"])
            
            # Convert to percentages
            edu_by_title_pct = edu_by_title.div(edu_by_title.sum(axis=1), axis=0) * 100
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            sns.heatmap(edu_by_title_pct, annot=True, fmt=".1f", cmap="YlGnBu")
            plt.title("Education Requirements by Job Title (%)")
            plt.tight_layout()
            
            # Save the plot
            edu_by_title_path = os.path.join(self.viz_dir, "education_by_job_title.png")
            plt.savefig(edu_by_title_path, dpi=300)
            plt.close()
            
            logger.info(f"Saved education by job title plot to {edu_by_title_path}")
        else:
            edu_by_title_path = None
        
        logger.info(f"Saved education requirements plot to {education_path}")
        
        # Return analysis results
        return {
            "education_counts": education_counts.to_dict("records"),
            "education_path": education_path,
            "edu_by_title_path": edu_by_title_path
        }
    
    def analyze_job_types(self, df):
        """
        Analyze job types in listings
        
        Args:
            df (DataFrame): Processed job data
            
        Returns:
            dict: Analysis results
        """
        if df is None or df.empty or "job_type" not in df.columns:
            logger.warning("No job type data to analyze")
            return {}
        
        logger.info("Analyzing job types in listings")
        
        # Count job types
        job_type_counts = df["job_type"].value_counts().reset_index()
        job_type_counts.columns = ["job_type", "count"]
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        sns.barplot(x="count", y="job_type", data=job_type_counts)
        plt.title("Job Types in Listings")
        plt.xlabel("Number of Job Listings")
        plt.ylabel("Job Type")
        plt.tight_layout()
        
        # Save the plot
        job_type_path = os.path.join(self.viz_dir, "job_types.png")
        plt.savefig(job_type_path, dpi=300)
        plt.close()
        
        logger.info(f"Saved job types plot to {job_type_path}")
        
        # Return analysis results
        return {
            "job_type_counts": job_type_counts.to_dict("records"),
            "job_type_path": job_type_path
        }
    
    def generate_summary_report(self, analyses):
        """
        Generate a summary report of all analyses
        
        Args:
            analyses (dict): Dictionary containing all analysis results
            
        Returns:
            str: Path to the summary report file
        """
        logger.info("Generating summary report")
        
        # Create timestamp for the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create report content
        report = {
            "timestamp": timestamp,
            "analyses": analyses
        }
        
        # Save report to JSON
        report_path = os.path.join(self.output_dir, f"analysis_summary_{timestamp}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved analysis summary report to {report_path}")
        
        return report_path
    
    def run(self):
        """
        Run the complete data analysis pipeline
        
        Returns:
            dict: Analysis results
        """
        logger.info("Starting job data analysis pipeline")
        
        # Load data
        df = self.load_data()
        
        if df is None:
            logger.error("Failed to load data, cannot proceed with analysis")
            return {}
        
        # Run analyses
        analyses = {}
        
        # Analyze job titles
        analyses["job_titles"] = self.analyze_job_titles(df)
        
        # Analyze locations
        analyses["locations"] = self.analyze_locations(df)
        
        # Analyze salaries
        analyses["salaries"] = self.analyze_salaries(df)
        
        # Analyze skills
        analyses["skills"] = self.analyze_skills(df)
        
        # Analyze education requirements
        analyses["education"] = self.analyze_education_requirements(df)
        
        # Analyze job types
        analyses["job_types"] = self.analyze_job_types(df)
        
        # Generate summary report
        report_path = self.generate_summary_report(analyses)
        analyses["report_path"] = report_path
        
        logger.info("Job data analysis pipeline completed successfully")
        
        return analyses


def main():
    """
    Main function to run the data analysis
    """
    # Set up data directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    processed_data_dir = os.path.join(project_dir, "data", "processed")
    output_dir = os.path.join(project_dir, "data", "output")
    
    # Create analyzer instance
    analyzer = JobDataAnalyzer(processed_data_dir, output_dir)
    
    # Run analysis pipeline
    analyses = analyzer.run()
    
    # Print summary
    print("\nAnalysis Summary:")
    
    if "job_titles" in analyses:
        print("\nJob Titles:")
        if "category_counts" in analyses["job_titles"]:
            for item in analyses["job_titles"]["category_counts"]:
                print(f"  - {item['category']}: {item['count']} listings")
    
    if "locations" in analyses:
        print("\nLocations:")
        if "location_counts" in analyses["locations"]:
            for item in analyses["locations"]["location_counts"]:
                print(f"  - {item['location']}: {item['count']} listings")
    
    if "salaries" in analyses:
        print("\nSalary Statistics:")
        if "salary_stats" in analyses["salaries"]:
            stats = analyses["salaries"]["salary_stats"]
            print(f"  - Average Salary: ${stats['mean']:,.2f}")
            print(f"  - Median Salary: ${stats['median']:,.2f}")
            print(f"  - Salary Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}")
    
    if "skills" in analyses:
        print("\nTop Skills:")
        if "top_skills" in analyses["skills"]:
            for item in analyses["skills"]["top_skills"][:10]:
                print(f"  - {item['skill']}: {item['count']} mentions")
    
    if "education" in analyses:
        print("\nEducation Requirements:")
        if "education_counts" in analyses["education"]:
            for item in analyses["education"]["education_counts"]:
                print(f"  - {item['education']}: {item['count']} listings")
    
    print(f"\nAnalysis results and visualizations saved to {output_dir} and {os.path.join(project_dir, 'visualizations')}")


if __name__ == "__main__":
    main()
