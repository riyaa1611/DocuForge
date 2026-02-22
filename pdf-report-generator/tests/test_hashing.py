from app.core.security import hash_password, verify_password

try:
    print("Testing hashing...")
    hashed = hash_password("secret")
    print(f"Hashed: {hashed}")
    
    print("Testing verify...")
    is_valid = verify_password("secret", hashed)
    print(f"Valid: {is_valid}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
