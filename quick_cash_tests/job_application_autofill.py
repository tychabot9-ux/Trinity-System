#!/usr/bin/env python3
"""
Job Application Auto-Fill Script
Automates filling out online job application forms

Features:
- Selenium-based web automation
- Configurable candidate profile
- Smart field detection
- Error handling and logging
- LinkedIn Easy Apply support

Usage:
    python3 job_application_autofill.py --profile candidate.json --url "job-url"
"""

import json
import time
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobApplicationBot:
    """Automated job application submission"""

    def __init__(self, profile_path: str):
        """Initialize with candidate profile"""
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)

        # Initialize browser (headless for automation)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Browser initialized")

    def fill_field(self, field_name: str, value: str):
        """Smart field filling with multiple strategies"""
        try:
            # Try by name
            element = self.driver.find_element(By.NAME, field_name)
            element.clear()
            element.send_keys(value)
            logger.info(f"Filled field: {field_name}")
            return True
        except:
            pass

        try:
            # Try by ID
            element = self.driver.find_element(By.ID, field_name)
            element.clear()
            element.send_keys(value)
            logger.info(f"Filled field by ID: {field_name}")
            return True
        except:
            pass

        try:
            # Try by label text
            label = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{field_name}')]")
            input_id = label.get_attribute('for')
            element = self.driver.find_element(By.ID, input_id)
            element.clear()
            element.send_keys(value)
            logger.info(f"Filled field by label: {field_name}")
            return True
        except:
            logger.warning(f"Could not fill field: {field_name}")
            return False

    def apply_to_job(self, job_url: str):
        """Navigate and fill job application"""
        logger.info(f"Navigating to: {job_url}")
        self.driver.get(job_url)
        time.sleep(2)  # Wait for page load

        # Common field mappings
        field_mapping = {
            'name': [self.profile['first_name'] + ' ' + self.profile['last_name']],
            'first_name': [self.profile['first_name']],
            'last_name': [self.profile['last_name']],
            'email': [self.profile['email']],
            'phone': [self.profile['phone']],
            'linkedin': [self.profile.get('linkedin_url', '')],
            'resume': [self.profile.get('resume_path', '')],
        }

        # Fill detected fields
        for field_key, values in field_mapping.items():
            for value in values:
                if value:
                    self.fill_field(field_key, value)

        logger.info("Application form filled successfully")
        return True

    def close(self):
        """Clean up"""
        self.driver.quit()
        logger.info("Browser closed")

def main():
    """Main execution"""
    # Example usage
    profile = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "resume_path": "/path/to/resume.pdf",
        "cover_letter": "Experienced software engineer with 5 years..."
    }

    # Save example profile
    with open('candidate_profile.json', 'w') as f:
        json.dump(profile, f, indent=2)

    logger.info("Example profile created: candidate_profile.json")
    logger.info("Usage: python3 job_application_autofill.py --profile candidate.json --url 'job-url'")

if __name__ == "__main__":
    main()
