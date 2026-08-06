import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_supplier():
    print("\n" + "="*50)
    print("TEST: Create Supplier")
    print("="*50)
    
    supplier = {
        "name": "Tech Distributors Ltd",
        "contact_person": "John Mwangi",
        "email": "john@techdistributors.co.ke",
        "phone": "0722123456",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Supplier created with ID: {data['id']}")
        print(f"   Name: {data['name']}")
        print(f"   Email: {data['email']}")
        return data
    else:
        print(f"❌ Failed: {response.json()}")
        return None

def test_invalid_supplier():
    print("\n" + "="*50)
    print("TEST: Invalid Supplier Validation")
    print("="*50)
    
    supplier = {
        "name": "A",
        "contact_person": "J",
        "email": "invalid-email",
        "phone": "123"
    }
    
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier)
    if response.status_code == 422:
        print("✅ Validation caught errors!")
        for error in response.json().get('errors', []):
            print(f"   - {error['field']}: {error['message']}")
    else:
        print(f"❌ Expected 422, got {response.status_code}")

def test_bulk_price_update():
    print("\n" + "="*50)
    print("TEST: Bulk Price Update")
    print("="*50)
    
    # First create a product
    product = {
        "name": "Test Product",
        "description": "Test product for bulk update",
        "brand": "HP",
        "category": "Laptops",
        "price": 50000,
        "stock": 10,
        "warranty_months": 12,
        "sku": "LAP-HP-9999"
    }
    requests.post(f"{BASE_URL}/products/", json=product)
    
    # Apply 10% discount
    update = {
        "category": "Laptops",
        "discount_percent": 10
    }
    
    response = requests.patch(f"{BASE_URL}/products/bulk-update/", json=update)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Bulk update completed")
        print(f"   Category: {data['category']}")
        print(f"   Updated: {data['updated_count']} products")
        print(f"   Skipped: {data['skipped_count']} products")
    else:
        print(f"❌ Failed: {response.json()}")

def test_stock_adjustment():
    print("\n" + "="*50)
    print("TEST: Stock Adjustment")
    print("="*50)
    
    adjustments = [
        {"product_id": 1, "quantity_to_add": 50},
        {"product_id": 999, "quantity_to_add": 10}  # This should fail
    ]
    
    response = requests.patch(f"{BASE_URL}/products/adjust-stock/", json=adjustments)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stock adjustment completed")
        print(f"   Successful: {data['successful']}")
        print(f"   Failed: {data['failed']}")
        for success in data['details']['success']:
            print(f"   ✅ {success['name']}: {success['old_stock']} → {success['new_stock']}")
        for failure in data['details']['failures']:
            print(f"   ❌ Product {failure['product_id']}: {failure['reason']}")
    else:
        print(f"❌ Failed: {response.json()}")

def main():
    print("\n" + "="*50)
    print("TECHVAULT API - COMPLETE TEST SUITE")
    print("LUCY WAMBUI KIMANI - C027-01-0890/2024")
    print("="*50)
    
    try:
        test_create_supplier()
        test_invalid_supplier()
        test_bulk_price_update()
        test_stock_adjustment()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()