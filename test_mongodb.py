#!/usr/bin/env python3
"""
Test MongoDB connection and operations
"""
import os
from dotenv import load_dotenv
from mongodb_helper import get_db_helper
import json

# Load environment variables
load_dotenv()

def test_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    try:
        db_helper = get_db_helper()
        print("✓ Successfully connected to MongoDB!")
        return db_helper
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        return None

def test_upsert(db_helper):
    """Test upsert operation"""
    print("\n🔍 Testing upsert operation...")
    
    test_data = {
        "invoice": {
            "number": "TEST-001",
            "date_of_issuing": "2025-11-10",
            "deal_number": "TEST123456"
        },
        "issued_to": {
            "name": "Test Customer",
            "address": "123 Test St",
            "trn": "123456789",
            "email": "test@example.com"
        },
        "terms": {
            "payment_terms": "Net 30",
            "amount_paid": "1000.00"
        },
        "items": [
            {
                "description": "Test Item",
                "sub_description": "Test Description",
                "quantity": 1.0,
                "uom": "Pcs",
                "price_incl_vat_aed": 1050.00,
                "discount_pct": 0,
                "vat_pct": 5
            }
        ],
        "amount_in_words": "One thousand AED ONLY"
    }
    
    try:
        # First upsert - should create
        is_new, doc_id = db_helper.upsert_invoice("TEST123456", test_data)
        print(f"✓ First upsert: {'Created' if is_new else 'Updated'} (ID: {doc_id})")
        
        # Modify data
        test_data["items"][0]["quantity"] = 2.0
        
        # Second upsert - should update
        is_new, doc_id = db_helper.upsert_invoice("TEST123456", test_data)
        print(f"✓ Second upsert: {'Created' if is_new else 'Updated'} (ID: {doc_id})")
        
        # Verify the update
        record = db_helper.find_by_deal_number("TEST123456")
        if record:
            print(f"✓ Retrieved record:")
            print(f"  - Deal Number: {record['invoice']['deal_number']}")
            print(f"  - Invoice Number: {record['invoice']['number']}")
            print(f"  - Quantity: {record['items'][0]['quantity']}")
            print(f"  - Created At: {record['created_at']}")
            print(f"  - Updated At: {record['updated_at']}")
        
        return True
    except Exception as e:
        print(f"❌ Error during upsert test: {str(e)}")
        return False

def test_find(db_helper):
    """Test find operation"""
    print("\n🔍 Testing find operation...")
    
    try:
        # Try to find existing record
        record = db_helper.find_by_deal_number("TEST123456")
        if record:
            print("✓ Found existing test record")
        else:
            print("ℹ No existing test record found")
        
        # Try to find non-existent record
        record = db_helper.find_by_deal_number("NONEXISTENT")
        if not record:
            print("✓ Correctly returned None for non-existent record")
        
        return True
    except Exception as e:
        print(f"❌ Error during find test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MongoDB Integration Test")
    print("=" * 60)
    
    # Test connection
    db_helper = test_connection()
    if not db_helper:
        print("\n❌ Cannot proceed without database connection")
        return
    
    # Test find
    test_find(db_helper)
    
    # Test upsert
    test_upsert(db_helper)
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)
    print("\nNote: Test data with deal_number='TEST123456' was created.")
    print("You can verify it in MongoDB using:")
    print('  db.proforma_invoices.find({"deal_number": "TEST123456"})')

if __name__ == "__main__":
    main()

