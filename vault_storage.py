import json
import os
import re
from crypto_logic import derive_key, encrypt_data, decrypt_data, generate_salt

def sanitize_vault_name(name):
    """Sanitizes the vault name to prevent path traversal."""
    if not name:
        return "vault"
    # Take the base filename
    base = os.path.basename(name)
    # Strip dangerous characters
    base = re.sub(r'[\\/:*?"<>|]', '', base)
    # Remove directory traversal patterns
    base = base.replace('..', '')
    # Ensure it's not empty after stripping
    if not base or base in ('.', '..'):
        return "vault"
    return base


VAULT_FILE = "vault.vault"

def get_data_dir():
    """Returns the path to the HermitVault data directory in the user's profile."""
    data_dir = os.path.join(os.path.expanduser("~"), "HermitVault")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

class VaultManager:
    def __init__(self, vault_name="vault"):
        self.vault_name = sanitize_vault_name(vault_name)
        self.data_dir = get_data_dir()
        self.vault_file = os.path.join(self.data_dir, f"{self.vault_name}.vault")
        self.salt = None
        self.key = None
        self.master_password = None  # transient memory for sync key derivation
        self.data = []
        self.trash = []
        self.notes = []
        self.version = 0

    @staticmethod
    def list_available_vaults():
        """Returns a list of vault names found in the data directory."""
        data_dir = get_data_dir()
        return [f[:-6] for f in os.listdir(data_dir) if f.endswith(".vault")]

    def vault_exists(self):
        return os.path.exists(self.vault_file)

    def initialize_vault(self, master_password):
        """Creates a new vault file with the master password."""
        self.salt = generate_salt()
        self.key = derive_key(master_password, self.salt)
        self.master_password = master_password
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
            
            self.master_password = master_password
            
            # Handle old vaults or structure changes
            if isinstance(decoded, list):
                self.data = decoded
                self.trash = []
                self.version = 0
            else:
                self.data = decoded.get("data", [])
                self.trash = decoded.get("trash", [])
                self.notes = decoded.get("notes", [])
                self.version = decoded.get("version", 0)
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
            "trash": self.trash,
            "notes": self.notes,
            "version": self.version
        }
        import time
        payload["last_updated"] = int(time.time())
        json_data = json.dumps(payload)
        encrypted_payload = encrypt_data(json_data, self.key)
        
        import tempfile
        dir_name = os.path.dirname(self.vault_file)
        try:
            fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmpvault")
            with os.fdopen(fd, "wb") as f:
                f.write(self.salt)
                f.write(encrypted_payload)
            # Atomic replace
            os.replace(temp_path, self.vault_file)
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
            raise e

    def add_credential(self, site, user, password, icon="", folder=""):
        import time
        self.data.append({
            "site": site,
            "user": user,
            "password": password,
            "icon": icon,
            "folder": folder,
            "last_modified": int(time.time())
        })
        self.version += 1
        self.save_vault()

    def update_credential(self, index, site, user, password, icon="", folder=""):
        if 0 <= index < len(self.data):
            import time
            self.data[index] = {
                "site": site,
                "user": user,
                "password": password,
                "icon": icon,
                "folder": folder,
                "last_modified": int(time.time())
            }
            self.version += 1
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
            if item.get("trash_type") == "note":
                del item["trash_type"]
                self.notes.append(item)
            else:
                self.data.append(item)
            self.save_vault()
            return True
        return False

    def merge_vaults(self, other_data, other_trash):
        """Merges another vault's data into this one based on timestamps."""
        # Merge Data
        my_map = {(c['site'], c['user']): c for c in self.data}
        for other in other_data:
            key = (other['site'], other['user'])
            if key in my_map:
                # Keep newest
                if other.get('last_modified', 0) > my_map[key].get('last_modified', 0):
                    my_map[key] = other
            else:
                my_map[key] = other
        self.data = list(my_map.values())

        # Merge Trash (simple union for now)
        my_trash_map = {(c['site'], c['user']): c for c in self.trash}
        for other in other_trash:
            key = (other['site'], other['user'])
            if key not in my_trash_map:
                my_trash_map[key] = other
        self.trash = list(my_trash_map.values())
        
        self.version += 1
        self.save_vault()
        return True

    def add_note(self, title, content, folder=""):
        import time
        self.notes.append({
            "title": title,
            "content": content,
            "folder": folder,
            "last_modified": int(time.time())
        })
        self.version += 1
        self.save_vault()

    def update_note(self, index, title, content, folder=""):
        if 0 <= index < len(self.notes):
            import time
            self.notes[index] = {
                "title": title,
                "content": content,
                "folder": folder,
                "last_modified": int(time.time())
            }
            self.version += 1
            self.save_vault()
            return True
        return False

    def get_notes(self):
        return self.notes

    def delete_note(self, index):
        """Moves a note to trash."""
        if 0 <= index < len(self.notes):
            note = self.notes.pop(index)
            note["trash_type"] = "note"
            self.trash.append(note)
            self.version += 1
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
        
        # Check if new password is same as old
        check_key = derive_key(new_password, self.salt)
        if check_key == self.key:
            return "ALREADY_SAME"
            
        self.salt = generate_salt()
        self.key = derive_key(new_password, self.salt)
        self.master_password = new_password
        self.save_vault()
        return True
