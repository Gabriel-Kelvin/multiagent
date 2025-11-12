#!/usr/bin/env python3
"""Check available tables in database"""
from app.config import settings
from utils import db_utils

try:
    conn = db_utils.connect(settings)
    cur = conn.cursor()
    
    # Query to get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    
    print("\nAvailable tables in your database:")
    print("=" * 50)
    if tables:
        for row in tables:
            table_name = row[0] if isinstance(row, tuple) else row.get('table_name')
            print(f"  - {table_name}")
    else:
        print("  No tables found in public schema")
    
    print("\nYour current DATA_TABLE setting:")
    print(f"  DATA_TABLE={settings.DATA_TABLE}")
    
    conn.close()
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure your .env has:")
    print("  DATA_DB_TYPE=postgres")
    print("  DATA_DSN=<your_supabase_connection_string>")

