"""Inspect real draw page structure."""
import requests
from bs4 import BeautifulSoup
import re

# Try a recent valid date (Friday Jan 24, 2026)
url = 'https://www.euro-millions.com/results/24-01-2026'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f'URL: {url}')
print(f'Status: {resp.status_code}')

soup = BeautifulSoup(resp.text, 'html.parser')

# Look for the winning numbers structure
print('\n=== Looking for balls ===')
balls = soup.find_all('li', class_=lambda x: x and 'ball' in str(x).lower() if x else False)
for b in balls[:10]:
    cls = b.get('class')
    txt = b.get_text(strip=True)
    print(f'  class={cls}: "{txt}"')

# Look for ul with balls
print('\n=== Looking for number lists ===')
uls = soup.find_all('ul')
for ul in uls:
    cls = ul.get('class', [])
    if any('ball' in str(c).lower() or 'number' in str(c).lower() or 'result' in str(c).lower() for c in cls):
        print(f'UL class={cls}')
        for li in ul.find_all('li')[:7]:
            print(f'  - {li.get_text(strip=True)}')

# Try looking at the actual HTML structure around numbers
print('\n=== Searching for specific patterns ===')
# EuroMillions results often have balls in specific divs
for div in soup.find_all('div'):
    cls = str(div.get('class', []))
    if 'ball' in cls.lower() or 'winning' in cls.lower() or 'result' in cls.lower():
        print(f'\nDIV class={div.get("class")}:')
        print(div.get_text(strip=True)[:200])

# Check title for date
title = soup.find('title')
if title:
    print(f'\n=== Page Title ===\n{title.get_text()}')

# Check h1
h1 = soup.find('h1')
if h1:
    print(f'\n=== H1 ===\n{h1.get_text(strip=True)}')

# Look for JSON data embedded in scripts
print('\n=== Looking for JSON data ===')
scripts = soup.find_all('script')
for script in scripts:
    txt = script.get_text()
    if 'numbers' in txt.lower() or 'balls' in txt.lower() or 'winning' in txt.lower():
        # Find JSON-like patterns
        json_match = re.search(r'\{[^{}]*"numbers"[^{}]*\}', txt)
        if json_match:
            print(f'Found JSON: {json_match.group()[:200]}')
