from data_collection.api_collector import APICollector
from visualization.visualize import create_visualizations
from processing.calculations import calculate_statistics
from database.db_setup import setup_database
from datetime import datetime, timedelta
import time

def collect_data_in_batches():
    """Collect data from all APIs in batches of 25"""
    collector = APICollector()
    
    # Last.fm: Collect 4 pages of 25 artists each
    print("1. Collecting Last.fm data...")
    for page in range(1, 5):
        print(f"\nCollecting page {page} of artists...")
        collector.collect_lastfm_data(page=page, limit=25)
        time.sleep(2)  # Small delay between requests
    
    # Google Trends: Collect 4 batches of 25 days each
    print("\n2. Collecting Google Trends data...")
    start_date = datetime.now() - timedelta(days=100)
    for i in range(4):
        batch_start = start_date + timedelta(days=i*25)
        print(f"\nCollecting trends from {batch_start.strftime('%Y-%m-%d')}...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                collector.collect_trends_data(start_date=batch_start)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 60 * (attempt + 1)  # Exponential backoff
                    print(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to collect trends after {max_retries} attempts")
    
    # Trimble: Collect 4 batches of 25 venues each
    print("\n3. Collecting Trimble data...")
    for offset in range(0, 100, 25):
        print(f"\nCollecting venues {offset+1} to {offset+25}...")
        collector.collect_trimble_data(offset=offset, limit=25)

def main():
    # 0. Set up database schema
    print("PART 0: Database Setup")
    print("=====================")
    conn, cur = setup_database()
    conn.close()
    
    # 1. Collect all data in batches
    print("\nPART 1: Data Collection")
    print("======================")
    collect_data_in_batches()
    
    # 2. Process and analyze the data
    print("\nPART 2: Data Processing")
    print("======================")
    results = calculate_statistics()
    
    # 3. Create visualizations
    print("\nPART 3: Data Visualization")
    print("=========================")
    create_visualizations()
    
    print("\nProject execution completed!")

if __name__ == "__main__":
    main() 