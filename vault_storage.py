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
        self.trash = []

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
        self.trash = []
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
            decoded = json.loads(decrypted_json)
            
            # Handle old vaults or structure changes
            if isinstance(decoded, list):
                self.data = decoded
                self.trash = []
            else:
                self.data = decoded.get("data", [])
                self.trash = decoded.get("trash", [])
            return True
        except Exception as e:
            print(f"Unlock failed: {e}")
            return False

    def save_vault(self):
        """Encrypts and saves the current data to the vault file."""
        if self.key is None or self.salt is None:
            raise Exception("Vault not unlocked")
        
        payload = {
            "data": self.data,
            "trash": self.trash
        }
        json_data = json.dumps(payload)
        encrypted_payload = encrypt_data(json_data, self.key)
        
        with open(self.vault_file, "wb") as f:
            f.write(self.salt)
            f.write(encrypted_payload)

    def add_credential(self, site, user, password, icon=""):
        self.data.append({
            "site": site,
            "user": user,
            "password": password,
            "icon": icon
        })
        self.save_vault()

    def update_credential(self, index, site, user, password, icon=""):
        if 0 <= index < len(self.data):
            self.data[index] = {
                "site": site,
                "user": user,
                "password": password,
                "icon": icon
            }
            self.save_vault()
            return True
        return False

    def get_credentials(self):
        return self.data

    def get_trash(self):
        return self.trash

    def delete_credential(self, index):
        if 0 <= index < len(self.data):
            item = self.data.pop(index)
            self.trash.append(item)
            self.save_vault()
            return True
        return False

    def restore_credential(self, index):
        if 0 <= index < len(self.trash):
            item = self.trash.pop(index)
            self.data.append(item)
            self.save_vault()
            return True
        return False

    def permanent_delete(self, index):
        if 0 <= index < len(self.trash):
            self.trash.pop(index)
            self.save_vault()
            return True
        return False

    def change_password(self, new_password):
        """Re-encrypts the vault data with a new password."""
        if self.key is None: return False
        self.salt = generate_salt()
        self.key = derive_key(new_password, self.salt)
        self.save_vault()
        return True
