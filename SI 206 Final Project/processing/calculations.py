import sqlite3
import pandas as pd
from datetime import datetime

def calculate_statistics():
    """
    Performs calculations on the collected data from all three APIs
    Writes results to a file
    """
    conn = sqlite3.connect('database/music_trends.db')
    
    # 1. Calculate average listeners per artist and their total song plays
    artist_stats = pd.read_sql_query('''
        SELECT a.name, a.listeners, 
               COUNT(s.track_id) as total_songs,
               SUM(s.playcount) as total_song_plays
        FROM artists a
        LEFT JOIN songs s ON a.artist_id = s.artist_id
        GROUP BY a.artist_id
        ORDER BY a.listeners DESC
    ''', conn)
    
    # 2. Calculate average interest over time for each trend keyword
    trend_stats = pd.read_sql_query('''
        SELECT keyword,
               AVG(interest) as avg_interest,
               MAX(interest) as peak_interest,
               COUNT(*) as data_points
        FROM trends
        GROUP BY keyword
        ORDER BY avg_interest DESC
    ''', conn)
    
    # 3. Calculate venue statistics by city
    venue_stats = pd.read_sql_query('''
        SELECT location,
               COUNT(*) as venue_count,
               AVG(capacity) as avg_capacity,
               AVG(event_count) as avg_events,
               SUM(capacity * event_count) as total_potential_attendance
        FROM trimble_data
        GROUP BY location
        ORDER BY total_potential_attendance DESC
    ''', conn)
    
    # Write results to file
    with open('processing/music_analysis.txt', 'w') as f:
        f.write("Music Industry Data Analysis\n")
        f.write("==========================\n\n")
        
        f.write("1. Artist Statistics\n")
        f.write("-----------------\n")
        f.write("Average listeners per artist: {:,.0f}\n".format(artist_stats['listeners'].mean()))
        f.write("Total songs analyzed: {:,}\n".format(artist_stats['total_songs'].sum()))
        f.write("\nTop 5 Artists by Listeners:\n")
        f.write(artist_stats.head().to_string())
        f.write("\n\n")
        
        f.write("2. Music Trend Analysis\n")
        f.write("--------------------\n")
        f.write("Trend keyword performance:\n")
        f.write(trend_stats.to_string())
        f.write("\n\n")
        
        f.write("3. Venue Analysis by City\n")
        f.write("----------------------\n")
        f.write("Total venues analyzed: {:,}\n".format(venue_stats['venue_count'].sum()))
        f.write("Average venue capacity: {:,.0f}\n".format(venue_stats['avg_capacity'].mean()))
        f.write("\nCity Statistics:\n")
        f.write(venue_stats.to_string())
    
    conn.close()
    print("✓ Successfully wrote analysis to processing/music_analysis.txt")
    
    return {
        'artist_stats': artist_stats,
        'trend_stats': trend_stats,
        'venue_stats': venue_stats
    }