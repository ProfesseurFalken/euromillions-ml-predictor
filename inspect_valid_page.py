"""Inspect a known valid draw page."""
import requests
from bs4 import BeautifulSoup
import re

# Use a known valid date from the results page
url = 'https://www.euro-millions.com/results/23-01-2026'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'})
print(f'URL: {url}')
print(f'Status: {resp.status_code}')
print(f'Page size: {len(resp.text)} bytes')

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Check title
    title = soup.find('title')
    print(f'\nTitle: {title.get_text() if title else "N/A"}')
    
    # Look for all lists with numbers
    print('\n=== All UL elements ===')
    for ul in soup.find_all('ul')[:15]:
        cls = ul.get('class', [])
        lis = ul.find_all('li')
        texts = [li.get_text(strip=True) for li in lis[:7]]
        if any(t.isdigit() for t in texts):
            print(f'UL class={cls}: {texts}')
    
    # Look for spans with numbers
    print('\n=== Spans with single numbers ===')
    for span in soup.find_all('span'):
        txt = span.get_text(strip=True)
        if txt.isdigit() and 1 <= int(txt) <= 50:
            cls = span.get('class', [])
            parent_cls = span.parent.get('class', []) if span.parent else []
            print(f'  {txt} - span class={cls}, parent class={parent_cls}')
    
    # Try regex to find the pattern
    print('\n=== Looking for number sequences in text ===')
    text = soup.get_text()
    # Match 5 numbers followed by 2 stars pattern
    pattern = r'(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})'
    for match in list(re.finditer(pattern, text))[:5]:
        nums = [int(g) for g in match.groups()]
        main = nums[:5]
        stars = nums[5:]
        if all(1 <= n <= 50 for n in main) and all(1 <= s <= 12 for s in stars):
            print(f'  Potential match: {main} | Stars: {stars}')
    
    # Check for structured data
    print('\n=== Looking for structured ball elements ===')
    for selector in ['.ball', '.number', '.winning-number', '[class*="ball"]', '[class*="number"]']:
        elems = soup.select(selector)
        if elems:
            print(f'{selector}: {[e.get_text(strip=True) for e in elems[:10]]}')
