import os
import ttkbootstrap as tb
from database.db import initialize_database
from views.login_view import LoginView

def main():
    # Initialize SQLite database and tables, insert default admin
    initialize_database()
    
    # Initialize modern ttkbootstrap window
    root = tb.Window(themename="cosmo")
    root.title("Advanced Student Marks Analytics System")
    root.geometry("800x600")
    
    def on_closing():
        root.quit()
        root.destroy()
        os._exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
        
    app = LoginView(root)
    root.mainloop()

if __name__ == "__main__":
    main()
