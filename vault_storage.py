import json
import os
from crypto_logic import derive_key, encrypt_data, decrypt_data, generate_salt

VAULT_FILE = "vault.vault"

class VaultManager:
    def __init__(self, vault_name="vault"):
        self.vault_name = vault_name
        self.vault_file = f"{vault_name}.vault"
        self.salt = None
        self.key = None
        self.data = []

    @staticmethod
    def list_available_vaults():
        """Returns a list of vault names found in the current directory."""
        return [f[:-6] for f in os.listdir(".") if f.endswith(".vault")]

    def vault_exists(self):
        return os.path.exists(self.vault_file)

    def initialize_vault(self, master_password):
        """Creates a new vault file with the master password."""
        self.salt = generate_salt()
        self.key = derive_key(master_password, self.salt)
        self.data = []
        self.save_vault()

    def unlock_vault(self, master_password):
        """Attempts to unlock the vault. Returns True if successful, False otherwise."""
        if not self.vault_exists():
            return False
        
        try:
            with open(self.vault_file, "rb") as f:
                content = f.read()
                self.salt = content[:16]
                encrypted_payload = content[16:]
            
            self.key = derive_key(master_password, self.salt)
            decrypted_json = decrypt_data(encrypted_payload, self.key)
            self.data = json.loads(decrypted_json)
            return True
        except Exception as e:
            print(f"Unlock failed: {e}")
            return False

    def save_vault(self):
        """Encrypts and saves the current data to the vault file."""
        if self.key is None or self.salt is None:
            raise Exception("Vault not unlocked")
        
        json_data = json.dumps(self.data)
        encrypted_payload = encrypt_data(json_data, self.key)
        
        with open(self.vault_file, "wb") as f:
            f.write(self.salt)
            f.write(encrypted_payload)

    def add_credential(self, site, user, password):
        self.data.append({
            "site": site,
            "user": user,
            "password": password
        })
        self.save_vault()

    def get_credentials(self):
        return self.data

    def delete_credential(self, index):
        if 0 <= index < len(self.data):
            self.data.pop(index)
            self.save_vault()
            return True
        return False
