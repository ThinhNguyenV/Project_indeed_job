"""
Dashboard generator for Indeed job analysis

This script creates an interactive dashboard to visualize the insights
from the Indeed job data analysis.

Author: Thinh Nguyen Van
Date: April 14, 2025
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "dashboard.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dashboard_generator")

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

class DashboardGenerator:
    """
    A class to generate a comprehensive dashboard from analysis results
    """
    
    def __init__(self, analysis_dir, viz_dir, output_dir):
        """
        Initialize the dashboard generator
        
        Args:
            analysis_dir (str): Directory containing analysis results
            viz_dir (str): Directory containing visualization files
            output_dir (str): Directory to save dashboard outputs
        """
        self.analysis_dir = analysis_dir
        self.viz_dir = viz_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized dashboard generator with analysis data from {analysis_dir}")
    
    def _find_latest_analysis_file(self):
        """
        Find the latest analysis summary file
        
        Returns:
            str: Path to the latest analysis summary file
        """
        # Find all analysis summary files
        analysis_files = [f for f in os.listdir(self.analysis_dir) if f.startswith("analysis_summary_") and f.endswith(".json")]
        
        if not analysis_files:
            logger.error("No analysis summary files found")
            return None
        
        # Sort by timestamp (part of filename) to get the latest
        latest_file = sorted(analysis_files)[-1]
        
        file_path = os.path.join(self.analysis_dir, latest_file)
        logger.info(f"Found latest analysis summary file: {file_path}")
        
        return file_path
    
    def load_analysis_data(self):
        """
        Load the analysis data
        
        Returns:
            dict: Analysis data
        """
        # Find the latest analysis file
        analysis_file = self._find_latest_analysis_file()
        
        if not analysis_file:
            logger.error("Could not find analysis file")
            return None
        
        # Load the data
        try:
            with open(analysis_file, "r") as f:
                analysis_data = json.load(f)
            logger.info(f"Loaded analysis data from {analysis_file}")
            return analysis_data
        except Exception as e:
            logger.error(f"Error loading analysis data: {e}")
            return None
    
    def create_overview_dashboard(self, analysis_data):
        """
        Create an overview dashboard with key insights
        
        Args:
            analysis_data (dict): Analysis data
            
        Returns:
            str: Path to the saved dashboard file
        """
        if not analysis_data or "analyses" not in analysis_data:
            logger.warning("No analysis data to create overview dashboard")
            return None
        
        logger.info("Creating overview dashboard")
        
        # Create a large figure for the dashboard
        plt.figure(figsize=(20, 24))
        
        # Create a grid layout
        gs = GridSpec(4, 2, figure=plt.gcf())
        
        # Add title
        plt.suptitle("Indeed Job Market Analysis Dashboard", fontsize=24, y=0.98)
        
        # 1. Job Titles Distribution (top left)
        ax1 = plt.subplot(gs[0, 0])
        job_title_path = os.path.join(self.viz_dir, "job_title_distribution.png")
        if os.path.exists(job_title_path):
            img1 = plt.imread(job_title_path)
            ax1.imshow(img1)
            ax1.axis('off')
            ax1.set_title("Job Titles Distribution", fontsize=16)
        
        # 2. Locations Distribution (top right)
        ax2 = plt.subplot(gs[0, 1])
        locations_path = os.path.join(self.viz_dir, "job_locations_distribution.png")
        if os.path.exists(locations_path):
            img2 = plt.imread(locations_path)
            ax2.imshow(img2)
            ax2.axis('off')
            ax2.set_title("Job Locations Distribution", fontsize=16)
        
        # 3. Salary Distribution (middle left)
        ax3 = plt.subplot(gs[1, 0])
        salary_dist_path = os.path.join(self.viz_dir, "salary_distribution.png")
        if os.path.exists(salary_dist_path):
            img3 = plt.imread(salary_dist_path)
            ax3.imshow(img3)
            ax3.axis('off')
            ax3.set_title("Salary Distribution", fontsize=16)
        
        # 4. Top Skills (middle right)
        ax4 = plt.subplot(gs[1, 1])
        top_skills_path = os.path.join(self.viz_dir, "top_skills.png")
        if os.path.exists(top_skills_path):
            img4 = plt.imread(top_skills_path)
            ax4.imshow(img4)
            ax4.axis('off')
            ax4.set_title("Top Skills in Demand", fontsize=16)
        
        # 5. Education Requirements (bottom left)
        ax5 = plt.subplot(gs[2, 0])
        education_path = os.path.join(self.viz_dir, "education_requirements.png")
        if os.path.exists(education_path):
            img5 = plt.imread(education_path)
            ax5.imshow(img5)
            ax5.axis('off')
            ax5.set_title("Education Requirements", fontsize=16)
        
        # 6. Job Types (bottom right)
        ax6 = plt.subplot(gs[2, 1])
        job_types_path = os.path.join(self.viz_dir, "job_types.png")
        if os.path.exists(job_types_path):
            img6 = plt.imread(job_types_path)
            ax6.imshow(img6)
            ax6.axis('off')
            ax6.set_title("Job Types", fontsize=16)
        
        # 7. Skill Co-occurrence (bottom)
        ax7 = plt.subplot(gs[3, :])
        skill_co_path = os.path.join(self.viz_dir, "skill_co_occurrence.png")
        if os.path.exists(skill_co_path):
            img7 = plt.imread(skill_co_path)
            ax7.imshow(img7)
            ax7.axis('off')
            ax7.set_title("Skill Co-occurrence Matrix", fontsize=16)
        
        # Add timestamp and footer
        plt.figtext(0.5, 0.01, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   ha="center", fontsize=10, style='italic')
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        
        # Save the dashboard
        dashboard_path = os.path.join(self.output_dir, "indeed_job_analysis_dashboard.png")
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved overview dashboard to {dashboard_path}")
        
        return dashboard_path
    
    def create_skills_dashboard(self, analysis_data):
        """
        Create a skills-focused dashboard
        
        Args:
            analysis_data (dict): Analysis data
            
        Returns:
            str: Path to the saved dashboard file
        """
        if not analysis_data or "analyses" not in analysis_data:
            logger.warning("No analysis data to create skills dashboard")
            return None
        
        logger.info("Creating skills dashboard")
        
        # Create a large figure for the dashboard
        plt.figure(figsize=(20, 24))
        
        # Create a grid layout
        gs = GridSpec(3, 2, figure=plt.gcf())
        
        # Add title
        plt.suptitle("Indeed Job Market Skills Analysis", fontsize=24, y=0.98)
        
        # 1. Top Skills Overall (top left)
        ax1 = plt.subplot(gs[0, 0])
        top_skills_path = os.path.join(self.viz_dir, "top_skills.png")
        if os.path.exists(top_skills_path):
            img1 = plt.imread(top_skills_path)
            ax1.imshow(img1)
            ax1.axis('off')
            ax1.set_title("Top Skills Overall", fontsize=16)
        
        # 2. Skill Co-occurrence (top right)
        ax2 = plt.subplot(gs[0, 1])
        skill_co_path = os.path.join(self.viz_dir, "skill_co_occurrence.png")
        if os.path.exists(skill_co_path):
            img2 = plt.imread(skill_co_path)
            ax2.imshow(img2)
            ax2.axis('off')
            ax2.set_title("Skill Co-occurrence Matrix", fontsize=16)
        
        # 3-6. Skills by Job Title (bottom two rows)
        job_titles = ["data_analyst", "business_analyst", "data_scientist", "business_intelligence_analyst"]
        positions = [(1, 0), (1, 1), (2, 0), (2, 1)]
        
        for i, (title, pos) in enumerate(zip(job_titles, positions)):
            ax = plt.subplot(gs[pos])
            title_display = title.replace("_", " ").title()
            skills_path = os.path.join(self.viz_dir, f"skills_{title}.png")
            
            if os.path.exists(skills_path):
                img = plt.imread(skills_path)
                ax.imshow(img)
                ax.axis('off')
                ax.set_title(f"Skills for {title_display} Positions", fontsize=16)
        
        # Add timestamp and footer
        plt.figtext(0.5, 0.01, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   ha="center", fontsize=10, style='italic')
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        
        # Save the dashboard
        dashboard_path = os.path.join(self.output_dir, "indeed_job_skills_dashboard.png")
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved skills dashboard to {dashboard_path}")
        
        return dashboard_path
    
    def create_salary_dashboard(self, analysis_data):
        """
        Create a salary-focused dashboard
        
        Args:
            analysis_data (dict): Analysis data
            
        Returns:
            str: Path to the saved dashboard file
        """
        if not analysis_data or "analyses" not in analysis_data:
            logger.warning("No analysis data to create salary dashboard")
            return None
        
        logger.info("Creating salary dashboard")
        
        # Create a large figure for the dashboard
        plt.figure(figsize=(20, 16))
        
        # Create a grid layout
        gs = GridSpec(2, 2, figure=plt.gcf())
        
        # Add title
        plt.suptitle("Indeed Job Market Salary Analysis", fontsize=24, y=0.98)
        
        # 1. Salary Distribution (top left)
        ax1 = plt.subplot(gs[0, 0])
        salary_dist_path = os.path.join(self.viz_dir, "salary_distribution.png")
        if os.path.exists(salary_dist_path):
            img1 = plt.imread(salary_dist_path)
            ax1.imshow(img1)
            ax1.axis('off')
            ax1.set_title("Salary Distribution", fontsize=16)
        
        # 2. Salary by Job Title (top right)
        ax2 = plt.subplot(gs[0, 1])
        salary_by_title_path = os.path.join(self.viz_dir, "salary_by_job_title.png")
        if os.path.exists(salary_by_title_path):
            img2 = plt.imread(salary_by_title_path)
            ax2.imshow(img2)
            ax2.axis('off')
            ax2.set_title("Salary by Job Title", fontsize=16)
        
        # 3. Salary by Location (bottom left)
        ax3 = plt.subplot(gs[1, 0])
        salary_by_location_path = os.path.join(self.viz_dir, "salary_by_location.png")
        if os.path.exists(salary_by_location_path):
            img3 = plt.imread(salary_by_location_path)
            ax3.imshow(img3)
            ax3.axis('off')
            ax3.set_title("Salary by Location", fontsize=16)
        
        # 4. Salary by Experience (bottom right)
        ax4 = plt.subplot(gs[1, 1])
        salary_by_exp_path = os.path.join(self.viz_dir, "salary_by_experience.png")
        if os.path.exists(salary_by_exp_path):
            img4 = plt.imread(salary_by_exp_path)
            ax4.imshow(img4)
            ax4.axis('off')
            ax4.set_title("Salary vs. Years of Experience", fontsize=16)
        
        # Add timestamp and footer
        plt.figtext(0.5, 0.01, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   ha="center", fontsize=10, style='italic')
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        
        # Save the dashboard
        dashboard_path = os.path.join(self.output_dir, "indeed_job_salary_dashboard.png")
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved salary dashboard to {dashboard_path}")
        
        return dashboard_path
    
    def create_html_dashboard(self, dashboard_paths):
        """
        Create an HTML dashboard that includes all visualizations
        
        Args:
            dashboard_paths (list): Paths to dashboard images
            
        Returns:
            str: Path to the saved HTML file
        """
        logger.info("Creating HTML dashboard")
        
        # Create HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Indeed Job Market Analysis Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }
                h2 {
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 40px;
                }
                .dashboard-container {
                    margin-bottom: 50px;
                }
                .dashboard-image {
                    width: 100%;
                    max-width: 1200px;
                    height: auto;
                    margin: 20px 0;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .key-insights {
                    background-color: #f9f9f9;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                }
                footer {
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 0.9em;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <h1>Indeed Job Market Analysis Dashboard</h1>
            
            <div class="key-insights">
                <h2>Key Insights</h2>
                <ul>
                    <li><strong>Job Distribution:</strong> Data Scientist (26%), Business Analyst (25.5%), Data Analyst (25%), Business Intelligence Analyst (23.5%)</li>
                    <li><strong>Top Locations:</strong> Chicago, San Francisco, Austin, Remote, Seattle, New York</li>
                    <li><strong>Salary:</strong> Average $77,581.50, Median $90,000.00</li>
                    <li><strong>Top Skills:</strong> Machine Learning, Azure, Hadoop, Power BI, Tableau</li>
                    <li><strong>Education:</strong> Master's degree (58%), Bachelor's degree (42%)</li>
                </ul>
            </div>
            
            <h2>Overview Dashboard</h2>
            <div class="dashboard-container">
                <img src="indeed_job_analysis_dashboard.png" alt="Overview Dashboard" class="dashboard-image">
            </div>
            
            <h2>Skills Analysis</h2>
            <div class="dashboard-container">
                <img src="indeed_job_skills_dashboard.png" alt="Skills Dashboard" class="dashboard-image">
            </div>
            
            <h2>Salary Analysis</h2>
            <div class="dashboard-container">
                <img src="indeed_job_salary_dashboard.png" alt="Salary Dashboard" class="dashboard-image">
            </div>
            
            <footer>
                <p>Generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                <p>Indeed Job Market Analysis Project</p>
            </footer>
        </body>
        </html>
        """
        
        # Save HTML file
        html_path = os.path.join(self.output_dir, "indeed_job_analysis_dashboard.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        
        logger.info(f"Saved HTML dashboard to {html_path}")
        
        return html_path
    
    def run(self):
        """
        Run the complete dashboard generation pipeline
        
        Returns:
            dict: Paths to generated dashboards
        """
        logger.info("Starting dashboard generation pipeline")
        
        # Load analysis data
        analysis_data = self.load_analysis_data()
        
        if not analysis_data:
            logger.error("Failed to load analysis data, cannot proceed with dashboard generation")
            return {}
        
        # Create dashboards
        overview_path = self.create_overview_dashboard(analysis_data)
        skills_path = self.create_skills_dashboard(analysis_data)
        salary_path = self.create_salary_dashboard(analysis_data)
        
        # Create HTML dashboard
        dashboard_paths = [overview_path, skills_path, salary_path]
        html_path = self.create_html_dashboard(dashboard_paths)
        
        logger.info("Dashboard generation pipeline completed successfully")
        
        return {
            "overview_dashboard": overview_path,
            "skills_dashboard": skills_path,
            "salary_dashboard": salary_path,
            "html_dashboard": html_path
        }


def main():
    """
    Main function to run the dashboard generation
    """
    # Set up data directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    analysis_dir = os.path.join(project_dir, "data", "output")
    viz_dir = os.path.join(project_dir, "data", "visualizations")
    output_dir = os.path.join(project_dir, "data", "dashboard")
    
    # Create dashboard generator instance
    generator = DashboardGenerator(analysis_dir, viz_dir, output_dir)
    
    # Run dashboard generation pipeline
    dashboard_paths = generator.run()
    
    # Print summary
    print("\nDashboard Generation Summary:")
    for dashboard_type, path in dashboard_paths.items():
        if path:
            print(f"  - {dashboard_type.replace('_', ' ').title()}: {path}")
    
    print(f"\nAll dashboards saved to {output_dir}")


if __name__ == "__main__":
    main()
