"""Clean up incorrect date entries in database."""
import sqlite3
from pathlib import Path
from repository import get_repository
import pandas as pd

repo = get_repository()
df = repo.all_draws_df()
df['draw_date'] = pd.to_datetime(df['draw_date'])

# Find incorrect entries (not Tuesday or Friday)
incorrect = df[~df['draw_date'].dt.dayofweek.isin([1, 4])]

print("Incorrect date entries to remove:")
for _, row in incorrect.iterrows():
    date_str = row['draw_date'].strftime('%Y-%m-%d %A')
    nums = f"{row['n1']}-{row['n2']}-{row['n3']}-{row['n4']}-{row['n5']}"
    stars = f"{row['s1']}-{row['s2']}"
    print(f"  ID: {row['draw_id']}, Date: {date_str}")
    print(f"     Numbers: {nums} Stars: {stars}")

# Delete incorrect entries
db_path = Path("data/draws.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

deleted_count = 0
for _, row in incorrect.iterrows():
    draw_id = row['draw_id']
    cursor.execute("DELETE FROM draws WHERE draw_id = ?", (draw_id,))
    deleted_count += cursor.fetchone() if cursor.rowcount == 0 else cursor.rowcount

conn.commit()
conn.close()

print(f"\nDeleted {deleted_count} incorrect entries")

# Verify final state
final_df = repo.all_draws_df()
final_df['draw_date'] = pd.to_datetime(final_df['draw_date'])
final_incorrect = final_df[~final_df['draw_date'].dt.dayofweek.isin([1, 4])]
print(f"Remaining incorrect entries: {len(final_incorrect)}")
print(f"Total draws in database: {len(final_df)}")
