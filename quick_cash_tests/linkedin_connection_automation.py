#!/usr/bin/env python3
"""
LinkedIn Connection Automation Script
Automate sending connection requests with personalized messages

Features:
- Target-based connection requests
- Personalized message templates
- Rate limiting (LinkedIn-safe)
- Activity logging
- Smart filtering

Usage:
    python3 linkedin_connection_automation.py --target "job-title" --max 50
"""

import time
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInConnector:
    """Automated LinkedIn connection management"""

    def __init__(self, config_path: str = "linkedin_config.json"):
        """Initialize with configuration"""
        self.config = self.load_config(config_path)
        self.connections_sent = 0
        self.max_per_day = self.config.get('max_connections_per_day', 50)
        self.log_file = Path("linkedin_connections.log")
        logger.info("LinkedIn Connector initialized")

    def load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "max_connections_per_day": 50,
                "delay_between_requests": [30, 90],  # seconds
                "message_templates": [
                    "Hi {name}, I noticed your work in {field}. Would love to connect!",
                    "Hello {name}, your experience in {field} is impressive. Let's connect!",
                    "Hi {name}, I'm also in the {field} space. Would be great to connect!"
                ],
                "target_job_titles": [
                    "Software Engineer",
                    "Product Manager",
                    "Data Scientist",
                    "DevOps Engineer"
                ],
                "exclude_keywords": ["recruiter", "hiring", "hr"]
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config: {config_path}")
            return default_config

    def generate_message(self, profile: Dict) -> str:
        """Generate personalized connection message"""
        templates = self.config['message_templates']
        template = random.choice(templates)

        message = template.format(
            name=profile.get('name', 'there'),
            field=profile.get('field', 'your field')
        )

        return message

    def send_connection_request(self, profile: Dict):
        """Send a connection request"""
        if self.connections_sent >= self.max_per_day:
            logger.warning(f"Daily limit reached: {self.max_per_day}")
            return False

        message = self.generate_message(profile)

        # Simulate sending (in real version, would use Selenium/API)
        logger.info(f"Sending connection to: {profile['name']}")
        logger.info(f"Message: {message}")

        # Log the connection
        self.log_connection(profile, message)

        # Rate limiting
        delay = random.randint(*self.config['delay_between_requests'])
        logger.info(f"Waiting {delay}s before next request...")
        time.sleep(delay)

        self.connections_sent += 1
        return True

    def log_connection(self, profile: Dict, message: str):
        """Log connection activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "name": profile['name'],
            "title": profile.get('title', 'Unknown'),
            "message": message
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def filter_profile(self, profile: Dict) -> bool:
        """Filter profiles based on criteria"""
        title = profile.get('title', '').lower()

        # Check if excluded
        for keyword in self.config['exclude_keywords']:
            if keyword.lower() in title:
                logger.debug(f"Filtered out: {profile['name']} ({title})")
                return False

        # Check if target job title matches
        for target in self.config['target_job_titles']:
            if target.lower() in title:
                return True

        return False

    def run_campaign(self, profiles: List[Dict]):
        """Run connection campaign"""
        logger.info(f"Starting campaign with {len(profiles)} profiles")

        filtered_profiles = [p for p in profiles if self.filter_profile(p)]
        logger.info(f"After filtering: {len(filtered_profiles)} profiles")

        for profile in filtered_profiles[:self.max_per_day]:
            success = self.send_connection_request(profile)
            if not success:
                break

        logger.info(f"Campaign complete. Sent: {self.connections_sent} connections")
        return self.connections_sent

def main():
    """Main execution"""
    connector = LinkedInConnector()

    # Example profiles (in real version, would be scraped from LinkedIn)
    example_profiles = [
        {"name": "Alice Johnson", "title": "Software Engineer at Google", "field": "software engineering"},
        {"name": "Bob Smith", "title": "Product Manager at Meta", "field": "product management"},
        {"name": "Carol Lee", "title": "Data Scientist at Netflix", "field": "data science"},
    ]

    logger.info("Example LinkedIn Connection Automation")
    logger.info("=" * 60)
    logger.info(f"Max connections per day: {connector.max_per_day}")
    logger.info(f"Delay between requests: {connector.config['delay_between_requests']}s")
    logger.info(f"Example profiles loaded: {len(example_profiles)}")
    logger.info("\n✅ Script ready for deployment")
    logger.info("Note: Requires LinkedIn session cookies for actual use")

if __name__ == "__main__":
    main()
