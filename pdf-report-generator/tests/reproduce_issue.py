import asyncio
import httpx
import random
import string

BASE_URL = "http://localhost:8000/api/v1/auth"

def generate_random_email():
    """Generate a random email with mixed case."""
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"User_{random_str}@Example.com"

async def test_case_insensitive_login():
    email_mixed_case = generate_random_email()
    password = "securepassword123"
    
    print(f"1. Registering with mixed case: {email_mixed_case}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register
        resp = await client.post(f"{BASE_URL}/register", json={
            "email": email_mixed_case,
            "password": password
        })
        
        if resp.status_code != 201:
            print(f"Registration failed: {resp.text}")
            return
            
        print("Registration successful.")
        
        # Try Login with Exact Case
        print(f"2. Logging in with EXACT case: {email_mixed_case}")
        resp = await client.post(f"{BASE_URL}/login", json={
            "email": email_mixed_case,
            "password": password
        })
        if resp.status_code == 200:
            print("Login with exact case: SUCCESS")
        else:
            print(f"Login with exact case: FAILED ({resp.status_code})")

        # Try Login with Lower Case
        email_lower_case = email_mixed_case.lower()
        print(f"3. Logging in with LOWER case: {email_lower_case}")
        resp = await client.post(f"{BASE_URL}/login", json={
            "email": email_lower_case,
            "password": password
        })
        
        if resp.status_code == 200:
            print("Login with lower case: SUCCESS (Fix Verified)")
        else:
            print(f"Login with lower case: FAILED ({resp.status_code}) - Issue Reproduced")

if __name__ == "__main__":
    asyncio.run(test_case_insensitive_login())
