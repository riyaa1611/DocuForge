import asyncio
import httpx
import random
import string
import traceback

BASE_URL = "http://localhost:8000/api/v1/auth"

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"debug_{random_str}@example.com"

async def debug_registration():
    email = generate_random_email()
    password = "securepassword123"
    
    print(f"--- Debugging Registration ---")
    print(f"Attempting to register: {email}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Register
            resp = await client.post(f"{BASE_URL}/register", json={
                "name": "Test User",
                "email": email,
                "password": password,
                "confirmPassword": password
            })
            
            print(f"Response Status: {resp.status_code}")
            print(f"Response Body: {resp.text}")
            
            if resp.status_code == 201:
                print("✅ Registration Successful")
                
                # Try Login
                print(f"Attempting to login...")
                login_resp = await client.post(f"{BASE_URL}/login", json={
                    "email": email,
                    "password": password
                })
                print(f"Login Status: {login_resp.status_code}")
                if login_resp.status_code == 200:
                    print("✅ Login Successful")
                else:
                    print(f"❌ Login Failed: {login_resp.text}")
            else:
                print("❌ Registration Failed")

    except Exception as e:
        print(f"❌ Exception occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_registration())
