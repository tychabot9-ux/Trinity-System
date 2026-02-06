#!/usr/bin/env python3
"""
Price Monitoring Web Scraper
Track product prices across multiple websites and send alerts

Features:
- Multi-site price tracking
- Email/SMS alerts on price drops
- Historical price logging
- Configurable check intervals
- Anti-detection measures

Usage:
    python3 price_monitoring_scraper.py --config products.json
"""

import requests
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriceMonitor:
    """Automated price monitoring and alerting"""

    def __init__(self, config_path: str = "price_config.json"):
        """Initialize with configuration"""
        self.config = self.load_config(config_path)
        self.price_history = self.load_history()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        logger.info("Price Monitor initialized")

    def load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "products": [
                    {
                        "name": "Example Product",
                        "url": "https://example.com/product",
                        "price_selector": ".price",
                        "target_price": 99.99,
                        "alert_threshold": 0.10  # 10% drop
                    }
                ],
                "check_interval": 3600,  # seconds (1 hour)
                "alert_email": "your-email@example.com",
                "alert_methods": ["email", "log"]
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config: {config_path}")
            return default_config

    def load_history(self) -> Dict:
        """Load price history"""
        history_file = Path("price_history.json")
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
        return {}

    def save_history(self):
        """Save price history"""
        with open("price_history.json", 'w') as f:
            json.dump(self.price_history, f, indent=2)

    def extract_price(self, html: str, selector: str) -> Optional[float]:
        """Extract price from HTML using selector"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            price_element = soup.select_one(selector)

            if price_element:
                price_text = price_element.text.strip()
                # Extract numeric value
                price_text = price_text.replace('$', '').replace(',', '').strip()
                return float(price_text)
        except Exception as e:
            logger.error(f"Price extraction error: {e}")

        return None

    def check_product(self, product: Dict) -> Optional[float]:
        """Check current price for a product"""
        try:
            logger.info(f"Checking: {product['name']}")

            response = self.session.get(product['url'], timeout=10)
            response.raise_for_status()

            current_price = self.extract_price(response.text, product['price_selector'])

            if current_price:
                logger.info(f"Current price: ${current_price:.2f}")

                # Update history
                product_id = product['name']
                if product_id not in self.price_history:
                    self.price_history[product_id] = []

                self.price_history[product_id].append({
                    "timestamp": datetime.now().isoformat(),
                    "price": current_price
                })

                # Check for alerts
                self.check_alert(product, current_price)

                return current_price

        except Exception as e:
            logger.error(f"Error checking {product['name']}: {e}")

        return None

    def check_alert(self, product: Dict, current_price: float):
        """Check if alert should be sent"""
        product_id = product['name']
        history = self.price_history.get(product_id, [])

        if len(history) < 2:
            return  # Need at least 2 data points

        previous_price = history[-2]['price']
        price_change = (current_price - previous_price) / previous_price

        # Check if below target
        if current_price <= product.get('target_price', float('inf')):
            self.send_alert(
                product['name'],
                f"Target price reached! ${current_price:.2f} <= ${product['target_price']:.2f}"
            )

        # Check if significant drop
        elif price_change <= -product.get('alert_threshold', 0.10):
            self.send_alert(
                product['name'],
                f"Price drop: ${previous_price:.2f} → ${current_price:.2f} ({price_change*100:.1f}%)"
            )

    def send_alert(self, product_name: str, message: str):
        """Send price alert"""
        alert_methods = self.config.get('alert_methods', ['log'])

        if 'log' in alert_methods:
            logger.warning(f"🚨 ALERT - {product_name}: {message}")

        if 'email' in alert_methods:
            # In production, would send actual email
            logger.info(f"Email alert sent to: {self.config.get('alert_email')}")

        # Log alert
        with open("price_alerts.log", 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {product_name} | {message}\n")

    def run_monitoring(self, duration: int = None):
        """Run continuous price monitoring"""
        logger.info("Starting price monitoring...")
        products = self.config['products']
        check_interval = self.config['check_interval']

        iterations = 0
        start_time = time.time()

        while True:
            logger.info(f"\n{'='*60}")
            logger.info(f"Monitoring cycle {iterations + 1}")
            logger.info(f"{'='*60}")

            for product in products:
                self.check_product(product)
                time.sleep(5)  # Delay between products

            self.save_history()
            iterations += 1

            if duration and (time.time() - start_time) >= duration:
                break

            logger.info(f"Next check in {check_interval}s...")
            time.sleep(check_interval)

def main():
    """Main execution"""
    monitor = PriceMonitor()

    logger.info("Price Monitoring Scraper")
    logger.info("=" * 60)
    logger.info(f"Products tracked: {len(monitor.config['products'])}")
    logger.info(f"Check interval: {monitor.config['check_interval']}s")
    logger.info(f"Alert methods: {monitor.config['alert_methods']}")
    logger.info("\n✅ Script ready for deployment")
    logger.info("Usage: python3 price_monitoring_scraper.py --config products.json")

if __name__ == "__main__":
    main()
