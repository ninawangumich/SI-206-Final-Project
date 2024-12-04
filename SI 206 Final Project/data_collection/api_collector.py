import requests
import sqlite3
import os
from pytrends.request import TrendReq
import time
from datetime import datetime, timedelta

class APICollector:
    def __init__(self):
        self.lastfm_base_url = "http://ws.audioscrobbler.com/2.0/"
        self.lastfm_api_key = "9d3009eae3c41b83bbdc94be7bf023d0"
        self.db_path = 'database/music_trends.db'
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def connect_db(self):
        """Create connection to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        self.connect_db()
        
        # Create tables if they don't exist (removed DROP statements)
        self.cur.execute('''CREATE TABLE IF NOT EXISTS artists
                           (artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE,
                            playcount INTEGER,
                            listeners INTEGER,
                            genre TEXT)''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS songs
                           (track_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            artist_id INTEGER,
                            title TEXT,
                            playcount INTEGER,
                            listeners INTEGER,
                            FOREIGN KEY(artist_id) REFERENCES artists(artist_id))''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS trends
                           (trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            keyword TEXT,
                            date TEXT,
                            interest INTEGER,
                            UNIQUE(keyword, date))''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS trimble_data
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            location TEXT,
                            venue_name TEXT UNIQUE,
                            capacity INTEGER,
                            event_count INTEGER,
                            last_event_date TEXT)''')
        
        self.conn.commit()
        
    def reset_trimble_table(self):
        """Reset the Trimble table schema"""
        self.connect_db()
        self.cur.execute("DROP TABLE IF EXISTS trimble_data")
        self.cur.execute('''CREATE TABLE IF NOT EXISTS trimble_data
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            location TEXT,
                            venue_name TEXT UNIQUE,
                            capacity INTEGER,
                            event_count INTEGER,
                            last_event_date TEXT)''')
        self.conn.commit()
        print("✓ Reset Trimble table schema")
        
    def collect_lastfm_data(self, page=1, limit=25):
        """
        Collect top artists and their songs from Last.fm
        Limits to 25 artists per run and uses pagination
        """
        self.create_tables()
        
        params = {
            'method': 'chart.gettopartists',
            'api_key': self.lastfm_api_key,
            'format': 'json',
            'limit': limit,
            'page': page
        }
        
        try:
            response = requests.get(self.lastfm_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            artists = data['artists']['artist']
            for artist in artists:
                try:
                    self.cur.execute('''INSERT OR IGNORE INTO artists 
                                      (name, playcount, listeners)
                                      VALUES (?, ?, ?)''',
                                   (artist['name'],
                                    int(artist['playcount']),
                                    int(artist['listeners'])))
                    
                    if self.cur.rowcount > 0:  # Only get tracks if artist was inserted
                        track_params = {
                            'method': 'artist.gettoptracks',
                            'artist': artist['name'],
                            'api_key': self.lastfm_api_key,
                            'format': 'json',
                            'limit': 5
                        }
                        
                        track_response = requests.get(self.lastfm_base_url, params=track_params)
                        track_data = track_response.json()
                        
                        self.cur.execute('SELECT artist_id FROM artists WHERE name = ?', (artist['name'],))
                        artist_id = self.cur.fetchone()[0]
                        
                        for track in track_data['toptracks']['track']:
                            self.cur.execute('''INSERT OR IGNORE INTO songs 
                                              (artist_id, title, playcount, listeners)
                                              VALUES (?, ?, ?, ?)''',
                                           (artist_id,
                                            track['name'],
                                            int(track['playcount']),
                                            int(track['listeners'])))
                
                except sqlite3.IntegrityError:
                    continue  # Skip if artist already exists
            
            self.conn.commit()
            print(f"✓ Successfully collected data for page {page}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Last.fm data: {e}")
    
    def collect_trends_data(self, start_date=None):
        """
        Collect Google Trends data for music-related keywords
        Collects data for 25 days at a time
        """
        keywords = ['music', 'concert', 'festival', 'spotify', 'vinyl']
        if start_date is None:
            start_date = datetime.now() - timedelta(days=25)
        end_date = start_date + timedelta(days=25)
        
        timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"
        
        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe)
            trend_data = self.pytrends.interest_over_time()
            
            if not trend_data.empty:
                for date in trend_data.index:
                    for keyword in keywords:
                        interest = trend_data.loc[date, keyword]
                        try:
                            self.cur.execute('''INSERT OR IGNORE INTO trends 
                                              (keyword, date, interest)
                                              VALUES (?, ?, ?)''',
                                           (keyword, date.strftime('%Y-%m-%d'), interest))
                        except sqlite3.IntegrityError:
                            continue
                
                self.conn.commit()
                print(f"✓ Successfully collected Google Trends data from {start_date.strftime('%Y-%m-%d')}")
            else:
                print("No Google Trends data available")
                
        except Exception as e:
            print(f"Error fetching Google Trends data: {e}")
    
    def collect_trimble_data(self, offset=0, limit=25):
        """
        Collect data from Trimble API (simulated)
        Collects 25 venues per run with pagination
        """
        try:
            # Reset table schema if needed
            self.cur.execute("SELECT * FROM trimble_data LIMIT 1")
        except sqlite3.OperationalError:
            self.reset_trimble_table()
            
        try:
            # Simulated data for 100+ venues
            cities = ['New York', 'Los Angeles', 'Chicago', 'Miami', 'Nashville', 
                     'Austin', 'Seattle', 'Boston', 'Denver', 'Portland']
            venue_types = ['Arena', 'Theater', 'Club', 'Stadium', 'Hall']
            
            for i in range(limit):
                idx = offset + i
                if idx >= 100:  # Stop after generating 100 venues
                    break
                    
                city = cities[idx % len(cities)]
                venue_type = venue_types[idx % len(venue_types)]
                venue_name = f"{city} {venue_type} {idx + 1}"
                
                try:
                    self.cur.execute('''INSERT OR IGNORE INTO trimble_data 
                                      (location, venue_name, capacity, event_count, last_event_date)
                                      VALUES (?, ?, ?, ?, ?)''',
                                   (city,
                                    venue_name,
                                    5000 + (hash(venue_name) % 15000),  # Random capacity
                                    10 + (hash(venue_name) % 90),  # Random event count
                                    datetime.now().strftime('%Y-%m-%d')))
                except sqlite3.IntegrityError:
                    continue
            
            self.conn.commit()
            print(f"✓ Successfully collected Trimble data (offset: {offset}, limit: {limit})")
            
        except Exception as e:
            print(f"Error with Trimble data: {e}")
    
    def close_db(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close() 