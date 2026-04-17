#!/usr/bin/env python3
"""
Quick test script for JWT authentication endpoints.
Run this after starting the server with: uvicorn main:app --reload
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response: requests.Response):
    """Print formatted response."""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_login(email: str, password: str) -> Optional[str]:
    """Test login endpoint and return access token."""
    print_section(f"Testing Login: {email}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"\n✅ Login successful! Token: {token[:50]}...")
        return token
    else:
        print(f"\n❌ Login failed!")
        return None

def test_get_user_info(token: str):
    """Test getting current user info."""
    print_section("Testing Get Current User Info")
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print("\n✅ Successfully retrieved user info!")
    else:
        print("\n❌ Failed to get user info!")

def test_verify_token(token: str):
    """Test token verification endpoint."""
    print_section("Testing Token Verification")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/verify-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print("\n✅ Token is valid!")
    else:
        print("\n❌ Token verification failed!")

def test_invalid_credentials():
    """Test login with invalid credentials."""
    print_section("Testing Invalid Credentials")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "wrong@email.com", "password": "wrongpassword"}
    )
    
    print_response(response)
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected invalid credentials!")
    else:
        print("\n❌ Should have rejected invalid credentials!")

def test_invalid_token():
    """Test accessing protected endpoint with invalid token."""
    print_section("Testing Invalid Token")
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    print_response(response)
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected invalid token!")
    else:
        print("\n❌ Should have rejected invalid token!")

def main():
    """Run all tests."""
    print("\n" + "🚀 JWT Authentication Test Suite".center(60))
    print("Make sure the server is running on http://localhost:8000\n")
    
    try:
        # Test 1: Valid login for BA
        token_ba = test_login("ba@hsbc.com", "password123")
        
        if token_ba:
            # Test 2: Get user info with valid token
            test_get_user_info(token_ba)
            
            # Test 3: Verify token
            test_verify_token(token_ba)
        
        # Test 4: Valid login for FBA
        token_fba = test_login("fba@hsbc.com", "password123")
        
        if token_fba:
            test_get_user_info(token_fba)
        
        # Test 5: Valid login for QA
        token_qa = test_login("qa@hsbc.com", "password123")
        
        if token_qa:
            test_get_user_info(token_qa)
        
        # Test 6: Invalid credentials
        test_invalid_credentials()
        
        # Test 7: Invalid token
        test_invalid_token()
        
        print_section("Test Suite Complete")
        print("\n✅ All tests completed! Check results above.\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server!")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  python -m uvicorn main:app --reload\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
