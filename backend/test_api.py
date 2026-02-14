"""
Test script for Research Portal API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test API health check"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_financial_extraction(pdf_path):
    """Test financial statement extraction"""
    print("\n=== Testing Financial Extraction ===")
    print(f"Uploading: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/api/extract-financials",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'success' and result.get('file_path'):
        print(f"\nExcel file generated: {result['file_path']}")
        print(f"Download URL: {BASE_URL}/api/download/{result['file_path'].split('/')[-1]}")

def test_earnings_call_summary(pdf_path):
    """Test earnings call summarization"""
    print("\n=== Testing Earnings Call Summary ===")
    print(f"Uploading: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/api/summarize-earnings-call",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'success':
        print("\n=== Summary Details ===")
        print(f"Management Tone: {result.get('management_tone')}")
        print(f"Confidence Level: {result.get('confidence_level')}")
        print(f"\nKey Positives:")
        for item in result.get('key_positives', []):
            print(f"  - {item}")
        print(f"\nKey Concerns:")
        for item in result.get('key_concerns', []):
            print(f"  - {item}")

if __name__ == "__main__":
    # Test health check
    test_health_check()
    
    # Test with sample files (update paths as needed)
    # Uncomment to test:
    
    # test_financial_extraction("path/to/financial_statement.pdf")
    # test_earnings_call_summary("path/to/earnings_call.pdf")
    
    print("\n=== Tests Complete ===")
    print("\nTo test with your own files:")
    print("1. Update the file paths in this script")
    print("2. Uncomment the test function calls")
    print("3. Run: python test_api.py")
