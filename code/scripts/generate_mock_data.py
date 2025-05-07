"""
Mock data generator for Indeed job listings

This script generates mock job data for analysis when web scraping
encounters challenges with anti-scraping measures.

Author: Thinh Nguyen Van
Date: April 14, 2025
"""

import json
import random
import os
from datetime import datetime, timedelta
import sys

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import SCRAPING_CONFIG

# Define constants for mock data generation
JOB_TITLES = SCRAPING_CONFIG["job_titles"]
LOCATIONS = SCRAPING_CONFIG["locations"]

# Company names for mock data
COMPANIES = [
    "TechCorp Solutions", "DataViz Analytics", "Insight Technologies", 
    "Quantum Data Systems", "Nexus Innovations", "ByteWise Solutions",
    "Apex Analytics", "Stellar Data", "Precision Insights", "CoreTech Solutions",
    "DataSphere Inc.", "Analytics Advantage", "Metric Masters", "Insight Innovators",
    "DataDriven Enterprises", "QuantumLeap Analytics", "Visionary Data Solutions",
    "Pinnacle Insights", "Elite Analytics", "TechFusion Data"
]

# Skills for data analyst positions
DATA_SKILLS = [
    "SQL", "Python", "Excel", "Tableau", "Power BI", "R", "SAS", "SPSS",
    "Data Visualization", "Statistical Analysis", "Data Cleaning", "ETL",
    "Data Modeling", "Machine Learning", "Data Mining", "Big Data",
    "Hadoop", "Spark", "AWS", "Azure", "Google Cloud", "Database Management",
    "Data Warehousing", "Business Intelligence", "Data Governance", "Data Quality",
    "Predictive Analytics", "A/B Testing", "Dashboard Development", "Reporting"
]

# Education levels
EDUCATION_LEVELS = [
    "Bachelor's degree", "Master's degree", "PhD", "Associate's degree",
    "High School Diploma", "Certification"
]

# Job types
JOB_TYPES = [
    "Full-time", "Part-time", "Contract", "Temporary", "Internship", "Remote"
]

# Experience levels
EXPERIENCE_LEVELS = [
    "Entry level", "Mid level", "Senior level", "Manager", "Director", "Executive"
]

# Salary ranges
SALARY_RANGES = [
    "$40,000 - $60,000 a year", 
    "$60,000 - $80,000 a year", 
    "$80,000 - $100,000 a year",
    "$100,000 - $120,000 a year", 
    "$120,000 - $140,000 a year", 
    "$140,000 - $160,000 a year",
    "$50 - $70 an hour",
    "$70 - $90 an hour",
    "$90 - $110 an hour"
]

def generate_job_description(job_title):
    """Generate a realistic job description based on job title"""
    
    # Common intro phrases
    intros = [
        f"We are seeking a talented {job_title} to join our team.",
        f"Our client is looking for an experienced {job_title} to help drive business insights.",
        f"Join our growing team as a {job_title} and help transform data into actionable insights.",
        f"Exciting opportunity for a {job_title} to make an impact in a fast-paced environment.",
        f"We're hiring a {job_title} to help us make data-driven decisions."
    ]
    
    # Role descriptions based on job title
    if "Data Analyst" in job_title:
        role = [
            "In this role, you will analyze complex datasets to identify trends and insights.",
            "You will be responsible for creating dashboards and reports to communicate findings to stakeholders.",
            "This position involves cleaning and transforming data to ensure accuracy and reliability.",
            "You will work with cross-functional teams to understand business requirements and provide data-driven solutions."
        ]
        required_skills = random.sample(DATA_SKILLS, 6)
    
    elif "Business Analyst" in job_title:
        role = [
            "In this role, you will bridge the gap between business needs and technical solutions.",
            "You will gather and document business requirements and translate them into functional specifications.",
            "This position involves analyzing business processes and recommending improvements.",
            "You will work closely with stakeholders to ensure solutions meet business objectives."
        ]
        required_skills = random.sample(DATA_SKILLS, 6)
    
    elif "Data Scientist" in job_title:
        role = [
            "In this role, you will develop and implement advanced analytical models.",
            "You will use machine learning techniques to solve complex business problems.",
            "This position involves exploring and visualizing data to uncover hidden patterns.",
            "You will collaborate with stakeholders to translate business questions into analytical frameworks."
        ]
        required_skills = random.sample(DATA_SKILLS, 6)
    
    else:  # Business Intelligence Analyst
        role = [
            "In this role, you will design and build interactive dashboards and reports.",
            "You will transform raw data into meaningful business insights.",
            "This position involves optimizing data collection procedures and ensuring data quality.",
            "You will work with business users to understand reporting needs and deliver solutions."
        ]
        required_skills = random.sample(DATA_SKILLS, 6)
    
    # Qualifications
    education = random.choice(EDUCATION_LEVELS)
    experience = f"{random.randint(1, 7)}+ years of experience in {job_title.lower()} or related field"
    
    # Benefits
    benefits = [
        "Competitive salary and benefits package",
        "Flexible work arrangements",
        "Professional development opportunities",
        "Collaborative and innovative work environment",
        "Health, dental, and vision insurance",
        "401(k) matching",
        "Paid time off and holidays"
    ]
    
    # Combine all sections
    description = f"{random.choice(intros)}\n\n"
    description += "Responsibilities:\n"
    for item in random.sample(role, len(role)):
        description += f"- {item}\n"
    
    description += "\nRequirements:\n"
    description += f"- {education} in Computer Science, Statistics, Mathematics, or related field\n"
    description += f"- {experience}\n"
    for skill in required_skills:
        description += f"- Proficiency in {skill}\n"
    
    description += "\nPreferred Qualifications:\n"
    for skill in random.sample([s for s in DATA_SKILLS if s not in required_skills], 3):
        description += f"- Experience with {skill}\n"
    
    description += "\nBenefits:\n"
    for benefit in random.sample(benefits, 4):
        description += f"- {benefit}\n"
    
    return description

