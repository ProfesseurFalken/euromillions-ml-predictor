"""
SQLite repository for Euromillions draw data.
Handles database operations with automatic schema creation and data management.
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import pandas as pd
from config import get_settings


class EuromillionsRepository:
    """Repository for managing Euromillions draw data in SQLite."""
    
    def __init__(self):
        """Initialize repository with settings."""
        self.settings = get_settings()
        self._db_path = self._extract_db_path()
    
    def _extract_db_path(self) -> Path:
        """Extract database file path from DB_URL."""
        db_url = self.settings.db_url
        
        # Handle sqlite:///path format
        if db_url.startswith("sqlite:///"):
            path_str = db_url[10:]  # Remove 'sqlite:///'
        elif db_url.startswith("sqlite://"):
            path_str = db_url[9:]   # Remove 'sqlite://'
        else:
            # Assume it's already a path
            path_str = db_url
        
        return Path(path_str)
    
    @contextmanager
    def _connect(self):
        """
        Create database connection and ensure schema exists.
        
        Yields:
            sqlite3.Connection: Database connection with row factory
        """
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        try:
            # Create tables if they don't exist
            self._create_tables_if_missing(conn)
            yield conn
        finally:
            conn.close()
    
    def _create_tables_if_missing(self, conn: sqlite3.Connection) -> None:
        """Create database tables if they don't exist."""
        cursor = conn.cursor()
        
        # Create draws table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS draws (
                draw_id TEXT PRIMARY KEY,
                draw_date TEXT,
                n1 INTEGER,
                n2 INTEGER,
                n3 INTEGER,
                n4 INTEGER,
                n5 INTEGER,
                s1 INTEGER,
                s2 INTEGER,
                jackpot REAL,
                prize_table_json TEXT,
                raw_html TEXT
            )
        """)
        
        # Create meta table for storing metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_draws_date ON draws(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_draws_numbers ON draws(n1, n2, n3, n4, n5)")
        
        conn.commit()
    
    def init_db(self) -> None:
        """
        Initialize database schema.
        Creates all required tables and indexes.
        """
        with self._connect() as conn:
            # Tables are created in _connect(), so we just need to set initial metadata
            cursor = conn.cursor()
            
            # Set database version and creation timestamp
            cursor.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                ("db_version", "1.0")
            )
            cursor.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                ("created_at", pd.Timestamp.now().isoformat())
            )
            
            conn.commit()
    
    def upsert_draws(self, draws: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Insert or update draw records.
        
        Args:
            draws: List of draw dictionaries with required fields
            
        Returns:
            Dict with counts: {"inserted": int, "updated": int, "errors": int}
        """
        if not draws:
            return {"inserted": 0, "updated": 0, "errors": 0}
        
        inserted = 0
        updated = 0
        errors = 0
        
        with self._connect() as conn:
            cursor = conn.cursor()
            
            for draw in draws:
                try:
                    # Check if draw already exists
                    cursor.execute(
                        "SELECT draw_id FROM draws WHERE draw_id = ?",
                        (draw["draw_id"],)
                    )
                    exists = cursor.fetchone() is not None
                    
                    # Prepare data with proper JSON serialization
                    # Ensure draw_date is in string format
                    draw_date = draw["draw_date"]
                    if hasattr(draw_date, 'strftime'):
                        draw_date = draw_date.strftime('%Y-%m-%d')
                    elif isinstance(draw_date, str) and len(draw_date) > 10:
                        # Handle datetime strings that might include time
                        draw_date = draw_date[:10]
                    
                    draw_data = {
                        "draw_id": draw["draw_id"],
                        "draw_date": draw_date,
                        "n1": draw["n1"],
                        "n2": draw["n2"], 
                        "n3": draw["n3"],
                        "n4": draw["n4"],
                        "n5": draw["n5"],
                        "s1": draw["s1"],
                        "s2": draw["s2"],
                        "jackpot": draw.get("jackpot"),
                        "prize_table_json": json.dumps(draw.get("prize_table")) if draw.get("prize_table") else None,
                        "raw_html": draw.get("raw_html")
                    }
                    
                    # Insert or replace record
                    cursor.execute("""
                        INSERT OR REPLACE INTO draws 
                        (draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2, 
                         jackpot, prize_table_json, raw_html)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(draw_data.values()))
                    
                    if exists:
                        updated += 1
                    else:
                        inserted += 1
                        
                except Exception as e:
                    errors += 1
                    print(f"Error processing draw {draw.get('draw_id', 'unknown')}: {e}")
            
            conn.commit()
        
        return {"inserted": inserted, "updated": updated, "errors": errors}
    
    def all_draws_df(self) -> pd.DataFrame:
        """
        Get all draws as a pandas DataFrame ordered by draw_date ASC.
        
        Returns:
            pd.DataFrame: All draw data with parsed prize_table_json
        """
        with self._connect() as conn:
            # Query all draws ordered by date
            df = pd.read_sql_query("""
                SELECT draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2,
                       jackpot, prize_table_json, raw_html
                FROM draws 
                ORDER BY draw_date ASC
            """, conn)
            
            if df.empty:
                return df
            
            # Parse prize_table_json back to Python objects
            df["prize_table"] = df["prize_table_json"].apply(
                lambda x: json.loads(x) if x else None
            )
            
            # Convert draw_date to datetime for better handling
            # Handle both string and datetime formats with explicit format
            df["draw_date"] = pd.to_datetime(df["draw_date"], format='%Y-%m-%d', errors='coerce')
            
            # Remove rows with invalid dates
            df = df.dropna(subset=['draw_date'])
            
            return df
    
    def latest_draw_date(self) -> Optional[str]:
        """
        Get the date of the most recent draw.
        
        Returns:
            Optional[str]: Latest draw date in ISO format, or None if no draws
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT draw_date 
                FROM draws 
                ORDER BY draw_date DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            return result["draw_date"] if result else None
    
    def get_draw_by_id(self, draw_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific draw by ID.
        
        Args:
            draw_id: The draw identifier
            
        Returns:
            Optional[Dict]: Draw data or None if not found
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2,
                       jackpot, prize_table_json, raw_html
                FROM draws 
                WHERE draw_id = ?
            """, (draw_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Convert to dict and parse JSON
            draw = dict(result)
            if draw["prize_table_json"]:
                draw["prize_table"] = json.loads(draw["prize_table_json"])
            else:
                draw["prize_table"] = None
            
            return draw
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict with database stats
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # Count total draws
            cursor.execute("SELECT COUNT(*) as count FROM draws")
            total_draws = cursor.fetchone()["count"]
            
            # Get date range
            cursor.execute("""
                SELECT MIN(draw_date) as earliest, MAX(draw_date) as latest 
                FROM draws
            """)
            date_range = cursor.fetchone()
            
            # Get database file size
            db_size = self._db_path.stat().st_size if self._db_path.exists() else 0
            
            return {
                "total_draws": total_draws,
                "earliest_draw": date_range["earliest"],
                "latest_draw": date_range["latest"],
                "db_file_size_bytes": db_size,
                "db_path": str(self._db_path)
            }


# Convenience functions for easy access
def get_repository() -> EuromillionsRepository:
    """Get a repository instance."""
    return EuromillionsRepository()


def init_database() -> None:
    """Initialize the database with required schema."""
    repo = get_repository()
    repo.init_db()
    print(f"✅ Database initialized at: {repo._db_path}")
