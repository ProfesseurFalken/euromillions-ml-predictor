"""Inspect actual webpage structure to fix scraper."""
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.euro-millions.com/results/28-01-2026'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')

print(f"Page size: {len(resp.text)} bytes")
print(f"Status: {resp.status_code}")

print('\n=== Looking for ball/number elements ===')
for cls in ['ball', 'number', 'lucky', 'result', 'winning']:
    elems = soup.find_all(class_=lambda x: x and cls in x.lower() if x else False)
    if elems:
        print(f'\nFound {len(elems)} elements with class containing "{cls}"')
        for e in elems[:8]:
            txt = e.get_text(strip=True)[:60]
            print(f'  - <{e.name}> class={e.get("class")}: "{txt}"')

print('\n=== Looking for specific number patterns ===')
# Look for li elements with numbers
lis = soup.find_all('li')
for li in lis[:20]:
    txt = li.get_text(strip=True)
    if txt.isdigit() and 1 <= int(txt) <= 50:
        print(f'Found number in <li>: {txt}, class={li.get("class")}')

print('\n=== Looking for date elements ===')
for tag in ['time', 'span', 'div', 'h1', 'h2']:
    for elem in soup.find_all(tag):
        txt = elem.get_text(strip=True)
        if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', txt) or re.search(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', txt):
            print(f'Date in <{tag}>: "{txt[:80]}"')
        if 'january' in txt.lower() or 'february' in txt.lower() or '2026' in txt or '2025' in txt:
            if len(txt) < 100:
                print(f'Date-like in <{tag}>: "{txt}"')

print('\n=== Checking URL date pattern ===')
# The URL contains the date: results/28-01-2026 (DD-MM-YYYY format)
match = re.search(r'/results/(\d{2})-(\d{2})-(\d{4})', url)
if match:
    day, month, year = match.groups()
    iso_date = f"{year}-{month}-{day}"
    print(f"URL date extracted: {iso_date}")
