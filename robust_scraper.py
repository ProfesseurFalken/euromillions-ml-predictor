#!/usr/bin/env python3
"""
Robust EuroMillions Scraper
===========================

A reliable scraper for euro-millions.com with proper date and number extraction.
Fixes the issues in the original scraper:
1. Properly extracts dates from URLs (DD-MM-YYYY format)
2. Correctly parses the ul.balls structure for numbers
3. Separates main balls from stars properly
"""

import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings


class RobustEuromillionsScraper:
    """Robust scraper for euro-millions.com with reliable parsing."""
    
    def __init__(self):
        """Initialize scraper."""
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Primary source: euro-millions.com
        self.base_url = "https://www.euro-millions.com"
        self.results_url = f"{self.base_url}/results"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page with retries."""
        logger.debug(f"Fetching: {url}")
        
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        return BeautifulSoup(response.text, 'html.parser')
    
    def get_available_draw_urls(self, limit: int = 100) -> List[Tuple[str, str]]:
        """
        Get list of available draw URLs from the results page.
        
        Returns:
            List of tuples: (url, date_str in YYYY-MM-DD format)
        """
        logger.info(f"Fetching available draw URLs (limit: {limit})")
        
        soup = self._fetch_page(self.results_url)
        
        # Find all result links matching pattern /results/DD-MM-YYYY
        draw_links = []
        pattern = re.compile(r'/results/(\d{2})-(\d{2})-(\d{4})$')
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            match = pattern.search(href)
            if match:
                day, month, year = match.groups()
                iso_date = f"{year}-{month}-{day}"
                full_url = f"{self.base_url}{href}" if href.startswith('/') else href
                draw_links.append((full_url, iso_date))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for url, date in draw_links:
            if date not in seen:
                seen.add(date)
                unique_links.append((url, date))
        
        # Sort by date descending (newest first)
        unique_links.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(unique_links)} unique draw URLs")
        return unique_links[:limit]
    
    def parse_draw_page(self, url: str, expected_date: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single draw page.
        
        Args:
            url: Full URL of the draw page
            expected_date: Expected date in YYYY-MM-DD format (from URL)
            
        Returns:
            Dict with draw data or None if parsing fails
        """
        try:
            soup = self._fetch_page(url)
            
            # Extract numbers from the first ul.balls element
            # Structure: 5 main balls + 2 lucky stars in the first list
            balls_list = soup.find('ul', class_='balls')
            
            if not balls_list:
                logger.warning(f"No ul.balls found on {url}")
                return None
            
            # Get all li elements
            li_elements = balls_list.find_all('li')
            
            if len(li_elements) < 7:
                logger.warning(f"Expected 7 numbers (5+2), found {len(li_elements)} on {url}")
                return None
            
            # Extract numbers - first 5 are main balls, next 2 are stars
            numbers = []
            for li in li_elements[:7]:
                text = li.get_text(strip=True)
                if text.isdigit():
                    numbers.append(int(text))
            
            if len(numbers) != 7:
                logger.warning(f"Could not extract 7 numbers from {url}, got {numbers}")
                return None
            
            main_balls = sorted(numbers[:5])
            stars = sorted(numbers[5:7])
            
            # Validate ranges
            if not all(1 <= n <= 50 for n in main_balls):
                logger.warning(f"Main balls out of range on {url}: {main_balls}")
                return None
            
            if not all(1 <= s <= 12 for s in stars):
                logger.warning(f"Stars out of range on {url}: {stars}")
                return None
            
            # Try to extract jackpot
            jackpot = self._extract_jackpot(soup)
            
            # Build draw record
            draw = {
                "draw_id": expected_date,
                "draw_date": expected_date,
                "n1": main_balls[0],
                "n2": main_balls[1],
                "n3": main_balls[2],
                "n4": main_balls[3],
                "n5": main_balls[4],
                "s1": stars[0],
                "s2": stars[1],
                "jackpot": jackpot,
                "prize_table": None,
                "raw_html": None  # Don't store to save space
            }
            
            logger.info(f"Parsed draw {expected_date}: {main_balls} + {stars}")
            return draw
            
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            return None
    
    def _extract_jackpot(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract jackpot amount from page."""
        try:
            # Look for jackpot in common locations
            jackpot_elem = soup.find(class_=re.compile(r'jackpot', re.I))
            if jackpot_elem:
                text = jackpot_elem.get_text(strip=True)
                # Extract number from text like "€130,000,000"
                match = re.search(r'[\d,]+', text.replace(' ', ''))
                if match:
                    return float(match.group().replace(',', ''))
        except Exception:
            pass
        return None
    
    def scrape_latest(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape latest draws.
        
        Args:
            limit: Maximum number of draws to scrape
            
        Returns:
            List of draw dictionaries
        """
        logger.info(f"Scraping latest {limit} draws from euro-millions.com")
        
        # Get available URLs
        url_list = self.get_available_draw_urls(limit=limit + 10)  # Get extra in case some fail
        
        draws = []
        errors = 0
        
        for url, date_str in url_list:
            if len(draws) >= limit:
                break
                
            draw = self.parse_draw_page(url, date_str)
            if draw:
                draws.append(draw)
            else:
                errors += 1
                if errors > 5:
                    logger.warning("Too many errors, stopping")
                    break
        
        logger.info(f"Successfully scraped {len(draws)} draws")
        return draws
    
    def scrape_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Scrape draws within a specific date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of draw dictionaries
        """
        logger.info(f"Scraping draws from {start_date} to {end_date}")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate expected draw dates (Tuesdays and Fridays)
        expected_dates = []
        current = start
        while current <= end:
            if current.weekday() in [1, 4]:  # Tuesday=1, Friday=4
                expected_dates.append(current)
            current += timedelta(days=1)
        
        draws = []
        
        for date in expected_dates:
            # Format URL date as DD-MM-YYYY
            url_date = date.strftime('%d-%m-%Y')
            iso_date = date.strftime('%Y-%m-%d')
            url = f"{self.base_url}/results/{url_date}"
            
            draw = self.parse_draw_page(url, iso_date)
            if draw:
                draws.append(draw)
        
        logger.info(f"Scraped {len(draws)} draws in date range")
        return draws
    
    def scrape_missing_draws(self, existing_dates: List[str], 
                             start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape only the draws that are missing from the database.
        
        Args:
            existing_dates: List of dates already in database (YYYY-MM-DD format)
            start_date: Optional start date (defaults to earliest expected)
            end_date: Optional end date (defaults to today)
            
        Returns:
            List of missing draw dictionaries
        """
        existing_set = set(existing_dates)
        
        # Determine date range
        if not start_date:
            start_date = min(existing_dates) if existing_dates else '2024-01-01'
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Find missing dates
        missing_dates = []
        current = start
        while current <= end:
            if current.weekday() in [1, 4]:  # Tuesday=1, Friday=4
                iso_date = current.strftime('%Y-%m-%d')
                if iso_date not in existing_set:
                    missing_dates.append(current)
            current += timedelta(days=1)
        
        logger.info(f"Found {len(missing_dates)} missing draws to scrape")
        
        # Scrape missing draws
        draws = []
        for date in missing_dates:
            url_date = date.strftime('%d-%m-%Y')
            iso_date = date.strftime('%Y-%m-%d')
            url = f"{self.base_url}/results/{url_date}"
            
            draw = self.parse_draw_page(url, iso_date)
            if draw:
                draws.append(draw)
        
        return draws


def get_robust_scraper() -> RobustEuromillionsScraper:
    """Get a robust scraper instance."""
    return RobustEuromillionsScraper()


# Convenience function for hybrid_scraper compatibility
def scrape_with_robust_scraper(limit: int = 20) -> List[Dict[str, Any]]:
    """Scrape using the robust scraper."""
    scraper = get_robust_scraper()
    return scraper.scrape_latest(limit)


if __name__ == "__main__":
    # Test the scraper
    print("🎯 Testing Robust EuroMillions Scraper")
    print("=" * 50)
    
    scraper = RobustEuromillionsScraper()
    
    # Test latest draws
    draws = scraper.scrape_latest(limit=5)
    
    print(f"\n✅ Scraped {len(draws)} draws:")
    for draw in draws:
        date = draw['draw_date']
        nums = [draw[f'n{i}'] for i in range(1, 6)]
        stars = [draw['s1'], draw['s2']]
        print(f"  {date}: {nums} | ⭐ {stars}")
