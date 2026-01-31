#!/usr/bin/env python3
"""
Update EuroMillions Database
============================

Smart update script that only scrapes missing draws.
Can be run regularly to keep the database up to date.
"""

import sys
from datetime import datetime, timedelta
from typing import List, Set
import pandas as pd
from loguru import logger

from repository import get_repository
from robust_scraper import RobustEuromillionsScraper


def get_expected_dates_since(start_date: str) -> Set[str]:
    """Get all expected draw dates (Tue/Fri) since start_date."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.now()
    
    dates = set()
    current = start
    while current <= end:
        if current.weekday() in [1, 4]:  # Tuesday=1, Friday=4
            dates.add(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return dates


def update_database(days_back: int = 30, verbose: bool = True) -> dict:
    """
    Update the database with any missing draws.
    
    Args:
        days_back: How many days back to check for missing draws
        verbose: Whether to print progress
        
    Returns:
        dict with update statistics
    """
    repo = get_repository()
    scraper = RobustEuromillionsScraper()
    
    # Load current data
    df = repo.all_draws_df()
    
    if df.empty:
        if verbose:
            print("⚠️  Database is empty, running full initialization...")
        # Get last 100 draws
        draws = scraper.scrape_latest(limit=100)
        result = repo.upsert_draws(draws)
        return {
            'checked': 0,
            'missing': len(draws),
            'scraped': len(draws),
            'inserted': result['inserted'],
            'updated': result['updated'],
            'errors': result['errors']
        }
    
    # Get date range to check
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    latest_date = df['draw_date'].max()
    check_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Get actual dates in database
    actual_dates = set(df['draw_date'].dt.strftime('%Y-%m-%d'))  # type: ignore[union-attr]
    
    # Get expected dates
    expected_dates = get_expected_dates_since(check_from)
    
    # Find missing dates (only within check range)
    missing_dates = sorted(expected_dates - actual_dates)
    
    if verbose:
        print(f"📊 Database has {len(df)} draws")
        print(f"📅 Latest draw: {latest_date.strftime('%Y-%m-%d')}")
        print(f"🔍 Checking last {days_back} days...")
        print(f"❌ Missing draws: {len(missing_dates)}")
    
    if not missing_dates:
        if verbose:
            print("✅ Database is up to date!")
        return {
            'checked': len(expected_dates),
            'missing': 0,
            'scraped': 0,
            'inserted': 0,
            'updated': 0,
            'errors': 0
        }
    
    # Scrape missing draws
    if verbose:
        print(f"\n🌐 Scraping {len(missing_dates)} missing draws...")
    
    scraped_draws = []
    errors = 0
    
    for date_str in missing_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        url_date = date_obj.strftime('%d-%m-%Y')
        url = f"{scraper.base_url}/results/{url_date}"
        
        draw = scraper.parse_draw_page(url, date_str)
        if draw:
            scraped_draws.append(draw)
            if verbose:
                nums = [draw[f'n{i}'] for i in range(1, 6)]
                stars = [draw['s1'], draw['s2']]
                print(f"  ✅ {date_str}: {nums} | ⭐ {stars}")
        else:
            errors += 1
            if verbose:
                print(f"  ❌ {date_str}: Could not scrape")
    
    # Insert into database
    result = {'inserted': 0, 'updated': 0, 'errors': 0}
    if scraped_draws:
        result = repo.upsert_draws(scraped_draws)
        if verbose:
            print(f"\n📥 Inserted: {result['inserted']}, Updated: {result['updated']}")
    
    return {
        'checked': len(expected_dates),
        'missing': len(missing_dates),
        'scraped': len(scraped_draws),
        'inserted': result['inserted'],
        'updated': result['updated'],
        'errors': errors + result['errors']
    }


def main():
    """Main entry point."""
    print("=" * 60)
    print("🔄 EuroMillions Database Updater")
    print("=" * 60)
    
    # Check for command line arguments
    days_back = 30
    if len(sys.argv) > 1:
        try:
            days_back = int(sys.argv[1])
        except ValueError:
            pass
    
    result = update_database(days_back=days_back, verbose=True)
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"   Dates checked: {result['checked']}")
    print(f"   Missing found: {result['missing']}")
    print(f"   Successfully scraped: {result['scraped']}")
    print(f"   Inserted: {result['inserted']}")
    print(f"   Updated: {result['updated']}")
    print(f"   Errors: {result['errors']}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
