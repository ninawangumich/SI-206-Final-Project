import os
import sqlite3

def verify_project():
    """
    Verifies all components of the project are working
    """
    # Check directory structure
    required_dirs = ['database', 'visualization']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory '{dir_name}' exists")
        else:
            print(f"✗ Directory '{dir_name}' missing")
    
    # Check database
    try:
        conn = sqlite3.connect('database/music_trends.db')
        cur = conn.cursor()
        
        # Check tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print("\nDatabase tables:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cur.fetchone()[0]
            print(f"✓ Table '{table[0]}' exists with {count} rows")
        
        conn.close()
    except Exception as e:
        print(f"✗ Database error: {e}")
    
    # Check output files
    output_files = [
        'visualization/top_artists_listeners.png',
        'visualization/top_songs_playcount.png',
        'visualization/artist_popularity_scatter.png'
    ]
    
    print("\nOutput files:")
    for file_path in output_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ File '{file_path}' exists ({size} bytes)")
        else:
            dir_name = os.path.dirname(file_path)
            if not os.path.exists(dir_name):
                print(f"✗ File '{file_path}' missing - directory '{dir_name}' does not exist")
            else:
                print(f"✗ File '{file_path}' missing - directory exists but file not found")

if __name__ == "__main__":
    verify_project() 