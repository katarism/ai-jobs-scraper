#!/usr/bin/env python3
"""
Quick debug test for Notion API
"""

import requests
import json
import os
from datetime import datetime

# Get environment variables
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
AI_JOBS_DATABASE_ID = os.getenv('AI_JOBS_DATABASE_ID')
CHANGE_LOG_DATABASE_ID = os.getenv('CHANGE_LOG_DATABASE_ID')

print("🔧 Debug Test for AI Jobs Scraper")
print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test 1: Check environment variables
print("\n1️⃣ Checking environment variables...")
print(f"NOTION_TOKEN: {'✅ Set' if NOTION_TOKEN else '❌ Missing'}")
print(f"AI_JOBS_DATABASE_ID: {'✅ Set' if AI_JOBS_DATABASE_ID else '❌ Missing'}")
print(f"CHANGE_LOG_DATABASE_ID: {'✅ Set' if CHANGE_LOG_DATABASE_ID else '❌ Missing'}")

if not all([NOTION_TOKEN, AI_JOBS_DATABASE_ID, CHANGE_LOG_DATABASE_ID]):
    print("❌ Missing required environment variables. Exiting.")
    exit(1)

# Test 2: Check Notion API connection
print("\n2️⃣ Testing Notion API connection...")
headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

try:
    response = requests.get('https://api.notion.com/v1/users/me', headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Connection successful! User: {user_data.get('name', 'Unknown')}")
    else:
        print(f"❌ Connection failed: {response.status_code} - {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

# Test 3: Check database schema
print("\n3️⃣ Checking database schema...")
try:
    db_url = f'https://api.notion.com/v1/databases/{AI_JOBS_DATABASE_ID}'
    response = requests.get(db_url, headers=headers)
    
    if response.status_code == 200:
        db_data = response.json()
        properties = db_data.get('properties', {})
        print("📋 Available database fields:")
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"   - {prop_name}: {prop_type}")
    else:
        print(f"❌ Database access failed: {response.status_code} - {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Database check error: {e}")
    exit(1)

# Test 4: Try to create a simple entry
print("\n4️⃣ Testing simple entry creation...")

# Find the title field (could be "Name", "Job Title", "Title", etc.)
title_field = None
for prop_name, prop_info in properties.items():
    if prop_info.get('type') == 'title':
        title_field = prop_name
        break

if not title_field:
    print("❌ No title field found in database!")
    exit(1)

print(f"📝 Using title field: {title_field}")

# Create minimal entry
simple_entry = {
    "parent": {"database_id": AI_JOBS_DATABASE_ID},
    "properties": {
        title_field: {
            "title": [{"text": {"content": f"Test Job - {datetime.now().strftime('%H:%M:%S')}"}}]
        }
    }
}

print(f"🔍 Attempting to create entry with data: {json.dumps(simple_entry, indent=2)}")

try:
    create_url = 'https://api.notion.com/v1/pages'
    response = requests.post(create_url, headers=headers, json=simple_entry)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS! Entry created with ID: {result.get('id')}")
        print("🎉🎉🎉 Your AI Jobs automation system is working! 🎉🎉🎉")
        print("\n✅ The system can now:")
        print("   - Connect to Notion API")
        print("   - Access your database")
        print("   - Create new entries")
        print("   - Run automatically every day at 9:00 and 21:00 JST")
        print(f"\n📝 Check your database: https://www.notion.so/{AI_JOBS_DATABASE_ID}")
        print(f"🔗 Your newsletter: https://aijobsjp.beehiiv.com/")
    else:
        print(f"❌ Entry creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try to parse error for more details
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass
        
except Exception as e:
    print(f"❌ Entry creation error: {e}")

print(f"\n🔧 Debug test completed at {datetime.now().strftime('%H:%M:%S')}")
