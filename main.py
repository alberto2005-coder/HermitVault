import customtkinter as ctk
import pyperclip
import os
from PIL import Image, ImageTk
from vault_storage import VaultManager
from crypto_logic import generate_secure_password, check_password_strength
from tkinter import messagebox

# Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HermitVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HermitVault - Secure Password Manager")
        self.geometry("800x600")
        
        # Load Logo
        self.load_logo()
        
        self.vault_manager = VaultManager()
        
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
        
        exists = self.vault_manager.vault_exists()
        title_text = "Unlock Your Vault" if exists else "Create Your Vault"
        button_text = "Unlock" if exists else "Setup Vault"

        frame = ctk.CTkFrame(self.container, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.logo_img:
            ctk.CTkLabel(frame, image=self.logo_img, text="").pack(pady=(30, 0))

        ctk.CTkLabel(frame, text="HermitVault", font=("Outfit", 28, "bold")).pack(pady=(10, 10), padx=50)
        ctk.CTkLabel(frame, text=title_text, font=("Outfit", 16)).pack(pady=(0, 20))

        # Container for entry and eye button to keep them centered together
        pass_container = ctk.CTkFrame(frame, fg_color="transparent")
        pass_container.pack(pady=10)

        self.password_entry = ctk.CTkEntry(pass_container, placeholder_text="Master Password", show="*", width=250, height=45)
        self.password_entry.pack(side="left", padx=(0, 5))
        self.password_entry.bind("<Return>", lambda e: self.on_login())

        self.eye_btn = ctk.CTkButton(pass_container, text="👁️", width=45, height=45, 
                                     command=lambda: self.toggle_visibility(self.password_entry, self.eye_btn),
                                     fg_color="transparent", hover_color="#34495e")
        self.eye_btn.pack(side="left")

        # Master Strength Meter
        self.m_strength_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.m_strength_container.pack(pady=(0, 10), padx=50, fill="x")
        
        self.m_strength_bar = ctk.CTkProgressBar(self.m_strength_container, width=200, height=6)
        self.m_strength_bar.set(0)
        self.m_strength_bar.pack(side="left", padx=(0, 10))
        
        self.m_strength_label = ctk.CTkLabel(self.m_strength_container, text="", font=("Outfit", 10))
        self.m_strength_label.pack(side="left")
        
        self.password_entry.bind("<KeyRelease>", lambda e: self.update_master_strength_indicator())

        login_button = ctk.CTkButton(frame, text=button_text, command=self.on_login, width=300, height=45, font=("Outfit", 14, "bold"))
        login_button.pack(pady=(20, 30), padx=50)

        if not exists:
            ctk.CTkLabel(frame, text="Note: Your password must be 'Good' or better.\n(8+ chars, upper, lower, numbers/symbols)", font=("Outfit", 11), text_color="gray").pack(pady=(0, 20))

    def update_master_strength_indicator(self):
        password = self.password_entry.get()
        score, label, color = check_password_strength(password)
        self.m_strength_bar.set(score / 4 if password else 0)
        self.m_strength_bar.configure(progress_color=color)
        self.m_strength_label.configure(text=label, text_color=color)

    def toggle_visibility(self, entry, button):
        if entry.cget("show") == "*":
            entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            entry.configure(show="*")
            button.configure(text="👁️")

    def on_login(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Empty Password", "Please enter a master password.")
            return

        if self.vault_manager.vault_exists():
            if self.vault_manager.unlock_vault(password):
                self.show_vault_screen()
            else:
                messagebox.showerror("Error", "Invalid Master Password")
        else:
            score, label, _ = check_password_strength(password)
            if score < 3:
                messagebox.showwarning("Weak Password", f"Vault password is '{label}'. It must be at least 'Good' for your safety.")
                return
            
            self.vault_manager.initialize_vault(password)
            messagebox.showinfo("Success", "Vault created successfully!")
            self.show_vault_screen()

    def show_vault_screen(self):
        self.clear_container()
        
        # Sidebar/Header
        header = ctk.CTkFrame(self.container, height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        
        if self.logo_small:
            ctk.CTkLabel(header, image=self.logo_small, text="").pack(side="left", padx=(30, 5), pady=20)
            ctk.CTkLabel(header, text="HermitVault", font=("Outfit", 24, "bold")).pack(side="left", pady=20)
        else:
            ctk.CTkLabel(header, text="🛡️ HermitVault", font=("Outfit", 24, "bold")).pack(side="left", padx=30, pady=20)
        
        add_btn = ctk.CTkButton(header, text="+ Add Credential", command=self.show_add_dialog, width=150, height=35, font=("Outfit", 13, "bold"))
        add_btn.pack(side="right", padx=30, pady=20)

        # Scrollable area
        self.scroll_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh_vault_list()

    def refresh_vault_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        credentials = self.vault_manager.get_credentials()
        
        if not credentials:
            ctk.CTkLabel(self.scroll_frame, text="No credentials saved yet.\nClick '+ Add Credential' to start.", font=("Outfit", 14), text_color="gray").pack(pady=100)
            return

        for i, cred in enumerate(credentials):
            self.create_credential_card(i, cred)

    def create_credential_card(self, index, cred):
        card = ctk.CTkFrame(self.scroll_frame, height=80)
        card.pack(fill="x", pady=5, padx=5)

        # Info Layout
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=20, fill="y")

        ctk.CTkLabel(info_frame, text=cred['site'], font=("Outfit", 16, "bold"), anchor="w").pack(pady=(10, 0), fill="x")
        ctk.CTkLabel(info_frame, text=f"User: {cred['user']}", font=("Outfit", 12), text_color="gray", anchor="w").pack(pady=(0, 10), fill="x")

        # Actions Layout
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=20)

        copy_user_btn = ctk.CTkButton(actions_frame, text="Copy User", width=100, height=30, 
                                     fg_color="#34495e", hover_color="#2c3e50",
                                     command=lambda u=cred['user']: self.copy_to_clipboard(u, "Username"))
        copy_user_btn.pack(side="left", padx=5)

        copy_pass_btn = ctk.CTkButton(actions_frame, text="Copy Pass", width=100, height=30,
                                     command=lambda p=cred['password']: self.copy_to_clipboard(p, "Password"))
        copy_pass_btn.pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(actions_frame, text="🗑️", width=40, height=30, fg_color="#c0392b", hover_color="#a93226",
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
        ctk.CTkLabel(self, text="New Credential", font=("Outfit", 20, "bold")).pack(pady=20)

        self.site_entry = ctk.CTkEntry(self, placeholder_text="Website / Service (e.g. Google)", width=350, height=40)
        self.site_entry.pack(pady=10)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username / Email", width=350, height=40)
        self.user_entry.pack(pady=10)

        # Password row with eye and generate button
        pass_row = ctk.CTkFrame(self, fg_color="transparent")
        pass_row.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(pass_row, placeholder_text="Password", show="*", width=250, height=40)
        self.pass_entry.pack(side="left", padx=(0, 5))

        self.pass_eye_btn = ctk.CTkButton(pass_row, text="👁️", width=40, height=40, 
                                         command=lambda: self.toggle_visibility(self.pass_entry, self.pass_eye_btn),
                                         fg_color="transparent", hover_color="#34495e")
        self.pass_eye_btn.pack(side="left", padx=(0, 5))

        self.gen_toggle_btn = ctk.CTkButton(pass_row, text="🧙", width=40, height=40, 
                                           command=self.toggle_generator,
                                           fg_color="#8e44ad", hover_color="#7d3c98")
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
