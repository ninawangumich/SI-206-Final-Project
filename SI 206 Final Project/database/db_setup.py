import sqlite3
import os

def setup_database():
    """
    Creates the SQLite database and required tables
    Returns the database connection and cursor
    """
    # Create database directory if it doesn't exist
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('database/music_trends.db')
    cur = conn.cursor()
    
    # Drop existing tables to ensure clean schema
    cur.executescript('''
        DROP TABLE IF EXISTS songs;
        DROP TABLE IF EXISTS artists;
        DROP TABLE IF EXISTS trends;
        DROP TABLE IF EXISTS trimble_data;
    ''')
    
    # Create tables with correct schema
    cur.executescript('''
        -- Last.fm artists table
        CREATE TABLE artists (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            playcount INTEGER,
            listeners INTEGER,
            genre TEXT
        );
        
        -- Last.fm songs table (related to artists)
        CREATE TABLE songs (
            track_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            title TEXT,
            playcount INTEGER,
            listeners INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artists(artist_id)
        );
        
        -- Google Trends data
        CREATE TABLE trends (
            trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            date TEXT,
            interest INTEGER,
            UNIQUE(keyword, date)
        );
        
        -- Trimble venue data
        CREATE TABLE trimble_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            venue_name TEXT UNIQUE,
            capacity INTEGER,
            event_count INTEGER,
            last_event_date TEXT
        );
    ''')
    
    conn.commit()
    print("✓ Database schema created successfully")
    return conn, cur

if __name__ == "__main__":
    conn, cur = setup_database()
    conn.close() 