import requests
import json
import sys

API_URL = "http://127.0.0.1:8000"

def safe_print(text):
    # Strip non-ASCII characters to prevent console encoding issues on Windows
    print(text.encode('ascii', 'replace').decode('ascii'))

def run_tests():
    safe_print("=== STARTING BACKEND INTEGRATION TESTS ===")
    
    # Generate a unique email every run so registration doesn't conflict
    import random
    rand_num = random.randint(100, 999)
    email = f"merchant_{rand_num}@domain.com"
    password = "password123"
    
    safe_print(f"\n1. Testing User Registration for {email}...")
    try:
        reg_payload = {"full_name": "Nguyen Van A", "email": email, "password": password}
        res = requests.post(f"{API_URL}/api/auth/register", json=reg_payload)
        safe_print(f"Status Code: {res.status_code}")
        reg_json = res.json()
        if res.status_code == 200:
            safe_print("[OK] Registration successful!")
            safe_print(f"Returned Email: {reg_json.get('email')}")
            safe_print(f"Returned API Token: {reg_json.get('api_token')}")
        else:
            safe_print(f"[FAIL] Registration failed: {json.dumps(reg_json)}")
    except Exception as e:
        safe_print(f"Error during registration request: {e}")
        return
        
    # 2. Login
    safe_print("\n2. Testing User Login...")
    access_token = None
    api_token = None
    try:
        login_payload = {"email": email, "password": password}
        res = requests.post(f"{API_URL}/api/auth/login", json=login_payload)
        safe_print(f"Status Code: {res.status_code}")
        login_json = res.json()
        if res.status_code == 200:
            safe_print("[OK] Login successful!")
            access_token = login_json.get("access_token")
            api_token = login_json.get("api_token")
            safe_print(f"JWT Token: {access_token[:15]}...")
        else:
            safe_print(f"[FAIL] Login failed: {json.dumps(login_json)}")
            return
    except Exception as e:
        safe_print(f"Error during login request: {e}")
        return
        
    # 3. Get User Profile with JWT
    safe_print("\n3. Testing Get Profile (GET /api/auth/me)...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(f"{API_URL}/api/auth/me", headers=headers)
        safe_print(f"Status Code: {res.status_code}")
        me_json = res.json()
        if res.status_code == 200:
            safe_print("[OK] Profile retrieved successfully!")
            safe_print(f"Profile email: {me_json.get('email')}, Plan: {me_json.get('active_plan')}")
        else:
            safe_print(f"[FAIL] Profile retrieval failed: {json.dumps(me_json)}")
    except Exception as e:
        safe_print(f"Error during profile request: {e}")
        
    # 4. Predict size with INVALID/MISSING API Token
    safe_print("\n4. Testing Prediction with MISSING API Token...")
    # Mock base64 image (1x1 transparent png)
    mock_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    predict_payload = {
        "height": 170.0,
        "weight": 65.0,
        "gender": "male",
        "brand": "generic",
        "region": "asia",
        "image_type": "full",
        "ignore_baggy_warning": True,
        "image": mock_base64
    }
    
    try:
        res = requests.post(f"{API_URL}/predict", json=predict_payload)
        safe_print(f"Status Code: {res.status_code} (Should be 401)")
        if res.status_code == 401:
            safe_print("[OK] Correctly blocked unauthenticated request!")
        else:
            safe_print(f"[FAIL] Allowed unauthenticated request! Response: {json.dumps(res.json())}")
    except Exception as e:
        safe_print(f"Error: {e}")

    # 5. Predict size with VALID API Token
    safe_print("\n5. Testing Prediction with VALID API Token...")
    try:
        headers = {"X-API-Token": api_token}
        res = requests.post(f"{API_URL}/predict", json=predict_payload, headers=headers)
        safe_print(f"Status Code: {res.status_code} (Should be 200 or 400 validation error)")
        res_json = res.json()
        if res.status_code == 200:
            safe_print("[OK] Request authorized by API Token!")
            safe_print(f"API Response Success Field: {res_json.get('success')}")
            safe_print(f"API Response Error Details: {res_json.get('error')}")
        else:
            safe_print(f"[FAIL] API Token Authorization failed: {res.status_code} - {json.dumps(res_json)}")
    except Exception as e:
        safe_print(f"Error: {e}")

    # 6. Predict size with GUEST API Token
    safe_print("\n6. Testing Prediction with GUEST API Token...")
    try:
        headers = {"X-API-Token": "fv_demo_guest_key"}
        res = requests.post(f"{API_URL}/predict", json=predict_payload, headers=headers)
        safe_print(f"Status Code: {res.status_code} (Should be 200 or 400 validation error)")
        res_json = res.json()
        if res.status_code == 200:
            safe_print("[OK] Guest Request authorized by guest token!")
        else:
            safe_print(f"[FAIL] Guest Token Authorization failed: {res.status_code} - {json.dumps(res_json)}")
    except Exception as e:
        safe_print(f"Error: {e}")

if __name__ == "__main__":
    run_tests()
