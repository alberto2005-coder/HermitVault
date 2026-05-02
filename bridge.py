import webview
from vault_storage import VaultManager
from crypto_logic import check_password_strength, generate_secure_password
import pandas as pd
import os
from tkinter import filedialog, messagebox

from sync_logic import SyncManager

class HermitAPI:
    def __init__(self):
        self.vault_manager = None
        self.current_vault = None
        self.security_file = ".cache.dat"
        self._load_security_state()
        self.sync_manager = SyncManager()

    def _load_security_state(self):
        import json, base64
        if os.path.exists(self.security_file):
            try:
                with open(self.security_file, "r") as f:
                    # Simple obfuscation to prevent casual editing
                    encoded_data = f.read()
                    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                    self.security_state = json.loads(decoded_data)
            except:
                self.security_state = {"failed_attempts": 0, "lock_until": 0}
        else:
            self.security_state = {"failed_attempts": 0, "lock_until": 0}

    def _save_security_state(self):
        import json, base64
        data_str = json.dumps(self.security_state)
        encoded_data = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
        with open(self.security_file, "w") as f:
            f.write(encoded_data)

    def get_security_state(self):
        import time
        now = int(time.time())
        # Clean up old locks
        if now > self.security_state["lock_until"]:
            self.security_state["lock_until"] = 0
            self._save_security_state()
        return self.security_state

    def register_failed_attempt(self):
        import time
        self.security_state["failed_attempts"] += 1
        # Exponential backoff: 2^n seconds (max 30s delay)
        delay = min(pow(2, self.security_state["failed_attempts"]), 30)
        self.security_state["lock_until"] = int(time.time()) + delay
        self._save_security_state()
        return {"lock_until": self.security_state["lock_until"], "delay": delay}

    def reset_failed_attempts(self):
        self.security_state["failed_attempts"] = 0
        self.security_state["lock_until"] = 0
        self._save_security_state()

    def list_vaults(self):
        return VaultManager.list_available_vaults()

    def unlock_vault(self, name, password):
        state = self.get_security_state()
        import time
        if state["lock_until"] > time.time():
            return {"success": False, "error": "SYSTEM_LOCKED"}

        self.vault_manager = VaultManager(name)
        if self.vault_manager.unlock_vault(password):
            self.current_vault = name
            self.reset_failed_attempts()
            return {"success": True, "vault": name}
        
        # On failure
        lock_info = self.register_failed_attempt()
        return {"success": False, "error": "Invalid password", "lock_until": lock_info["lock_until"], "delay": lock_info["delay"]}

    def create_vault(self, name, password):
        score, _, _ = check_password_strength(password)
        if score < 3:
            return {"success": False, "error": "Password too weak"}
            
        self.vault_manager = VaultManager(name)
        self.vault_manager.initialize_vault(password)
        self.current_vault = name
        return {"success": True, "vault": name}

    def get_credentials(self):
        if not self.vault_manager: return []
        return self.vault_manager.get_credentials()

    def add_credential(self, site, user, password, icon=""):
        if not self.vault_manager: return False
        self.vault_manager.add_credential(site, user, password, icon)
        return True

    def update_credential(self, index, site, user, password, icon=""):
        if not self.vault_manager: return False
        return self.vault_manager.update_credential(index, site, user, password, icon)

    def delete_credential(self, index):
        if not self.vault_manager: return False
        self.vault_manager.delete_credential(index)
        return True

    def generate_password(self, length=16):
        return generate_secure_password(length)

    def export_excel(self):
        if not self.vault_manager: return False
        creds = self.vault_manager.get_credentials()
        if not creds: return False
        
        try:
            df = pd.DataFrame(creds)
            # Reorder columns for "Clean" look
            df = df[['site', 'user', 'password']]
            df.columns = ['Website/Service', 'Username/Email', 'Password']
            
            # Use tkinter to ask for file path (cleanest way in pywebview)
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"HermitVault_{self.current_vault}_Export.xlsx"
            )
            
            if path:
                df.to_excel(path, index=False)
                return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
        return False

    def change_master_password(self, new_password):
        if not self.vault_manager: return {"success": False, "error": "Vault not unlocked"}
        score, _, _ = check_password_strength(new_password)
        if score < 3:
            return {"success": False, "error": "Password too weak"}
        
        res = self.vault_manager.change_password(new_password)
        if res == "ALREADY_SAME":
            return {"success": False, "error": "New password is same as current one"}
        return {"success": res is True}

    def get_trash(self):
        if not self.vault_manager: return []
        return self.vault_manager.get_trash()

    def restore_credential(self, index):
        if not self.vault_manager: return False
        return self.vault_manager.restore_credential(index)

    def permanent_delete(self, index):
        if not self.vault_manager: return False
        return self.vault_manager.permanent_delete(index)

    def backup_vault(self):
        if not self.vault_manager or not self.current_vault: return False
        src = f"{self.current_vault}.vault"
        if not os.path.exists(src): return False
        
        path = filedialog.asksaveasfilename(
            defaultextension=".vault",
            filetypes=[("HermitVault files", "*.vault")],
            initialfile=f"BACKUP_{self.current_vault}.vault"
        )
        if path:
            import shutil
            shutil.copy2(src, path)
            return True
        return False

    def import_vault(self):
        path = filedialog.askopenfilename(
            filetypes=[("HermitVault files", "*.vault")]
        )
        if path:
            import shutil
            filename = os.path.basename(path)
            dest = os.path.join(os.getcwd(), filename)
            shutil.copy2(path, dest)
            return True
        return False

    def get_sync_info(self):
        return {
            "ip": self.sync_manager.get_local_ip(),
            "port": self.sync_manager.port
        }

    def start_sync_server(self):
        if not self.current_vault: return {"success": False, "error": "No vault open"}
        vault_path = f"{self.current_vault}.vault"
        
        def on_done(msg):
            print(f"Sync server: {msg}")
            
        self.sync_manager.start_server(vault_path, on_done)
        return {"success": True, "msg": "Sync server started"}

    def connect_to_sync(self, target_ip):
        if not self.vault_manager: return {"success": False, "error": "Open vault first"}
        
        def on_data(data):
            if isinstance(data, str) and data.startswith("Error"):
                print(data)
                return
            
            # Here we have the encrypted vault bytes
            try:
                # We need to decrypt it with the CURRENT vault's key
                # This assumes both vaults have the same password!
                import json
                from vault_storage import decrypt_data
                
                salt = data[:16]
                payload = data[16:]
                # We use the existing key (derived from password)
                # Note: This only works if salt is same or if we derive again
                # Actually, derive_key depends on salt. 
                # So we MUST derive a temp key using the target's salt and OUR current password.
                
                # To get the password, we might need to store it or ask user
                # For now, let's assume we can merge.
                # In a real app, we'd ask "Enter password for the incoming vault"
                pass
            except Exception as e:
                print(f"Sync Merge Error: {e}")

        # This part is complex because of key derivation.
        # Let's simplify: Send the DECRYPTED data over the local network (secure WiFi?)
        # NO, that's not secure.
        return {"success": False, "error": "P2P Sync requires same-network key exchange (In Development)"}
