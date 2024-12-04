from data_collection.api_collector import APICollector
import os

def test_database_creation():
    if os.path.exists('database/music_trends.db'):
        print("✓ Database exists")
    else:
        print("✗ Database not found")

def test_musixmatch_collection():
    collector = APICollector()
    collector.collect_musixmatch_data()
    
    # Check if data was stored
    collector.connect_db()
    collector.cur.execute("SELECT COUNT(*) FROM artists")
    count = collector.cur.fetchone()[0]
    print(f"✓ Found {count} artists in database")
    collector.close_db()

def test_trends_collection():
    collector = APICollector()
    collector.collect_trends_data()
    # Similar checks for Google Trends data

def test_trimble_collection():
    collector = APICollector()
    collector.collect_trimble_data()
    # Similar checks for Trimble data

if __name__ == "__main__":
    test_database_creation()
    test_musixmatch_collection()
    test_trends_collection()
    test_trimble_collection()