"""Analyze missing draws in the database."""
import pandas as pd
from datetime import datetime, timedelta
from repository import get_repository

repo = get_repository()
df = repo.all_draws_df()

print(f"Total draws in database: {len(df)}")
print(f"Date range: {df['draw_date'].min()} to {df['draw_date'].max()}")

# Ensure datetime
df['draw_date'] = pd.to_datetime(df['draw_date'])
df = df.sort_values('draw_date')

# Generate expected dates (Tue=1, Fri=4)
start_date = df['draw_date'].min()
end_date = df['draw_date'].max()

expected_dates = []
current = start_date
while current <= end_date:
    if current.weekday() in [1, 4]:  # Tuesday or Friday
        expected_dates.append(current.normalize())  # type: ignore[union-attr]
    current += timedelta(days=1)

actual_dates = set(df['draw_date'].dt.normalize())  # type: ignore[union-attr]
expected_set = set(expected_dates)

missing = sorted(expected_set - actual_dates)
extra = sorted(actual_dates - expected_set)

print(f"\nExpected draws (Tue/Fri): {len(expected_set)}")
print(f"Actual draws: {len(actual_dates)}")
print(f"Missing draws: {len(missing)}")
print(f"Extra (non Tue/Fri): {len(extra)}")

if missing:
    print(f"\n=== MISSING DRAWS ({len(missing)}) ===")
    for d in missing[:30]:
        print(f"  - {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})")
    if len(missing) > 30:
        print(f"  ... and {len(missing) - 30} more")

if extra:
    print(f"\n=== EXTRA DRAWS (not Tue/Fri) ===")
    for d in extra[:10]:
        print(f"  - {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})")

# Check recent draws (last 30 days)
print("\n=== RECENT 30 DAYS ANALYSIS ===")
recent_start = end_date - timedelta(days=30)
recent_expected = [d for d in expected_dates if d >= recent_start]
recent_actual = [d for d in actual_dates if d >= recent_start]
recent_missing = set(recent_expected) - set(recent_actual)

print(f"Expected in last 30 days: {len(recent_expected)}")
print(f"Actual in last 30 days: {len(recent_actual)}")
if recent_missing:
    print("Missing in last 30 days:")
    for d in sorted(recent_missing):
        print(f"  - {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})")
else:
    print("No missing draws in last 30 days!")

# Show last 10 draws in DB
print("\n=== LAST 10 DRAWS IN DATABASE ===")
last_10 = df.tail(10)[['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']]
for _, row in last_10.iterrows():
    date_str = row['draw_date'].strftime('%Y-%m-%d (%A)')
    nums = f"{row['n1']:2d}-{row['n2']:2d}-{row['n3']:2d}-{row['n4']:2d}-{row['n5']:2d}"
    stars = f"{row['s1']:2d}-{row['s2']:2d}"
    print(f"  {date_str}: {nums} | ⭐ {stars}")
