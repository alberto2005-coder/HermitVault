import customtkinter as ctk
import pyperclip
import os
from PIL import Image, ImageTk
from vault_storage import VaultManager
from crypto_logic import generate_secure_password, check_password_strength
from config_manager import load_config, save_config
from tkinter import messagebox

# Configuration
CONFIG = load_config()
ctk.set_appearance_mode(CONFIG.get("appearance", "dark"))

# Premium Color Palette (Light, Dark)
ACCENT_COLOR = "#8e44ad"
BG_COLOR = ("#f2f2f2", "#1a1a1a")
CARD_COLOR = ("#ffffff", "#252525")
BORDER_COLOR = ("#d1d1d1", "#333333")
TEXT_COLOR = ("#1a1a1a", "#ffffff")
SECONDARY_TEXT = ("#666666", "#b3b3b3")
INPUT_BG = ("#ffffff", "#1e1e1e")

class HermitVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HermitVault - Secure Password Manager")
        self.geometry("900x700")
        
        # Load Logo
        self.load_logo()
        
        self.current_vault_name = None
        self.vault_manager = None
        
        # Center the window
        self.center_window()

        # UI container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def load_logo(self):
        self.logo_path = "logo.png"
        if os.path.exists(self.logo_path):
            self.logo_img = ctk.CTkImage(light_image=Image.open(self.logo_path),
                                        dark_image=Image.open(self.logo_path),
                                        size=(60, 60))
            self.logo_small = ctk.CTkImage(light_image=Image.open(self.logo_path),
                                          dark_image=Image.open(self.logo_path),
                                          size=(30, 30))
            # Set window icon
            try:
                img = Image.open(self.logo_path)
                self.icon_photo = ImageTk.PhotoImage(img)
                self.after(200, lambda: self.iconphoto(False, self.icon_photo))
            except Exception as e:
                print(f"Icon error: {e}")
        else:
            self.logo_img = None
            self.logo_small = None

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_container()
        self.container.configure(fg_color=BG_COLOR)
        
        # Get available vaults
        vaults = VaultManager.list_available_vaults()
        
        # Main login card
        frame = ctk.CTkFrame(self.container, corner_radius=25, fg_color=CARD_COLOR, border_width=2, border_color=BORDER_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.logo_img:
            ctk.CTkLabel(frame, image=self.logo_img, text="").pack(pady=(40, 0))

        ctk.CTkLabel(frame, text="HermitVault", font=("Outfit", 32, "bold"), text_color=TEXT_COLOR).pack(pady=(10, 5), padx=60)
        
        # Tabs for "Unlock" vs "Create"
        self.tabview = ctk.CTkTabview(frame, width=400, height=350, fg_color="transparent", 
                                     segmented_button_selected_color=ACCENT_COLOR,
                                     segmented_button_unselected_hover_color="#333333")
        self.tabview.pack(pady=10, padx=40)
        
        # Theme Selector on Login Screen
        theme_frame = ctk.CTkFrame(frame, fg_color="transparent")
        theme_frame.pack(side="bottom", pady=(0, 20))
        ctk.CTkLabel(theme_frame, text="Theme:", font=("Outfit", 10), text_color=SECONDARY_TEXT).pack(side="left", padx=5)
        self.theme_menu = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light"], 
                                          width=100, height=25, font=("Outfit", 10),
                                          fg_color="#333333", button_color=ACCENT_COLOR,
                                          command=self.change_appearance_mode)
        self.theme_menu.set(CONFIG.get("appearance", "dark").capitalize())
        self.theme_menu.pack(side="left")

        tab_unlock = self.tabview.add("Unlock Vault")
        tab_create = self.tabview.add("New Vault")

        # --- UNLOCK TAB ---
        if not vaults:
            ctk.CTkLabel(tab_unlock, text="No vaults found.\nGo to 'New Vault' to create one.", 
                        font=("Outfit", 14), text_color=SECONDARY_TEXT).pack(pady=50)
        else:
            ctk.CTkLabel(tab_unlock, text="Select Vault:", font=("Outfit", 13)).pack(pady=(20, 5))
        self.vault_select = ctk.CTkOptionMenu(tab_unlock, values=vaults, width=320, height=45, 
                                                fg_color=INPUT_BG, button_color=ACCENT_COLOR, 
                                                text_color=TEXT_COLOR,
                                                dropdown_fg_color=CARD_COLOR, corner_radius=20)
        self.vault_select.pack(pady=10)
            
            # Password row for Unlock
        pass_container = ctk.CTkFrame(tab_unlock, fg_color="transparent")
        pass_container.pack(pady=10)
            
        self.password_entry = ctk.CTkEntry(pass_container, placeholder_text="Master Password", show="*", 
                                         width=280, height=50, font=("Outfit", 14),
                                         border_color=BORDER_COLOR, fg_color=INPUT_BG, text_color=TEXT_COLOR)
        self.password_entry.pack(side="left", padx=(0, 5))
        self.password_entry.bind("<Return>", lambda e: self.on_login())

        self.eye_btn = ctk.CTkButton(pass_container, text="👁️", width=50, height=50, 
                                     command=lambda: self.toggle_visibility(self.password_entry, self.eye_btn),
                                     fg_color=BORDER_COLOR, hover_color=ACCENT_COLOR, 
                                     text_color=TEXT_COLOR, font=("Outfit", 16))
        self.eye_btn.pack(side="left")
            
        ctk.CTkButton(tab_unlock, text="Unlock Vault", command=self.on_login, 
                         width=320, height=55, font=("Outfit", 16, "bold"),
                         fg_color=ACCENT_COLOR, corner_radius=25).pack(pady=20)

        # --- CREATE TAB ---
        ctk.CTkLabel(tab_create, text="Vault Name:", font=("Outfit", 13)).pack(pady=(20, 5))
        self.new_vault_name = ctk.CTkEntry(tab_create, placeholder_text="e.g. Personal, Work", 
                                          width=320, height=50, corner_radius=20)
        self.new_vault_name.pack(pady=5)
        
        ctk.CTkLabel(tab_create, text="Master Password:", font=("Outfit", 13)).pack(pady=(10, 5))
        
        # Password row for Create
        create_pass_frame = ctk.CTkFrame(tab_create, fg_color="transparent")
        create_pass_frame.pack(pady=5)
        
        self.new_vault_pass = ctk.CTkEntry(create_pass_frame, placeholder_text="Master Password", show="*", 
                                          width=260, height=50, font=("Outfit", 14), corner_radius=20)
        self.new_vault_pass.pack(side="left", padx=(0, 5))
        
        self.create_eye_btn = ctk.CTkButton(create_pass_frame, text="👁️", width=50, height=50, 
                                           command=lambda: self.toggle_visibility(self.new_vault_pass, self.create_eye_btn),
                                           fg_color=INPUT_BG, hover_color=ACCENT_COLOR, 
                                           text_color=TEXT_COLOR, corner_radius=20)
        self.create_eye_btn.pack(side="left")
        
        # Master Strength Meter
        self.m_strength_container = ctk.CTkFrame(tab_create, fg_color="transparent")
        self.m_strength_container.pack(pady=(5, 10), fill="x", padx=40)
        self.m_strength_bar = ctk.CTkProgressBar(self.m_strength_container, width=220, height=6, fg_color=BORDER_COLOR)
        self.m_strength_bar.set(0)
        self.m_strength_bar.pack(side="left", padx=(0, 10))
        self.m_strength_label = ctk.CTkLabel(self.m_strength_container, text="", font=("Outfit", 10))
        self.m_strength_label.pack(side="left")
        
        self.new_vault_pass.bind("<KeyRelease>", lambda e: self.update_master_strength_indicator())

        ctk.CTkButton(tab_create, text="Create Vault", command=self.on_create_vault, 
                     width=320, height=55, font=("Outfit", 16, "bold"),
                     fg_color=ACCENT_COLOR, corner_radius=25).pack(pady=20)

    def update_master_strength_indicator(self):
        password = self.new_vault_pass.get()
        score, label, color = check_password_strength(password)
        self.m_strength_bar.set(score / 4 if password else 0)
        self.m_strength_bar.configure(progress_color=color)
        self.m_strength_label.configure(text=label, text_color=color)

    def on_login(self):
        vault_name = self.vault_select.get()
        password = self.password_entry.get()
        
        if not password:
            messagebox.showwarning("Error", "Enter your password.")
            return

        self.vault_manager = VaultManager(vault_name)
        if self.vault_manager.unlock_vault(password):
            self.current_vault_name = vault_name
            self.show_vault_screen()
        else:
            messagebox.showerror("Error", "Invalid Password.")

    def on_create_vault(self):
        name = self.new_vault_name.get().strip()
        password = self.new_vault_pass.get()
        
        if not name or not password:
            messagebox.showwarning("Error", "Name and password are required.")
            return
        
        if name in VaultManager.list_available_vaults():
            messagebox.showwarning("Error", "A vault with this name already exists.")
            return

        score, label, _ = check_password_strength(password)
        if score < 3:
            messagebox.showwarning("Weak Password", f"Password is '{label}'. It must be at least 'Good'.")
            return

        self.vault_manager = VaultManager(name)
        self.vault_manager.initialize_vault(password)
        self.current_vault_name = name
        messagebox.showinfo("Success", f"Vault '{name}' created!")
        self.show_vault_screen()

    def show_vault_screen(self):
        self.clear_container()
        self.container.configure(fg_color=BG_COLOR)
        
        # Sidebar
        sidebar = ctk.CTkFrame(self.container, width=250, corner_radius=0, fg_color=CARD_COLOR)
        sidebar.pack(side="left", fill="y")

        if self.logo_img:
            ctk.CTkLabel(sidebar, image=self.logo_img, text="").pack(pady=(40, 10))
        
        ctk.CTkLabel(sidebar, text=f"{self.current_vault_name.title()} Vault", font=("Outfit", 20, "bold")).pack(pady=(0, 40))

        add_btn = ctk.CTkButton(sidebar, text="+ Add New", command=self.show_add_dialog, 
                               width=180, height=50, font=("Outfit", 14, "bold"),
                               fg_color=ACCENT_COLOR, hover_color="#7d3c98", corner_radius=25)
        add_btn.pack(pady=10)
        
        # Logout button
        logout_btn = ctk.CTkButton(sidebar, text="🔒 Lock & Exit", command=self.show_login_screen,
                                  width=180, height=50, font=("Outfit", 14),
                                  fg_color="#333333", hover_color="#444444", corner_radius=25)
        logout_btn.pack(pady=10)
        
        # Appearance Switch in Sidebar
        theme_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        theme_frame.pack(side="bottom", pady=20)
        ctk.CTkLabel(theme_frame, text="Appearance:", font=("Outfit", 11), text_color=SECONDARY_TEXT).pack(pady=5)
        self.sidebar_theme = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light"], 
                                             width=120, height=30, font=("Outfit", 11),
                                             fg_color="#333333", button_color=ACCENT_COLOR,
                                             command=self.change_appearance_mode)
        self.sidebar_theme.set(CONFIG.get("appearance", "dark").capitalize())
        self.sidebar_theme.pack()

        stats_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        stats_frame.pack(side="bottom", fill="x", pady=40)
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="", font=("Outfit", 12), text_color=SECONDARY_TEXT)
        self.stats_label.pack()

        # Main Content Area
        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(content, text="Your Secure Vault", font=("Outfit", 28, "bold"), anchor="w").pack(fill="x", pady=(0, 20))

        # Scrollable area
        self.scroll_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        self.refresh_vault_list()

    def refresh_vault_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        credentials = self.vault_manager.get_credentials()
        
        # Update stats label
        self.stats_label.configure(text=f"{len(credentials)} items secured")
        
        if not credentials:
            ctk.CTkLabel(self.scroll_frame, text="No credentials saved yet.\nClick '+ Add Credential' to start.", font=("Outfit", 14), text_color="gray").pack(pady=100)
            return

        for i, cred in enumerate(credentials):
            self.create_credential_card(i, cred)

    def create_credential_card(self, index, cred):
        card = ctk.CTkFrame(self.scroll_frame, height=90, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", pady=10, padx=5)

        # Info Layout
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=25, fill="y")

        ctk.CTkLabel(info_frame, text=cred['site'], font=("Outfit", 18, "bold"), anchor="w", text_color=TEXT_COLOR).pack(pady=(15, 0), fill="x")
        ctk.CTkLabel(info_frame, text=cred['user'], font=("Outfit", 13), text_color=SECONDARY_TEXT, anchor="w").pack(pady=(0, 15), fill="x")

        # Actions Layout
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=25)

        copy_user_btn = ctk.CTkButton(actions_frame, text="User", width=80, height=35, 
                                     fg_color=BORDER_COLOR, hover_color=ACCENT_COLOR, 
                                     text_color=TEXT_COLOR, font=("Outfit", 12, "bold"),
                                     command=lambda u=cred['user']: self.copy_to_clipboard(u, "Username"))
        copy_user_btn.pack(side="left", padx=5)

        copy_pass_btn = ctk.CTkButton(actions_frame, text="Pass", width=80, height=35,
                                     fg_color=ACCENT_COLOR, hover_color="#7d3c98", font=("Outfit", 12, "bold"),
                                     command=lambda p=cred['password']: self.copy_to_clipboard(p, "Password"))
        copy_pass_btn.pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(actions_frame, text="🗑️", width=40, height=35, fg_color=("#ffdddd", "#442222"), hover_color="#c0392b",
                               command=lambda i=index: self.delete_credential(i))
        del_btn.pack(side="left", padx=5)

    def copy_to_clipboard(self, text, label):
        pyperclip.copy(text)
        # We could add a temporary label or toast here
        print(f"{label} copied to clipboard!")

    def delete_credential(self, index):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this credential?"):
            self.vault_manager.delete_credential(index)
            self.refresh_vault_list()

    def change_appearance_mode(self, new_mode: str):
        mode = new_mode.lower()
        ctk.set_appearance_mode(mode)
        CONFIG["appearance"] = mode
        save_config(CONFIG)

    def toggle_visibility(self, entry, button):
        if entry.cget("show") == "*":
            entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            entry.configure(show="*")
            button.configure(text="👁️")

    def show_add_dialog(self):
        dialog = AddCredentialDialog(self)
        self.wait_window(dialog)
        self.refresh_vault_list()

class AddCredentialDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add New Credential")
        self.geometry("450x650") # Increased height for generator
        self.resizable(False, False)
        
        # Generator state
        self.show_gen_options = False
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        self.configure(fg_color=BG_COLOR)
        ctk.CTkLabel(self, text="New Credential", font=("Outfit", 24, "bold"), text_color=TEXT_COLOR).pack(pady=30)

        self.site_entry = ctk.CTkEntry(self, placeholder_text="Service Name", width=350, height=45, fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.site_entry.pack(pady=10)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username / Email", width=350, height=45, fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.user_entry.pack(pady=10)

        # Password row with eye and generate button
        pass_row = ctk.CTkFrame(self, fg_color="transparent")
        pass_row.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(pass_row, placeholder_text="Password", show="*", width=240, height=45, fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR)
        self.pass_entry.pack(side="left", padx=(0, 5))

        self.pass_eye_btn = ctk.CTkButton(pass_row, text="👁️", width=45, height=45, 
                                         command=lambda: self.toggle_visibility(self.pass_entry, self.pass_eye_btn),
                                         fg_color=INPUT_BG, hover_color=ACCENT_COLOR, text_color=TEXT_COLOR)
        self.pass_eye_btn.pack(side="left", padx=(0, 5))

        self.gen_toggle_btn = ctk.CTkButton(pass_row, text="🧙", width=45, height=45, 
                                           command=self.toggle_generator,
                                           fg_color=ACCENT_COLOR, hover_color="#7d3c98")
        self.gen_toggle_btn.pack(side="left")

        # Strength Meter
        self.strength_container = ctk.CTkFrame(self, fg_color="transparent")
        self.strength_container.pack(pady=(0, 10), padx=50, fill="x")
        
        self.strength_bar = ctk.CTkProgressBar(self.strength_container, width=250, height=8)
        self.strength_bar.set(0)
        self.strength_bar.pack(side="left", padx=(0, 10))
        
        self.strength_label = ctk.CTkLabel(self.strength_container, text="", font=("Outfit", 11))
        self.strength_label.pack(side="left")
        
        self.pass_entry.bind("<KeyRelease>", lambda e: self.update_strength_indicator())

        # Generator Options Frame (initially hidden)
        self.gen_frame = ctk.CTkFrame(self, border_width=1, border_color="#8e44ad")
        
        ctk.CTkLabel(self.gen_frame, text="Password Generator Settings", font=("Outfit", 12, "bold")).pack(pady=10)
        
        # Length
        len_frame = ctk.CTkFrame(self.gen_frame, fg_color="transparent")
        len_frame.pack(fill="x", padx=20)
        ctk.CTkLabel(len_frame, text="Length:").pack(side="left")
        self.len_slider = ctk.CTkSlider(len_frame, from_=8, to=32, number_of_steps=24, width=200)
        self.len_slider.set(16)
        self.len_slider.pack(side="right")
        self.len_label = ctk.CTkLabel(len_frame, text="16")
        self.len_label.pack(side="right", padx=10)
        self.len_slider.configure(command=lambda v: self.len_label.configure(text=str(int(v))))

        # Switches
        self.upper_switch = ctk.CTkSwitch(self.gen_frame, text="Uppercase (A-Z)")
        self.upper_switch.select()
        self.upper_switch.pack(pady=5, padx=20, anchor="w")

        self.num_switch = ctk.CTkSwitch(self.gen_frame, text="Numbers (0-9)")
        self.num_switch.select()
        self.num_switch.pack(pady=5, padx=20, anchor="w")

        self.sym_switch = ctk.CTkSwitch(self.gen_frame, text="Symbols (!@#...)")
        self.sym_switch.select()
        self.sym_switch.pack(pady=5, padx=20, anchor="w")

        self.do_gen_btn = ctk.CTkButton(self.gen_frame, text="Generate & Fill", 
                                       command=self.generate_and_fill,
                                       fg_color="#8e44ad", hover_color="#7d3c98")
        self.do_gen_btn.pack(pady=15)

        # Main Save Button
        self.save_btn = ctk.CTkButton(self, text="Save Credential", command=self.save, width=350, height=45, font=("Outfit", 14, "bold"))
        self.save_btn.pack(pady=30)

    def toggle_generator(self):
        if self.show_gen_options:
            self.gen_frame.pack_forget()
            self.show_gen_options = False
        else:
            self.gen_frame.pack(pady=10, padx=20, fill="x", before=self.save_btn)
            self.show_gen_options = True

    def toggle_visibility(self, entry, button):
        if entry.cget("show") == "*":
            entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            entry.configure(show="*")
            button.configure(text="👁️")

    def generate_and_fill(self):
        length = int(self.len_slider.get())
        password = generate_secure_password(
            length=length,
            use_upper=self.upper_switch.get(),
            use_digits=self.num_switch.get(),
            use_symbols=self.sym_switch.get()
        )
        self.pass_entry.delete(0, 'end')
        self.pass_entry.insert(0, password)
        # Update strength meter
        self.update_strength_indicator()
        # Optionally show password briefly or just let user know
        self.pass_entry.configure(show="")
        self.after(2000, lambda: self.pass_entry.configure(show="*"))

    def update_strength_indicator(self):
        password = self.pass_entry.get()
        score, label, color = check_password_strength(password)
        
        # Update progress bar (score is 0-4, progress is 0.0-1.0)
        self.strength_bar.set(score / 4 if password else 0)
        self.strength_bar.configure(progress_color=color)
        
        # Update label
        self.strength_label.configure(text=label, text_color=color)

    def save(self):
        site = self.site_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()

        if not all([site, user, password]):
            messagebox.showwarning("Missing Info", "All fields are required.")
            return

        self.parent.vault_manager.add_credential(site, user, password)
        self.destroy()

if __name__ == "__main__":
    app = HermitVaultApp()
    app.mainloop()
