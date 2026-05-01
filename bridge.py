import webview
from vault_storage import VaultManager
from crypto_logic import check_password_strength, generate_secure_password
import pandas as pd
import os
from tkinter import filedialog, messagebox

class HermitAPI:
    def __init__(self):
        self.vault_manager = None
        self.current_vault = None

    def list_vaults(self):
        return VaultManager.list_available_vaults()

    def unlock_vault(self, name, password):
        self.vault_manager = VaultManager(name)
        if self.vault_manager.unlock_vault(password):
            self.current_vault = name
            return {"success": True, "vault": name}
        return {"success": False, "error": "Invalid password"}

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