def generate_job_id():
    """Generate a random job ID"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(16))

def generate_search_results(count=200):
    """Generate mock search results"""
    results = []
    
    for _ in range(count):
        job_title = random.choice(JOB_TITLES)
        location = random.choice(LOCATIONS)
        company = random.choice(COMPANIES)
        job_id = generate_job_id()
        
        # Create job listing
        job = {
            "job_id": job_id,
            "title": job_title,
            "company": company,
            "location": location,
            "salary": random.choice(SALARY_RANGES) if random.random() > 0.3 else "N/A",
            "description_snippet": generate_job_description(job_title)[:150] + "...",
            "url": f"https://www.indeed.com/viewjob?jk={job_id}",
            "search_job_title": job_title,
            "search_location": location,
            "date_posted": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "job_type": random.choice(JOB_TYPES),
            "experience_level": random.choice(EXPERIENCE_LEVELS)
        }
        
        results.append(job)
    
    return results

def generate_job_details(search_results):
    """Generate detailed job information based on search results"""
    job_details = []
    
    for result in search_results:
        # Create detailed job listing
        detail = {
            "job_id": result["job_id"],
            "title": result["title"],
            "company": result["company"],
            "location": result["location"],
            "salary": result["salary"],
            "description": generate_job_description(result["title"]),
            "url": result["url"],
            "date_posted": result["date_posted"],
            "job_type": result["job_type"],
            "experience_level": result["experience_level"],
            "required_skills": random.sample(DATA_SKILLS, random.randint(5, 10)),
            "education": random.choice(EDUCATION_LEVELS),
            "benefits": random.sample([
                "Health insurance", "Dental insurance", "Vision insurance",
                "401(k)", "Paid time off", "Flexible schedule", "Remote work option",
                "Professional development", "Tuition reimbursement", "Gym membership",
                "Company events", "Casual dress code", "Free snacks and drinks"
            ], random.randint(4, 8))
        }
        
        job_details.append(detail)
    
    return job_details

def main():
    """Main function to generate mock data"""
    print("Generating mock Indeed job data...")
    
    # Create timestamp for this data generation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create data directories if they don't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    raw_dir = os.path.join(data_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    # Generate search results
    search_results = generate_search_results(200)
    
    # Save search results
    search_results_file = os.path.join(raw_dir, f"indeed_search_results_{timestamp}.json")
    with open(search_results_file, "w") as f:
        json.dump(search_results, f, indent=2)
    
    print(f"Generated {len(search_results)} search results and saved to {search_results_file}")
    
    # Generate job details
    job_details = generate_job_details(search_results)
    
    # Save job details
    job_details_file = os.path.join(raw_dir, f"indeed_job_details_{timestamp}.json")
    with open(job_details_file, "w") as f:
        json.dump(job_details, f, indent=2)
    
    print(f"Generated {len(job_details)} job details and saved to {job_details_file}")
    
    # Create summary file with collection metadata
    summary = {
        "timestamp": timestamp,
        "job_titles": JOB_TITLES,
        "locations": LOCATIONS,
        "search_results_count": len(search_results),
        "job_details_count": len(job_details),
        "search_results_file": f"indeed_search_results_{timestamp}.json",
        "job_details_file": f"indeed_job_details_{timestamp}.json",
        "data_type": "mock"
    }
    
    # Save summary to file
    summary_file = os.path.join(raw_dir, f"collection_summary_{timestamp}.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Generated collection summary and saved to {summary_file}")
    print("Mock data generation completed successfully")

if __name__ == "__main__":
    main()
