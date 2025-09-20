import zipfile
import os
from cryptography.fernet import Fernet

def main():
    """
    Generates an encrypted .env file, an OpenVPN config, and packages
    the entire project into a ZIP archive.
    The encryption key is NOT included in the zip for security.
    """
    # --- Configuration ---
    zip_filename = 'stormcar820_v7_package.zip'

    # --- Generate Encrypted .env ---
    try:
        key = Fernet.generate_key()
        cipher = Fernet(key)

        env_content = """
BOT_TOKEN=your_telegram_token_here
UBER_API_KEY=your_uber_api_key_here
SHEETS_CREDENTIALS=path/to/your/credentials.json
GODDESS_MASTER_CODE=G8-MASTER
""".encode()

        encrypted_env = cipher.encrypt(env_content)

        # Save the encrypted file
        with open('.env.encrypted', 'wb') as f:
            f.write(encrypted_env)

        # Save the key to a separate file that will NOT be zipped.
        with open('.env.key', 'wb') as f:
            f.write(key)

        print("✅ Successfully generated '.env.encrypted' and '.env.key'.")
        print("IMPORTANT: Securely transfer the '.env.key' file. It is NOT in the ZIP archive.")

    except Exception as e:
        print(f"🔥 Error during .env encryption: {e}")

    # --- Generate OpenVPN Config Example ---
    try:
        vpn_config = """
client
dev tun
proto udp
remote your-vpn-server.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
cert client.crt
key client.key
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
verb 3
"""
        with open('openvpn_auto.conf', 'w') as f:
            f.write(vpn_config)
        print("✅ Successfully generated 'openvpn_auto.conf'.")
    except Exception as e:
        print(f"🔥 Error generating OpenVPN config: {e}")


    # --- Package files into ZIP archive ---
    files_to_zip = [
        'README.md',
        'dummy.html',
        'dispatcher.js',
        'server.py',
        'goddess_roster_excel.py',
        'generate_mock_orders.py',
        'decrypt_env.py',
        '.env.encrypted',
        'openvpn_auto.conf',
        'goddess_truecodes.json',
        'goddess_data_table.md',
        '.env.goddess',
        '.github/workflows/auto-deploy.yml'
    ]

    print(f"\n📦 Creating ZIP archive: {zip_filename}...")

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    zipf.write(file_path)
                    print(f"  -> Added '{file_path}'")
                else:
                    print(f"  -> ⚠️  Warning: File '{file_path}' not found. Skipping.")

        print(f"\n✅ Successfully created ZIP archive: {zip_filename}")
        print("To use, unzip the package and run 'python decrypt_env.py' after securely placing the '.env.key' file in the same directory.")

    except Exception as e:
        print(f"🔥 Error creating ZIP archive: {e}")

if __name__ == '__main__':
    main()
