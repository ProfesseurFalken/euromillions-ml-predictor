#!/usr/bin/env python3
"""
Fix Missing Draws in Database
==============================

This script identifies and scrapes missing draws from the database,
then updates the database with the correct data.
"""

import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

from repository import get_repository
from robust_scraper import RobustEuromillionsScraper


def get_expected_draw_dates(start_date: str, end_date: str) -> list:
    """Generate list of expected draw dates (Tuesdays and Fridays)."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    dates = []
    current = start
    while current <= end:
        if current.weekday() in [1, 4]:  # Tuesday=1, Friday=4
            dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return dates


def find_missing_draws(df: pd.DataFrame) -> list:
    """Find draws that are missing from the database."""
    if df.empty:
        return []
    
    # Get actual dates in database
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    actual_dates = set(df['draw_date'].dt.strftime('%Y-%m-%d'))  # type: ignore[union-attr]
    
    # Determine date range
    start_date = df['draw_date'].min().strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get expected dates
    expected_dates = get_expected_draw_dates(start_date, end_date)
    expected_set = set(expected_dates)
    
    # Find missing
    missing = sorted(expected_set - actual_dates)
    
    return missing


def find_incorrect_dates(df: pd.DataFrame) -> list:
    """Find draws with incorrect dates (not Tuesday or Friday)."""
    if df.empty:
        return []
    
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    incorrect = []
    
    for _, row in df.iterrows():
        date = row['draw_date']
        if date.weekday() not in [1, 4]:  # Not Tuesday or Friday
            incorrect.append({
                'draw_id': row['draw_id'],
                'draw_date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'numbers': [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']],
                'stars': [row['s1'], row['s2']]
            })
    
    return incorrect


def scrape_and_fix_missing(missing_dates: list, scraper: RobustEuromillionsScraper) -> list:
    """Scrape missing draws from the website."""
    draws = []
    
    # Filter to only recent dates (within last 2 years - website might not have older)
    cutoff = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    recent_missing = [d for d in missing_dates if d >= cutoff]
    
    logger.info(f"Attempting to scrape {len(recent_missing)} recent missing draws")
    
    for date_str in recent_missing:
        # Convert YYYY-MM-DD to DD-MM-YYYY for URL
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        url_date = date_obj.strftime('%d-%m-%Y')
        url = f"{scraper.base_url}/results/{url_date}"
        
        draw = scraper.parse_draw_page(url, date_str)
        if draw:
            draws.append(draw)
            logger.info(f"✅ Found: {date_str}")
        else:
            logger.warning(f"❌ Not found: {date_str}")
    
    return draws


def main():
    """Main function to fix missing draws."""
    print("=" * 60)
    print("🔧 EuroMillions Database Fixer")
    print("=" * 60)
    
    # Initialize
    repo = get_repository()
    scraper = RobustEuromillionsScraper()
    
    # Load current data
    print("\n📊 Loading current database...")
    df = repo.all_draws_df()
    print(f"   Total draws in database: {len(df)}")
    
    if df.empty:
        print("   ⚠️  Database is empty!")
        return
    
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    print(f"   Date range: {df['draw_date'].min().strftime('%Y-%m-%d')} to {df['draw_date'].max().strftime('%Y-%m-%d')}")
    
    # Find issues
    print("\n🔍 Analyzing database...")
    
    # 1. Find incorrect dates
    incorrect = find_incorrect_dates(df)
    if incorrect:
        print(f"\n⚠️  Found {len(incorrect)} draws with incorrect dates (not Tue/Fri):")
        for item in incorrect[:10]:
            print(f"   - {item['draw_date']} ({item['day_name']}): {item['numbers']} | ⭐ {item['stars']}")
        if len(incorrect) > 10:
            print(f"   ... and {len(incorrect) - 10} more")
    
    # 2. Find missing dates
    missing = find_missing_draws(df)
    if missing:
        print(f"\n❌ Found {len(missing)} missing draws:")
        for date in missing[:20]:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            print(f"   - {date} ({date_obj.strftime('%A')})")
        if len(missing) > 20:
            print(f"   ... and {len(missing) - 20} more")
    
    # 3. Scrape missing draws
    if missing:
        print(f"\n🌐 Scraping missing draws from euro-millions.com...")
        new_draws = scrape_and_fix_missing(missing, scraper)
        
        if new_draws:
            print(f"\n📥 Inserting {len(new_draws)} new draws into database...")
            result = repo.upsert_draws(new_draws)
            print(f"   Inserted: {result['inserted']}")
            print(f"   Updated: {result['updated']}")
            print(f"   Errors: {result['errors']}")
        else:
            print("   No draws could be scraped")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 Final Status")
    print("=" * 60)
    
    final_df = repo.all_draws_df()
    print(f"   Total draws: {len(final_df)}")
    
    final_missing = find_missing_draws(final_df)
    print(f"   Still missing: {len(final_missing)}")
    
    final_incorrect = find_incorrect_dates(final_df)
    print(f"   Incorrect dates: {len(final_incorrect)}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
