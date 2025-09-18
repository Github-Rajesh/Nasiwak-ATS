#!/usr/bin/env python3
"""
Migration script to add AI analysis fields to the candidates table
Run this script to update the database schema
"""

import sqlite3
import os
import sys
from pathlib import Path

def migrate_database():
    """Add AI analysis fields to candidates table"""
    
    # Find the database file
    db_paths = [
        'instance/rsart.db',
        'instance/rsart_prod.db',
        'rsart.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Error: No database file found")
        return False
    
    print(f"Found database at: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add AI analysis columns if they don't exist
        if 'ai_analysis' not in columns:
            print("Adding ai_analysis column...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN ai_analysis TEXT")
        
        if 'ai_strengths' not in columns:
            print("Adding ai_strengths column...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN ai_strengths TEXT")
        
        if 'ai_concerns' not in columns:
            print("Adding ai_concerns column...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN ai_concerns TEXT")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting database migration...")
    success = migrate_database()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
