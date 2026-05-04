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

    def get_all_items(self):
        if not self.vault_manager: return []
        creds = self.vault_manager.get_credentials()
        # Mark as credential
        new_creds = []
        for i, c in enumerate(creds):
            item = c.copy()
            item["type"] = "credential"
            item["original_index"] = i
            new_creds.append(item)
        
        notes = self.vault_manager.get_notes()
        new_notes = []
        for i, n in enumerate(notes):
            item = n.copy()
            item["type"] = "note"
            item["original_index"] = i
            new_notes.append(item)
        
        return new_creds + new_notes

    def add_credential(self, site, user, password, icon="", folder=""):
        if not self.vault_manager: return False
        self.vault_manager.add_credential(site, user, password, icon, folder)
        return True

    def update_credential(self, index, site, user, password, icon="", folder=""):
        if not self.vault_manager: return False
        return self.vault_manager.update_credential(index, site, user, password, icon, folder)

    def get_notes(self):
        if not self.vault_manager: return []
        return self.vault_manager.get_notes()

    def add_note(self, title, content, folder=""):
        if not self.vault_manager: return False
        self.vault_manager.add_note(title, content, folder)
        return True

    def update_note(self, index, title, content, folder=""):
        if not self.vault_manager: return False
        self.vault_manager.update_note(index, title, content, folder)
        return True

    def delete_note(self, index):
        if not self.vault_manager: return False
        self.vault_manager.delete_note(index)
        return True

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

    def browser_import(self):
        """Import credentials from CSV (Chrome/Edge) or generic TXT files"""
        if not self.vault_manager: return {"success": False, "error": "Vault not unlocked"}
        
        path = filedialog.askopenfilename(
            filetypes=[
                ("Credential Files", "*.csv *.txt"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if not path: return {"success": False, "error": "No file selected"}

        imported_count = 0
        try:
            # Try parsing as CSV first
            if path.lower().endswith('.csv'):
                df = pd.read_csv(path)
                # Normalize column names to lowercase
                df.columns = [c.lower() for c in df.columns]
                
                # Mapping for common browser export headers
                site_cols = ['url', 'site', 'website', 'name', 'title']
                user_cols = ['username', 'user', 'login', 'email', 'user_name']
                pass_cols = ['password', 'pass', 'word', 'credential']

                for _, row in df.iterrows():
                    site = next((row[c] for c in site_cols if c in df.columns), "Imported Site")
                    user = next((row[c] for c in user_cols if c in df.columns), "Imported User")
                    password = next((row[c] for c in pass_cols if c in df.columns), "")
                    
                    if password:
                        self.vault_manager.add_credential(str(site), str(user), str(password), folder="Imported")
                        imported_count += 1
            
            # Try parsing as TXT with separators
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        
                        # Try common separators: , ; : | \t
                        parts = None
                        for sep in [',', ';', ':', '|', '\t']:
                            if sep in line:
                                candidate = line.split(sep)
                                if len(candidate) >= 3:
                                    parts = candidate
                                    break
                        
                        if parts and len(parts) >= 3:
                            site = parts[0].strip()
                            user = parts[1].strip()
                            password = parts[2].strip()
                            self.vault_manager.add_credential(site, user, password, folder="Imported")
                            imported_count += 1

            if imported_count > 0:
                return {"success": True, "count": imported_count}
            else:
                return {"success": False, "error": "No valid credentials found in file"}
                
        except Exception as e:
            print(f"Import error: {e}")
            return {"success": False, "error": f"Error parsing file: {str(e)}"}

    def get_sync_info(self):
        return {
            "ip": self.sync_manager.get_local_ip(),
            "port": self.sync_manager.port
        }

    def start_sync_server(self, port=None):
        if not self.current_vault: return {"success": False, "error": "No vault open"}
        vault_path = f"{self.current_vault}.vault"
        
        def on_done(msg):
            print(f"Sync server: {msg}")
            
        try:
            p = int(port) if port else None
            self.sync_manager.start_server(vault_path, on_done, p)
            return {"success": True, "msg": "Sync server started"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_sync_server(self):
        if self.sync_manager:
            return self.sync_manager.stop_server()
        return False

    def connect_to_sync(self, target_ip, port=None):
        if not self.vault_manager: return {"success": False, "error": "Open vault first"}
        
        def on_data(data):
            if isinstance(data, str) and data.startswith("Error"):
                print(f"Sync error: {data}")
                return
            
            try:
                # Assuming the received vault has the same master password as the current one
                # We need the salt from the received data (first 16 bytes)
                remote_salt = data[:16]
                remote_encrypted = data[16:]
                
                from crypto_logic import decrypt_data
                decrypted_json = decrypt_data(remote_encrypted, self.vault_manager.key)
                remote_payload = json.loads(decrypted_json)
                
                remote_creds = remote_payload.get("data", [])
                remote_notes = remote_payload.get("notes", [])
                
                # Merge Credentials
                added_count = 0
                local_creds = self.vault_manager.data
                for rc in remote_creds:
                    # Check if exists (by site and user)
                    exists = any(lc['site'] == rc['site'] and lc['user'] == rc['user'] for lc in local_creds)
                    if not exists:
                        local_creds.append(rc)
                        added_count += 1
                
                # Merge Notes
                notes_added = 0
                local_notes = self.vault_manager.notes
                for rn in remote_notes:
                    # Check if exists (by title and content)
                    exists = any(ln['title'] == rn['title'] and ln['content'] == rn['content'] for ln in local_notes)
                    if not exists:
                        local_notes.append(rn)
                        notes_added += 1
                
                if added_count > 0 or notes_added > 0:
                    self.vault_manager.version += 1
                    self.vault_manager.save_vault()
                    print(f"Merged: {added_count} credentials and {notes_added} notes added.")
                else:
                    print("Sync complete: No new items found.")

            except Exception as e:
                print(f"Failed to merge received vault: {e}")

        try:
            p = int(port) if port else None
            self.sync_manager.receive_vault(target_ip, on_data, p)
            return {"success": True, "msg": "Connection established, waiting for data..."}
        except Exception as e:
            return {"success": False, "error": str(e)}
