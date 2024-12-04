import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import pandas as pd
import os

def create_visualizations():
    """
    Creates distinct visualizations for Last.fm, Google Trends, and Trimble data
    """
    # Connect to database
    conn = sqlite3.connect('database/music_trends.db')
    
    # Create visualization directory if it doesn't exist
    viz_dir = 'visualization'
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    # 1. Last.fm Visualization: Artist Popularity
    artist_stats = pd.read_sql_query('''
        SELECT name, listeners, playcount 
        FROM artists
        ORDER BY listeners DESC
        LIMIT 10
    ''', conn)
    
    plt.figure(figsize=(12, 6))
    plt.subplot(111)
    bars = plt.bar(artist_stats['name'], artist_stats['listeners'], color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 10 Artists by Listeners (Last.fm)')
    plt.xlabel('Artist')
    plt.ylabel('Number of Listeners')
    
    # Add playcount as text on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/lastfm_top_artists.png')
    plt.close()
    
    # 2. Google Trends Visualization: Trend Comparison
    trends_data = pd.read_sql_query('''
        SELECT keyword, date, interest
        FROM trends
        ORDER BY date
    ''', conn)
    
    if not trends_data.empty:
        plt.figure(figsize=(12, 6))
        for keyword in trends_data['keyword'].unique():
            keyword_data = trends_data[trends_data['keyword'] == keyword]
            plt.plot(pd.to_datetime(keyword_data['date']), 
                    keyword_data['interest'], 
                    label=keyword, 
                    marker='o', 
                    markersize=4)
        
        plt.title('Music-Related Search Trends Over Time (Google Trends)')
        plt.xlabel('Date')
        plt.ylabel('Search Interest')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{viz_dir}/google_trends_comparison.png', bbox_inches='tight')
        plt.close()
    
    # 3. Trimble Visualization: Venue Statistics by Location
    trimble_data = pd.read_sql_query('''
        SELECT location,
               COUNT(*) as venue_count,
               AVG(capacity) as avg_capacity,
               AVG(event_count) as avg_events
        FROM trimble_data
        GROUP BY location
        ORDER BY avg_capacity DESC
    ''', conn)
    
    plt.figure(figsize=(12, 6))
    x = range(len(trimble_data))
    width = 0.35
    
    ax = plt.gca()
    capacity_bars = ax.bar([i - width/2 for i in x], 
                          trimble_data['avg_capacity'], 
                          width, 
                          label='Average Capacity',
                          color='skyblue')
    
    ax2 = ax.twinx()
    event_bars = ax2.bar([i + width/2 for i in x], 
                        trimble_data['avg_events'], 
                        width, 
                        label='Average Events',
                        color='lightcoral')
    
    ax.set_xticks(x)
    ax.set_xticklabels(trimble_data['location'], rotation=45, ha='right')
    
    ax.set_ylabel('Average Venue Capacity')
    ax2.set_ylabel('Average Events per Venue')
    
    plt.title('Venue Statistics by Location (Trimble)')
    
    # Add both legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/trimble_venue_stats.png')
    plt.close()
    
    conn.close()
    print("✓ Successfully created visualizations for all three APIs")