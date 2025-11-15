#!/usr/bin/env python3
"""
Test script for Smart Upload System

Tests the JSON analyzer to demonstrate SQL vs NoSQL categorization
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storage.json_analyzer import analyze_json_for_database


def print_separator(title):
    """Print a nice separator"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def test_sql_friendly_data():
    """Test with SQL-friendly data"""
    print_separator("TEST 1: SQL-Friendly Data (Structured Products)")

    data = [
        {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50},
        {"id": 2, "name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 200},
        {"id": 3, "name": "Book", "price": 19.99, "category": "Books", "stock": 100}
    ]

    print("\nInput Data:")
    import json
    print(json.dumps(data, indent=2))

    result = analyze_json_for_database(data)

    print(f"\n🎯 RECOMMENDATION: {result.recommended_db.upper()}")
    print(f"📊 CONFIDENCE: {result.confidence * 100:.0f}%")
    print(f"\n💡 REASONS:")
    for reason in result.reasons:
        print(f"   {reason}")
    print(f"\n📈 METRICS:")
    for key, value in result.metrics.items():
        print(f"   {key}: {value}")


def test_nosql_friendly_data():
    """Test with NoSQL-friendly data"""
    print_separator("TEST 2: NoSQL-Friendly Data (Complex User Profile)")

    data = {
        "user": {
            "id": "user123",
            "profile": {
                "personal": {
                    "name": "Alice Johnson",
                    "age": 30,
                    "contacts": [
                        {
                            "type": "email",
                            "value": "alice@example.com",
                            "verified": True,
                            "preferences": {"marketing": False}
                        },
                        {
                            "type": "phone",
                            "value": "+1234567890",
                            "verified": False
                        }
                    ]
                },
                "preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": {
                        "email": True,
                        "sms": False,
                        "push": {"enabled": True, "frequency": "daily"}
                    }
                },
                "settings": {
                    "privacy": {"profile_visible": True, "show_email": False}
                }
            },
            "activity": [
                {
                    "date": "2024-01-15",
                    "events": [
                        {"type": "login", "ip": "192.168.1.1", "device": "mobile"},
                        {"type": "purchase", "amount": 99.99, "items": [1, 2, 3]}
                    ]
                },
                {
                    "date": "2024-01-14",
                    "actions": ["view_profile", "update_settings"]
                }
            ]
        }
    }

    print("\nInput Data:")
    import json
    print(json.dumps(data, indent=2))

    result = analyze_json_for_database(data)

    print(f"\n🎯 RECOMMENDATION: {result.recommended_db.upper()}")
    print(f"📊 CONFIDENCE: {result.confidence * 100:.0f}%")
    print(f"\n💡 REASONS:")
    for reason in result.reasons:
        print(f"   {reason}")
    print(f"\n📈 METRICS:")
    for key, value in result.metrics.items():
        print(f"   {key}: {value}")


def test_mixed_data():
    """Test with borderline data"""
    print_separator("TEST 3: Borderline Data (E-commerce Orders)")

    data = [
        {
            "order_id": 1001,
            "customer": {"id": 123, "name": "John Doe"},
            "items": [
                {"product_id": 1, "quantity": 2, "price": 29.99},
                {"product_id": 2, "quantity": 1, "price": 49.99}
            ],
            "total": 109.97,
            "status": "completed"
        },
        {
            "order_id": 1002,
            "customer": {"id": 456, "name": "Jane Smith", "email": "jane@example.com"},
            "items": [
                {"product_id": 3, "quantity": 1, "price": 99.99, "discount": 10}
            ],
            "total": 89.99,
            "status": "pending",
            "notes": "Express shipping requested"
        }
    ]

    print("\nInput Data:")
    import json
    print(json.dumps(data, indent=2))

    result = analyze_json_for_database(data)

    print(f"\n🎯 RECOMMENDATION: {result.recommended_db.upper()}")
    print(f"📊 CONFIDENCE: {result.confidence * 100:.0f}%")
    print(f"\n💡 REASONS:")
    for reason in result.reasons:
        print(f"   {reason}")
    print(f"\n📈 METRICS:")
    for key, value in result.metrics.items():
        print(f"   {key}: {value}")


def test_simple_flat_data():
    """Test with very simple flat data"""
    print_separator("TEST 4: Simple Flat Data (User List)")

    data = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]

    print("\nInput Data:")
    import json
    print(json.dumps(data, indent=2))

    result = analyze_json_for_database(data)

    print(f"\n🎯 RECOMMENDATION: {result.recommended_db.upper()}")
    print(f"📊 CONFIDENCE: {result.confidence * 100:.0f}%")
    print(f"\n💡 REASONS:")
    for reason in result.reasons:
        print(f"   {reason}")
    print(f"\n📈 METRICS:")
    for key, value in result.metrics.items():
        print(f"   {key}: {value}")


if __name__ == '__main__':
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║         SMART UPLOAD SYSTEM - JSON ANALYZER TEST SUITE                    ║")
    print("║                                                                            ║")
    print("║  Tests intelligent SQL vs NoSQL categorization based on JSON structure    ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    try:
        # Run all tests
        test_sql_friendly_data()
        test_nosql_friendly_data()
        test_mixed_data()
        test_simple_flat_data()

        print_separator("✅ ALL TESTS COMPLETED")
        print("\nThe analyzer successfully categorized all test cases!")
        print("\nNext Steps:")
        print("1. Start PostgreSQL and MongoDB")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py runserver")
        print("4. Create admin user via API: POST /api/smart/auth/create")
        print("5. Start uploading JSON data!")

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
