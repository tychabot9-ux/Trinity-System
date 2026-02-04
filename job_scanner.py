#!/usr/bin/env python3
"""
Automated Job Board Scanner
Scans Indeed, LinkedIn, and other job boards for matching positions
Runs with low CPU priority to protect trading bot
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
import psutil

load_dotenv()

# Set low CPU priority
p = psutil.Process(os.getpid())
p.nice(10)

# ============================================================================
# SEARCH CRITERIA
# ============================================================================

SEARCH_KEYWORDS = [
    "front desk",
    "concierge",
    "guest services",
    "night audit",
    "hotel receptionist",
    "inn front desk"
]

LOCATION = "Paso Robles, CA"
RADIUS_MILES = 50

# Excluded keywords
EXCLUDE_KEYWORDS = [
    "manager", "director", "supervisor",
    "sales", "timeshare", "commission"
]

MIN_SALARY = 20  # per hour

# ============================================================================
# JOB BOARD SCRAPERS
# ============================================================================

def extract_contact_info(job_description: str) -> Dict:
    """Extract contact information from job description"""
    import re

    contact_info = {}

    # Email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, job_description)
    if emails:
        contact_info['email'] = emails[0]

    # Phone patterns
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, job_description)
    if phones:
        contact_info['phone'] = phones[0]

    # Common contact name patterns
    name_patterns = [
        r'Contact[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)',
        r'Hiring Manager[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s[A-Z][a-z]+),?\s+(?:Hiring|HR|Recruiter)'
    ]

    for pattern in name_patterns:
        names = re.findall(pattern, job_description)
        if names:
            contact_info['name'] = names[0]
            break

    return contact_info

def scan_indeed(keywords: str, location: str) -> List[Dict]:
    """
    Scan Indeed for jobs using RSS feed (lightweight, no browser needed)
    """
    jobs = []

    try:
        print(f"  🔍 Scanning Indeed for: {keywords} in {location}")

        # Use Indeed RSS feed (public, no authentication needed)
        search_query = keywords.replace(' ', '+')
        location_query = location.replace(' ', '+')
        rss_url = f"https://www.indeed.com/rss?q={search_query}&l={location_query}&radius=50"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(rss_url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:5]  # Limit to 5 jobs

            for item in items:
                try:
                    title = item.find('title').text.strip() if item.find('title') else "Unknown Position"
                    link = item.find('link').text.strip() if item.find('link') else ""
                    description = item.find('description').text.strip() if item.find('description') else ""

                    # Parse title (format: "Position - Company - Location")
                    parts = title.split(' - ')
                    position = parts[0] if len(parts) > 0 else title
                    company = parts[1] if len(parts) > 1 else "Unknown Company"

                    # Clean HTML from description
                    desc_soup = BeautifulSoup(description, 'html.parser')
                    clean_description = desc_soup.get_text()

                    # Extract contact info
                    contact_info = extract_contact_info(clean_description)

                    jobs.append({
                        'position': position,
                        'company': company,
                        'description': clean_description,
                        'url': link,
                        'contact_info': contact_info,
                        'source': 'Indeed'
                    })

                    print(f"    ✅ Found: {company} - {position}")

                except Exception as e:
                    print(f"    ⚠️  Error parsing item: {e}")
                    continue

        else:
            print(f"  ⚠️  Indeed returned status {response.status_code}")

    except Exception as e:
        print(f"  ❌ Indeed scan error: {e}")

    return jobs

def scan_linkedin(keywords: str, location: str) -> List[Dict]:
    """
    Scan LinkedIn for jobs using public job search (lightweight)
    """
    jobs = []

    try:
        print(f"  🔍 Scanning LinkedIn for: {keywords} in {location}")

        # Use LinkedIn's public job search
        search_query = keywords.replace(' ', '%20')
        location_query = location.replace(' ', '%20')
        search_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={search_query}&location={location_query}&distance=50&start=0"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        response = requests.get(search_url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('li', limit=5)

            for card in job_cards:
                try:
                    # Extract basic info
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    link_elem = card.find('a', class_='base-card__full-link')

                    if not all([title_elem, company_elem, link_elem]):
                        continue

                    position = title_elem.text.strip()
                    company = company_elem.text.strip()
                    url = link_elem.get('href', '')

                    # Get job description (requires separate request)
                    job_id_match = url.split('/')[-1].split('?')[0] if url else None
                    description = "Visit LinkedIn for full details"

                    jobs.append({
                        'position': position,
                        'company': company,
                        'description': description,
                        'url': url,
                        'contact_info': {},
                        'source': 'LinkedIn'
                    })

                    print(f"    ✅ Found: {company} - {position}")

                except Exception as e:
                    print(f"    ⚠️  Error parsing LinkedIn card: {e}")
                    continue

        else:
            print(f"  ⚠️  LinkedIn returned status {response.status_code}")

    except Exception as e:
        print(f"  ❌ LinkedIn scan error: {e}")

    return jobs

def scan_local_job_boards() -> List[Dict]:
    """
    Scan local Paso Robles / SLO County job boards
    Smaller sites often easier to scrape
    """
    jobs = []

    print("  🔍 Scanning local job boards...")

    # Example: Could scrape:
    # - Local hotel websites directly
    # - SLO County job boards
    # - Hospitality-specific sites

    # TODO: Implement local scrapers

    return jobs

# ============================================================================
# JOB SUBMISSION TO TRINITY
# ============================================================================

def submit_to_trinity(job_data: Dict) -> Dict:
    """Submit found job to Trinity for processing"""
    try:
        response = requests.post(
            "http://localhost:8001/job/apply",
            headers={
                "Authorization": f"Bearer {os.getenv('TRINITY_PASSWORD')}",
                "Content-Type": "application/json"
            },
            json={
                "job_url_or_text": job_data['description'],
                "company": job_data['company'],
                "position": job_data['position']
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# MAIN SCANNER
# ============================================================================

def run_scan():
    """Run a complete job board scan"""
    print(f"\n{'='*70}")
    print(f"  TRINITY AUTO-SCANNER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    print(f"📍 Location: {LOCATION} ({RADIUS_MILES} miles)")
    print(f"🔍 Keywords: {', '.join(SEARCH_KEYWORDS)}")
    print(f"💰 Min Salary: ${MIN_SALARY}/hr\n")

    # Import job status checker
    from job_status import check_duplicate_application

    all_jobs = []
    filtered_jobs = []

    # Scan each keyword
    for keyword in SEARCH_KEYWORDS:
        print(f"\n🔎 Searching: '{keyword}'...")

        # Scan job boards
        indeed_jobs = scan_indeed(keyword, LOCATION)
        linkedin_jobs = scan_linkedin(keyword, LOCATION)
        local_jobs = scan_local_job_boards()

        all_jobs.extend(indeed_jobs)
        all_jobs.extend(linkedin_jobs)
        all_jobs.extend(local_jobs)

        time.sleep(2)  # Rate limiting

    print(f"\n📊 Found {len(all_jobs)} total jobs")

    # Filter out duplicates
    for job in all_jobs:
        duplicate = check_duplicate_application(job['company'], job['position'])
        if duplicate:
            print(f"  ⏭️  Skipping duplicate: {job['company']} - {job['position']}")
        else:
            filtered_jobs.append(job)

    print(f"📋 {len(filtered_jobs)} new jobs after filtering")

    # Submit to Trinity for processing
    if filtered_jobs:
        print(f"\n📤 Submitting to Trinity for analysis...")

        for job in filtered_jobs:
            print(f"  • {job['company']} - {job['position']}")
            result = submit_to_trinity(job)
            print(f"    Status: {result.get('status', 'unknown')}")
            time.sleep(1)  # Rate limiting

    print(f"\n✅ Scan complete!\n")

def run_scheduled_scan():
    """Wrapper for scheduled scans with error handling"""
    try:
        run_scan()
    except Exception as e:
        print(f"❌ Scheduled scan error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test run
    run_scan()
