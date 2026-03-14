import tkinter as tk
from tkinter import messagebox
from database import login_user
from menu import MainMenu

def start_login():
    login_win = tk.Tk()
    login_win.title("Staff Login - Bean & Brew")
    login_win.geometry("350x400")
    login_win.configure(bg='#f5f5f5')
    
    # Center the window
    login_win.eval('tk::PlaceWindow . center')
    
    # Logo/Title frame
    title_frame = tk.Frame(login_win, bg='#6F4E37', height=100)
    title_frame.pack(fill=tk.X)
    
    tk.Label(title_frame, text="Bean & Brew", 
            font=("Arial", 24, "bold"), 
            bg='#6F4E37', fg='white').pack(pady=30)
    
    # Login form
    form_frame = tk.Frame(login_win, bg='#f5f5f5', padx=40, pady=30)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(form_frame, text="Username:", bg='#f5f5f5', 
            font=("Arial", 11)).pack(anchor='w')
    
    ent_user = tk.Entry(form_frame, font=("Arial", 11), width=25)
    ent_user.pack(pady=(0, 15))
    ent_user.focus()
    
    tk.Label(form_frame, text="Password:", bg='#f5f5f5', 
            font=("Arial", 11)).pack(anchor='w')
    
    ent_pass = tk.Entry(form_frame, show="*", font=("Arial", 11), width=25)
    ent_pass.pack(pady=(0, 20))
    
    # Bind Enter key to login
    ent_pass.bind('<Return>', lambda e: handle_login())
    
    def handle_login():
        username = ent_user.get()
        password = ent_pass.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password")
            return
        
        user = login_user(username, password)
        if user:
            login_win.destroy()
            # Create main menu with user data
            root = tk.Tk()
            app = MainMenu(root, user)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            ent_pass.delete(0, tk.END)
    
    tk.Button(form_frame, text="Login", bg="#6F4E37", fg="white",
             font=("Arial", 11, "bold"), width=20,
             command=handle_login).pack(pady=10)
    
    # Demo credentials (remove in production)
    tk.Label(form_frame, text="Demo: admin/admin123", 
            font=("Arial", 8), fg="gray", bg='#f5f5f5').pack()
    
    login_win.mainloop()

if __name__ == "__main__":
    start_login()