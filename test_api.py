import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    print("\n" + "="*50)
    print("TEST: Root Endpoint")
    print("="*50)
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message: {data.get('message')}")
        print(f"   Developer: {data.get('developer')}")
    else:
        print(f"❌ Error: {response.text}")

def test_create_valid_product():
    print("\n" + "="*50)
    print("TEST: Create Valid Product")
    print("="*50)
    product = {
        "name": "HP Laptop ProBook 450",
        "description": "Business laptop with 15.6 inch display, 16GB RAM, 512GB SSD",
        "brand": "hp",
        "category": "laptops",
        "price": 85000.50,
        "stock": 25,
        "warranty_months": 12,
        "sku": "LAP-HP-0001"
    }
    print(f"Creating: {product['name']}")
    response = requests.post(f"{BASE_URL}/products/", json=product)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Created with ID: {data['id']}, SKU: {data['sku']}")
    else:
        print(f"❌ Failed: {response.json()}")

def test_invalid_product():
    print("\n" + "="*50)
    print("TEST: Invalid Product Validation")
    print("="*50)
    product = {
        "name": "invalid name",
        "description": "Test",
        "brand": "Unknown",
        "category": "Invalid",
        "price": 50,
        "stock": -5,
        "warranty_months": 48,
        "sku": "INVALID"
    }
    response = requests.post(f"{BASE_URL}/products/", json=product)
    if response.status_code == 422:
        print("✅ Validation caught errors!")
        for error in response.json().get('errors', []):
            print(f"   - {error['field']}: {error['message']}")
    else:
        print(f"❌ Expected 422, got {response.status_code}")

def test_get_products():
    print("\n" + "="*50)
    print("TEST: Get All Products")
    print("="*50)
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products")
        for p in products[:3]:
            print(f"   - {p['name']} (SKU: {p['sku']})")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("TECHVAULT API TEST SUITE")
    print("LUCY WAMBUI KIMANI - C027-01-0890/2024")
    print("="*50)
    try:
        test_root()
        test_create_valid_product()
        test_invalid_product()
        test_get_products()
        print("\n✅ ALL TESTS COMPLETED")
    except Exception as e:
        print(f"\n❌ Error: {e}")