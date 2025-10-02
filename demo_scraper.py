"""
Mock scraper for testing and development.
Provides sample data without making actual web requests.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class MockEuromillionsScraper:
    """Mock scraper that generates realistic test data."""
    
    def __init__(self):
        """Initialize mock scraper."""
        self.base_date = datetime(2024, 1, 5)  # Start from first draw of 2024
        self.max_date = datetime.now() - timedelta(days=3)  # Don't go beyond recent past
    
    def list_recent_draw_urls(self, limit: int = 20) -> List[str]:
        """Generate mock URLs for recent draws."""
        urls = []
        current_date = self.base_date
        
        for i in range(limit):
            # Euromillions draws are typically Tuesday and Friday
            while current_date.weekday() not in [1, 4]:  # Tuesday=1, Friday=4
                current_date += timedelta(days=1)
            
            # Stop if we've reached the maximum allowed date
            if current_date > self.max_date:
                break
            
            date_str = current_date.strftime('%Y-%m-%d')
            url = f"https://www.euro-millions.com/results/{date_str}"
            urls.append(url)
            
            # Move to next potential draw date
            current_date += timedelta(days=3)
        
        return urls
    
    def parse_draw(self, url: str) -> Dict[str, Any]:
        """Generate mock draw data from URL."""
        # Extract date from URL
        import re
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
        if date_match:
            draw_date = date_match.group(1)
        else:
            draw_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate realistic numbers
        main_numbers = sorted(random.sample(range(1, 51), 5))
        star_numbers = sorted(random.sample(range(1, 13), 2))
        
        # Generate realistic jackpot
        jackpot = random.uniform(15_000_000, 150_000_000)
        
        # Generate mock prize table
        prize_table = {
            "5+2": {"winners": random.randint(0, 2), "prize": jackpot},
            "5+1": {"winners": random.randint(1, 5), "prize": random.randint(100000, 500000)},
            "5+0": {"winners": random.randint(3, 12), "prize": random.randint(25000, 75000)},
            "4+2": {"winners": random.randint(10, 50), "prize": random.randint(1000, 5000)},
            "4+1": {"winners": random.randint(100, 500), "prize": random.randint(100, 300)},
            "4+0": {"winners": random.randint(500, 1500), "prize": random.randint(50, 100)},
            "3+2": {"winners": random.randint(500, 2000), "prize": random.randint(30, 80)},
            "3+1": {"winners": random.randint(5000, 15000), "prize": random.randint(10, 25)},
            "3+0": {"winners": random.randint(25000, 75000), "prize": random.randint(8, 15)},
            "2+2": {"winners": random.randint(10000, 30000), "prize": random.randint(5, 12)},
            "2+1": {"winners": random.randint(100000, 300000), "prize": random.randint(3, 8)},
            "2+0": {"winners": random.randint(500000, 1500000), "prize": random.randint(2, 5)},
        }
        
        # Generate mock HTML
        raw_html = f"""
        <html>
        <head><title>Euromillions Results {draw_date}</title></head>
        <body>
        <div class="draw-results">
            <h1>Euromillions Results for {draw_date}</h1>
            <div class="numbers">
                <span class="ball-number">{main_numbers[0]}</span>
                <span class="ball-number">{main_numbers[1]}</span>
                <span class="ball-number">{main_numbers[2]}</span>
                <span class="ball-number">{main_numbers[3]}</span>
                <span class="ball-number">{main_numbers[4]}</span>
                <span class="star-number">{star_numbers[0]}</span>
                <span class="star-number">{star_numbers[1]}</span>
            </div>
            <div class="jackpot">Jackpot: €{jackpot:,.0f}</div>
        </div>
        </body>
        </html>
        """
        
        return {
            "draw_id": draw_date,
            "draw_date": draw_date,
            "n1": main_numbers[0],
            "n2": main_numbers[1],
            "n3": main_numbers[2],
            "n4": main_numbers[3],
            "n5": main_numbers[4],
            "s1": star_numbers[0],
            "s2": star_numbers[1],
            "jackpot": jackpot,
            "prize_table_json": prize_table,
            "raw_html": raw_html
        }
    
    def scrape_latest(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Generate mock data for latest draws."""
        urls = self.list_recent_draw_urls(limit)
        draws = []
        
        for url in urls:
            draw_data = self.parse_draw(url)
            draws.append(draw_data)
        
        return draws


def demo_mock_scraper():
    """Demonstrate mock scraper functionality."""
    print("🎭 Demo: Mock Euromillions Scraper")
    print("=" * 50)
    
    scraper = MockEuromillionsScraper()
    
    # Demo URL listing
    print("\n📋 Recent Draw URLs:")
    urls = scraper.list_recent_draw_urls(5)
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    # Demo single draw parsing
    print(f"\n🎯 Parsing Single Draw:")
    draw = scraper.parse_draw(urls[0])
    print(f"   📅 Draw: {draw['draw_id']}")
    print(f"   🎱 Numbers: {draw['n1']}-{draw['n2']}-{draw['n3']}-{draw['n4']}-{draw['n5']}")
    print(f"   ⭐ Stars: {draw['s1']}-{draw['s2']}")
    print(f"   💰 Jackpot: €{draw['jackpot']:,.0f}")
    print(f"   🏆 Prize categories: {len(draw['prize_table_json'])}")
    
    # Demo batch scraping
    print(f"\n📊 Batch Scraping (3 draws):")
    draws = scraper.scrape_latest(3)
    for draw in draws:
        print(f"   📅 {draw['draw_id']}: {draw['n1']}-{draw['n2']}-{draw['n3']}-{draw['n4']}-{draw['n5']} + {draw['s1']}-{draw['s2']} (€{draw['jackpot']:,.0f})")
    
    # Demo integration with repository
    print(f"\n💾 Repository Integration:")
    try:
        from repository import get_repository, init_database
        
        init_database()
        repo = get_repository()
        
        result = repo.upsert_draws(draws)
        print(f"   📈 Insert result: {result}")
        
        df = repo.all_draws_df()
        print(f"   📊 Total draws in DB: {len(df)}")
        
        latest = repo.latest_draw_date()
        print(f"   📅 Latest draw: {latest}")
        
    except ImportError:
        print("   ⚠️  Repository not available for demo")
    
    print("\n✅ Mock scraper demo completed!")
    return draws

if __name__ == "__main__":
    demo_mock_scraper()
