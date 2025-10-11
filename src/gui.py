import tkinter as tk
from tkinter import filedialog, messagebox
from rsa import generate_keys, sign, verify
from hashing import hash_file
import os
import pickle

class DigitalSignatureApp:
    def __init__(self, master):
        self.master = master
        master.title("Digital Signature System")
        master.geometry("500x350")
        
        # Keys
        self.public_key = None
        self.private_key = None
        self.keys_folder = "keys"
        os.makedirs(self.keys_folder, exist_ok=True)
        
        # Try to load existing keys
        self.load_keys()
        
        # Labels
        self.label = tk.Label(master, text="Digital Signature System", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # Buttons
        self.key_button = tk.Button(master, text="Generate Keys", width=25, command=self.generate_keys)
        self.key_button.pack(pady=5)
        
        self.sign_button = tk.Button(master, text="Sign File", width=25, command=self.sign_file)
        self.sign_button.pack(pady=5)
        
        self.verify_button = tk.Button(master, text="Verify File", width=25, command=self.verify_file)
        self.verify_button.pack(pady=5)
        
        # Output
        self.output_text = tk.Text(master, height=10, width=60)
        self.output_text.pack(pady=10)
    
    def generate_keys(self):
        self.public_key, self.private_key = generate_keys()
        self.save_keys()
        self.output_text.insert(tk.END, f"Keys generated!\nPublic Key: {self.public_key}\nPrivate Key: {self.private_key}\n\n")
    
    def save_keys(self):
        with open(os.path.join(self.keys_folder, "public_key.pkl"), "wb") as f:
            pickle.dump(self.public_key, f)
        with open(os.path.join(self.keys_folder, "private_key.pkl"), "wb") as f:
            pickle.dump(self.private_key, f)
    
    def load_keys(self):
        try:
            with open(os.path.join(self.keys_folder, "public_key.pkl"), "rb") as f:
                self.public_key = pickle.load(f)
            with open(os.path.join(self.keys_folder, "private_key.pkl"), "rb") as f:
                self.private_key = pickle.load(f)
            print("Keys loaded successfully.")
        except FileNotFoundError:
            print("No existing keys found. Generate keys first.")
    
    def sign_file(self):
        if self.private_key is None:
            messagebox.showerror("Error", "Generate keys first!")
            return
        
        file_path = filedialog.askopenfilename(title="Select file to sign")
        if not file_path:
            return
        
        file_hash = hash_file(file_path)
        signature = sign(file_hash, self.private_key)
        self.output_text.insert(tk.END, f"File signed!\nSignature: {signature}\n\n")
        
        # Save signature in a file
        with open(file_path + ".sig", "w") as f:
            f.write(str(signature))
    
    def verify_file(self):
        if self.public_key is None:
            messagebox.showerror("Error", "Generate keys first!")
            return
        
        file_path = filedialog.askopenfilename(title="Select file to verify")
        if not file_path:
            return
        
        sig_path = filedialog.askopenfilename(title="Select signature file (.sig)")
        if not sig_path:
            return
        
        file_hash = hash_file(file_path)
        file_hash_mod = file_hash % self.public_key[1]
        try:
            with open(sig_path, "r") as f:
                signature = int(f.read().strip())
        except:
            messagebox.showerror("Error", "Invalid signature file!")
            return
        
        verified_hash_mod = verify(signature, self.public_key)
        if verified_hash_mod == file_hash_mod:
            messagebox.showinfo("Verification", "Success! File is authentic.")
            self.output_text.insert(tk.END, f"Verification Success: File is authentic\n\n")
        else:
            messagebox.showwarning("Verification", "Failed! File has been tampered.")
            self.output_text.insert(tk.END, f"Verification Failed: File has been tampered\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()
