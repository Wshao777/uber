from cryptography.fernet import Fernet

try:
    with open('.env_key', 'rb') as f:
        key = f.read()

    with open('.env.encrypted', 'rb') as f:
        encrypted_data = f.read()

    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data).decode()

    with open('.env', 'w') as f:
        f.write(decrypted_data)

    print("✅ .env file has been decrypted successfully.")
    print("Decrypted content:")
    print(decrypted_data)

except FileNotFoundError:
    print("Error: '.env.encrypted' or '.env_key' not found. Please run zip_generator.py first.")
except Exception as e:
    print(f"An error occurred: {e}")
