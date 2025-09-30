#!/usr/bin/env python3
"""
Database manager for gossip audio files
Handles storage and retrieval of gossip recordings
"""

import sqlite3
import os
import random
import datetime
from typing import Optional, List, Dict

class GossipDatabase:
    def __init__(self, db_path: str = "gossip.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the gossip database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create gossip table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gossip (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                original_text TEXT,
                gossip_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration_seconds REAL,
                file_size_bytes INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def add_gossip(self, file_path: str, original_text: str = "", gossip_text: str = "") -> int:
        """
        Add a new gossip entry to the database
        Returns the ID of the inserted record
        """
        try:
            # Get file metadata
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO gossip (file_path, original_text, gossip_text, file_size_bytes)
                VALUES (?, ?, ?, ?)
            ''', (file_path, original_text, gossip_text, file_size))
            
            gossip_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Added gossip to database: ID {gossip_id}, file: {file_path}")
            return gossip_id
            
        except Exception as e:
            print(f"Error adding gossip to database: {e}")
            return -1
    
    def get_random_gossip(self) -> Optional[Dict]:
        """
        Get a random active gossip entry from the database
        Returns None if no gossip available
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active gossip entries
            cursor.execute('''
                SELECT id, file_path, gossip_text, timestamp
                FROM gossip 
                WHERE is_active = 1 AND file_path IS NOT NULL
                ORDER BY RANDOM()
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'file_path': result[1],
                    'gossip_text': result[2],
                    'timestamp': result[3]
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error getting random gossip: {e}")
            return None
    
    def get_all_gossip(self) -> List[Dict]:
        """Get all active gossip entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, file_path, original_text, gossip_text, timestamp, duration_seconds
                FROM gossip 
                WHERE is_active = 1
                ORDER BY timestamp DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'file_path': row[1],
                    'original_text': row[2],
                    'gossip_text': row[3],
                    'timestamp': row[4],
                    'duration_seconds': row[5]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"Error getting all gossip: {e}")
            return []
    
    def deactivate_gossip(self, gossip_id: int) -> bool:
        """Deactivate a gossip entry (soft delete)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE gossip SET is_active = 0 WHERE id = ?
            ''', (gossip_id,))
            
            conn.commit()
            conn.close()
            
            print(f"Deactivated gossip ID: {gossip_id}")
            return True
            
        except Exception as e:
            print(f"Error deactivating gossip: {e}")
            return False
    
    def get_gossip_count(self) -> int:
        """Get the count of active gossip entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM gossip WHERE is_active = 1')
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"Error getting gossip count: {e}")
            return 0
    
    def cleanup_missing_files(self):
        """Remove database entries for files that no longer exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, file_path FROM gossip WHERE is_active = 1')
            entries = cursor.fetchall()
            
            removed_count = 0
            for entry_id, file_path in entries:
                if not os.path.exists(file_path):
                    cursor.execute('UPDATE gossip SET is_active = 0 WHERE id = ?', (entry_id,))
                    removed_count += 1
            
            conn.commit()
            conn.close()
            
            if removed_count > 0:
                print(f"Cleaned up {removed_count} missing file entries")
                
        except Exception as e:
            print(f"Error cleaning up database: {e}")

# Test function
def test_database():
    """Test the database functionality"""
    db = GossipDatabase("test_gossip.db")
    
    # Add some test entries
    db.add_gossip("test1.mp3", "Original text 1", "Gossip text 1")
    db.add_gossip("test2.mp3", "Original text 2", "Gossip text 2")
    
    # Get random gossip
    random_gossip = db.get_random_gossip()
    print(f"Random gossip: {random_gossip}")
    
    # Get count
    count = db.get_gossip_count()
    print(f"Total gossip count: {count}")
    
    # Get all gossip
    all_gossip = db.get_all_gossip()
    print(f"All gossip: {all_gossip}")

if __name__ == "__main__":
    test_database()