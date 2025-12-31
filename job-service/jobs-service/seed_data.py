"""
Sample data script to populate the database with initial job listings
Run this script after starting the server for the first time
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/jobs"

# Sample jobs data
sample_jobs = [
    {
        "title": "Senior Software Engineer",
        "company": "TechCorp Egypt",
        "location": "Cairo",
        "experience": "5+ years",
        "salary": "30,000 - 45,000 EGP",
        "type": "Hybrid",
        "category": "Software",
        "logo_url": "https://via.placeholder.com/150/0000FF/FFFFFF?text=TechCorp",
        "description": [
            "Join our dynamic team as a Senior Software Engineer",
            "Work on cutting-edge technologies and innovative projects",
            "Collaborate with cross-functional teams to deliver high-quality solutions"
        ],
        "responsibilities": [
            "Design and develop scalable web applications",
            "Lead code reviews and mentor junior developers",
            "Participate in architectural decisions",
            "Ensure code quality and best practices"
        ],
        "soft_skills": [
            "Excellent communication skills",
            "Team player with leadership abilities",
            "Problem-solving mindset",
            "Adaptability to changing requirements"
        ],
        "qualifications": [
            "Bachelor's degree in Computer Science or related field",
            "5+ years of experience in software development",
            "Strong proficiency in Python, JavaScript, or similar languages",
            "Experience with modern frameworks (React, FastAPI, Django, etc.)"
        ]
    },
    {
        "title": "Marketing Manager",
        "company": "Digital Solutions Ltd",
        "location": "Giza",
        "experience": "3-5 years",
        "salary": "20,000 - 30,000 EGP",
        "type": "On-site",
        "category": "Marketing",
        "logo_url": "https://via.placeholder.com/150/FF0000/FFFFFF?text=Digital",
        "description": [
            "Lead our marketing efforts to drive brand awareness and growth",
            "Develop and execute comprehensive marketing strategies",
            "Manage digital marketing campaigns across multiple channels"
        ],
        "responsibilities": [
            "Develop and implement marketing strategies",
            "Manage social media presence and campaigns",
            "Analyze market trends and competitor activities",
            "Coordinate with sales team to align marketing efforts"
        ],
        "soft_skills": [
            "Creative thinking",
            "Strong leadership skills",
            "Excellent written and verbal communication",
            "Data-driven decision making"
        ],
        "qualifications": [
            "Bachelor's degree in Marketing or Business Administration",
            "3-5 years of marketing experience",
            "Proven track record in digital marketing",
            "Experience with marketing analytics tools"
        ]
    },
    {
        "title": "Sales Executive",
        "company": "Global Trade Co",
        "location": "Alexandria",
        "experience": "2-4 years",
        "salary": "15,000 - 25,000 EGP + Commission",
        "type": "On-site",
        "category": "Sales",
        "logo_url": "https://via.placeholder.com/150/00FF00/FFFFFF?text=Global",
        "description": [
            "Drive sales growth and expand our customer base",
            "Build and maintain strong client relationships",
            "Achieve and exceed sales targets"
        ],
        "responsibilities": [
            "Identify and pursue new business opportunities",
            "Present and demonstrate products to potential clients",
            "Negotiate contracts and close deals",
            "Maintain accurate sales records and reports"
        ],
        "soft_skills": [
            "Persuasive communication",
            "Relationship building",
            "Goal-oriented mindset",
            "Resilience and persistence"
        ],
        "qualifications": [
            "Bachelor's degree in Business or related field",
            "2-4 years of sales experience",
            "Proven track record of meeting sales targets",
            "Strong negotiation skills"
        ]
    },
    {
        "title": "Accountant",
        "company": "Finance First",
        "location": "Cairo",
        "experience": "1-3 years",
        "salary": "12,000 - 18,000 EGP",
        "type": "Remote",
        "category": "Accounting",
        "logo_url": "https://via.placeholder.com/150/FFA500/FFFFFF?text=Finance",
        "description": [
            "Manage financial records and ensure accuracy",
            "Prepare financial reports and statements",
            "Support the finance team in various accounting tasks"
        ],
        "responsibilities": [
            "Prepare and maintain financial records",
            "Process accounts payable and receivable",
            "Assist with monthly and annual closings",
            "Ensure compliance with accounting standards"
        ],
        "soft_skills": [
            "Attention to detail",
            "Analytical thinking",
            "Time management",
            "Professional ethics"
        ],
        "qualifications": [
            "Bachelor's degree in Accounting or Finance",
            "1-3 years of accounting experience",
            "Proficiency in accounting software",
            "Knowledge of Egyptian tax regulations"
        ]
    },
    {
        "title": "Mechanical Engineer",
        "company": "Engineering Pro",
        "location": "Giza",
        "experience": "3-6 years",
        "salary": "18,000 - 28,000 EGP",
        "type": "Hybrid",
        "category": "Engineering",
        "logo_url": "https://via.placeholder.com/150/800080/FFFFFF?text=EngPro",
        "description": [
            "Design and develop mechanical systems and components",
            "Work on innovative engineering projects",
            "Collaborate with multidisciplinary teams"
        ],
        "responsibilities": [
            "Design mechanical systems and components",
            "Perform calculations and simulations",
            "Review and approve technical drawings",
            "Conduct testing and quality assurance"
        ],
        "soft_skills": [
            "Technical aptitude",
            "Problem-solving abilities",
            "Team collaboration",
            "Project management"
        ],
        "qualifications": [
            "Bachelor's degree in Mechanical Engineering",
            "3-6 years of engineering experience",
            "Proficiency in CAD software (AutoCAD, SolidWorks)",
            "Strong understanding of engineering principles"
        ]
    },
    {
        "title": "Full Stack Developer",
        "company": "StartupHub",
        "location": "Cairo",
        "experience": "2-4 years",
        "salary": "25,000 - 35,000 EGP",
        "type": "Remote",
        "category": "Software",
        "logo_url": "https://via.placeholder.com/150/FF69B4/FFFFFF?text=StartupHub",
        "description": [
            "Build and maintain web applications from front to back",
            "Work in a fast-paced startup environment",
            "Contribute to product development and innovation"
        ],
        "responsibilities": [
            "Develop frontend and backend components",
            "Design and implement RESTful APIs",
            "Optimize application performance",
            "Collaborate with product team on feature development"
        ],
        "soft_skills": [
            "Self-motivated",
            "Quick learner",
            "Collaborative mindset",
            "Innovative thinking"
        ],
        "qualifications": [
            "Bachelor's degree in Computer Science or equivalent",
            "2-4 years of full stack development experience",
            "Proficiency in React, Node.js, or similar technologies",
            "Experience with databases (SQL and NoSQL)"
        ]
    }
]

def populate_database():
    """Send POST requests to create sample jobs"""
    print("Starting to populate database with sample jobs...")
    print(f"Target URL: {BASE_URL}")
    print("-" * 60)
    
    for idx, job_data in enumerate(sample_jobs, 1):
        try:
            response = requests.post(BASE_URL, json=job_data)
            if response.status_code == 201:
                print(f"✓ [{idx}/{len(sample_jobs)}] Created: {job_data['title']} at {job_data['company']}")
            else:
                print(f"✗ [{idx}/{len(sample_jobs)}] Failed: {job_data['title']} - Status: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ [{idx}/{len(sample_jobs)}] Error creating {job_data['title']}: {str(e)}")
    
    print("-" * 60)
    print("Database population complete!")
    print("\nYou can now:")
    print("1. Visit http://localhost:8000/docs to see the API documentation")
    print("2. Visit http://localhost:8000/api/jobs to see all jobs")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Job Service - Sample Data Populator")
    print("="*60 + "\n")
    print("⚠️  Make sure the FastAPI server is running before executing this script!")
    print("   Start server with: uvicorn main:app --reload")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    populate_database()
