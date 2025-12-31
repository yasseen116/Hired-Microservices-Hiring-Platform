"""
Test script for logo upload functionality
"""
import requests
import json
from pathlib import Path

# API endpoint
URL = "http://localhost:8000/api/jobs/with-logo"

# Path to test image
test_logo_path = Path("C:/Users/YasseenMohamed/.gemini/antigravity/brain/62bb0f89-fd07-4e8f-a239-a02006741ed4/test_company_logo_1766591837399.png")

# Prepare form data
data = {
    'title': 'Full Stack Developer with Logo',
    'company': 'LogoTech Corp',
    'location': 'Cairo',
    'experience': '3-5 years',
    'salary': '25,000-35,000 EGP',
    'type': 'Hybrid',
    'category': 'Software',
    'description': json.dumps(['Build full stack applications', 'Work with modern tech stack']),
    'responsibilities': json.dumps(['Lead development', 'Mentor juniors']),
    'soft_skills': json.dumps(['Leadership', 'Communication']),
    'qualifications': json.dumps(['5+ years experience', 'BSc in CS'])
}

print("="*60)
print("Testing Logo Upload Feature")
print("="*60)
print(f"\nTest logo path: {test_logo_path}")
print(f"File exists: {test_logo_path.exists()}\n")

if not test_logo_path.exists():
    print(f"ERROR: Test logo file not found at {test_logo_path}")
    exit(1)

# Prepare file
files = {
    'logo': ('test_company_logo.png', open(test_logo_path, 'rb'), 'image/png')
}

print("Sending request to API...")
print(f"URL: {URL}\n")

try:
    response = requests.post(URL, data=data, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print("-"*60)
    
    if response.status_code == 201:
        job_data = response.json()
        print(json.dumps(job_data, indent=2))
        print("-"*60)
        print(f"\n✅ SUCCESS! Job created with ID: {job_data.get('id')}")
        
        logo_url = job_data.get('logoUrl')
        if logo_url:
            print(f"✅ Logo URL: {logo_url}")
            
            # Test retrieving the logo
            full_url = f"http://localhost:8000{logo_url}"
            print(f"\nTesting logo retrieval from: {full_url}")
            
            logo_response = requests.get(full_url)
            if logo_response.status_code == 200:
                print(f"✅ Logo retrieved successfully! (Size: {len(logo_response.content)} bytes)")
            else:
                print(f"❌ Failed to retrieve logo. Status: {logo_response.status_code}")
        else:
            print("⚠️ No logo URL in response")
    else:
        print(json.dumps(response.json(), indent=2))
        print("-"*60)
        print(f"\n❌ FAILED with status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to the server.")
    print("Make sure the server is running: python -m uvicorn main:app --reload")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "="*60)
