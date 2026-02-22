import asyncio
import httpx

# Mimicking the exact fields the Frontend sends based on the Screenshot and Schema
# Name: Riya Gaur
# Email: gaurrriya1611@gmail.com
# Password: Riya@1611
# Confirm Password: Riya@1611

BASE_URL = "http://localhost:8000/api/v1/auth"

async def debug_frontend_payload():
    print(f"--- Simulating Frontend Payload ---")
    
    payload = {
        "name": "Riya Gaur",
        "email": "gaurrriya1611@gmail.com",
        "password": "Riya@1611",
        "confirmPassword": "Riya@1611"
    }
    print(f"Sending Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{BASE_URL}/register", json=payload)
            
            print(f"Response Status: {resp.status_code}")
            print(f"Response Body: {resp.text}")
            
            if resp.status_code == 201:
                print("✅ Backend ACCEPTED the payload.")
            else:
                print("❌ Backend REJECTED the payload.")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_frontend_payload())
