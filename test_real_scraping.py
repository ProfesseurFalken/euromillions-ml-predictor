#!/usr/bin/env python3
"""
Test du scraping réel des données EuroMillions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_real_scraping():
    """Tester le scraping des vraies données."""
    print('🕷️ Test du scraping réel des données EuroMillions')
    print('=' * 55)
    
    try:
        # Test avec le scraper principal
        print('\n1. Test scraper principal...')
        from scraper import EuromillionsScraper
        
        scraper = EuromillionsScraper()
        
        # Essayer de récupérer quelques tirages récents
        print('   Récupération des derniers tirages...')
        draws = scraper.scrape_latest(limit=3)
        
        if draws:
            print(f'✅ {len(draws)} tirages récupérés:')
            for draw in draws:
                date = draw.get('draw_date', 'N/A')
                n1, n2, n3, n4, n5 = draw.get('n1', 0), draw.get('n2', 0), draw.get('n3', 0), draw.get('n4', 0), draw.get('n5', 0)
                s1, s2 = draw.get('s1', 0), draw.get('s2', 0)
                balls = f"{n1:02d}-{n2:02d}-{n3:02d}-{n4:02d}-{n5:02d}"
                stars = f"{s1:02d}-{s2:02d}"
                print(f'   {date}: {balls} | ⭐ {stars}')
        else:
            print('❌ Aucun tirage récupéré par le scraper principal')
            
    except Exception as e:
        print(f'❌ Erreur scraper principal: {e}')
    
    try:
        # Test avec le scraper hybride
        print('\n2. Test scraper hybride...')
        from hybrid_scraper import hybrid_scrape_latest
        
        draws = hybrid_scrape_latest(limit=3)
        
        if draws:
            print(f'✅ {len(draws)} tirages récupérés:')
            for draw in draws:
                date = draw.get('draw_date', 'N/A')
                n1, n2, n3, n4, n5 = draw.get('n1', 0), draw.get('n2', 0), draw.get('n3', 0), draw.get('n4', 0), draw.get('n5', 0)
                s1, s2 = draw.get('s1', 0), draw.get('s2', 0)
                balls = f"{n1:02d}-{n2:02d}-{n3:02d}-{n4:02d}-{n5:02d}"
                stars = f"{s1:02d}-{s2:02d}"
                print(f'   {date}: {balls} | ⭐ {stars}')
        else:
            print('❌ Aucun tirage récupéré par le scraper hybride')
            
    except Exception as e:
        print(f'❌ Erreur scraper hybride: {e}')
    
    try:
        # Test connexion directe UK National Lottery
        print('\n3. Test connexion UK National Lottery...')
        import requests
        from bs4 import BeautifulSoup
        
        url = "https://www.national-lottery.co.uk/results/euromillions"
        
        response = requests.get(url, timeout=10)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f'   Page récupérée: {len(response.content)} bytes')
            print('   ✅ Connexion OK')
        else:
            print(f'   ❌ Erreur HTTP: {response.status_code}')
            
    except Exception as e:
        print(f'❌ Erreur connexion: {e}')

if __name__ == "__main__":
    test_real_scraping()