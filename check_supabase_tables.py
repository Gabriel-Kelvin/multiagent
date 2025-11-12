#!/usr/bin/env python3
"""Check tables in the Supabase database you provided"""
import psycopg2
import psycopg2.extras
import sys

# Get DSN from command line
if len(sys.argv) > 1:
    DSN = sys.argv[1]
else:
    print("Usage: python check_supabase_tables.py <your_dsn>")
    print("Example: python check_supabase_tables.py 'postgresql://user:pass@host:port/db?sslmode=require'")
    sys.exit(1)

print("=" * 70)
print("Checking Tables in Your Supabase Database")
print("=" * 70)
print(f"\nDSN: {DSN[:50]}...")

try:
    conn = psycopg2.connect(DSN, cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()
    
    # Get all tables in public schema
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    
    print("\nAvailable tables in 'public' schema:")
    print("-" * 70)
    if tables:
        for row in tables:
            table_name = row['table_name']
            print(f"  - {table_name}")
            
        # Check if employee_survey_data exists
        if any(row['table_name'] == 'employee_survey_data' for row in tables):
            print("\n[OK] Table 'employee_survey_data' EXISTS!")
            
            # Get column info
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema='public' 
                AND table_name='employee_survey_data'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"    - {col['column_name']} ({col['data_type']})")
                
            # Sample data
            cur.execute("SELECT * FROM employee_survey_data LIMIT 3")
            rows = cur.fetchall()
            print(f"\nSample data: {len(rows)} row(s)")
            if rows:
                print(f"  First row: {dict(rows[0])}")
        else:
            print("\n[ERROR] Table 'employee_survey_data' DOES NOT EXIST!")
            print("\nYou need to:")
            print("  1. Create the table in your Supabase database")
            print("  2. Or use one of the existing tables above")
    else:
        print("  No tables found in public schema")
        
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPossible issues:")
    print("  - Incorrect credentials")
    print("  - Network/firewall blocking connection")
    print("  - Database doesn't exist")

print("\n" + "=" * 70)

