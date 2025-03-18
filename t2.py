import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Management System")
        
        # Initialize database
        self.conn = sqlite3.connect('invoice.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        ttk.Button(self.main_frame, text="Add Client", command=self.add_client).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(self.main_frame, text="Add Machine", command=self.add_machine).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.main_frame, text="Add Task", command=self.add_task).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(self.main_frame, text="Add Invoice", command=self.add_invoice).grid(row=0, column=3, padx=10, pady=5)

        self.client_combo = None  # Initialize client_combo to None
        self.machine_combo = None  # Initialize machine_combo to None

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Client (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            registre_comars TEXT NOT NULL,
                            nif TEXT NOT NULL,
                            nis TEXT NOT NULL,
                            ai TEXT NOT NULL)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Machine (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            model TEXT NOT NULL,
                            company TEXT NOT NULL,
                            ns INTEGER NOT NULL)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Invoice (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            client_id INTEGER NOT NULL,
                            invoice_date DATE NOT NULL,
                            task_id INTEGER NOT NULL,
                            FOREIGN KEY(client_id) REFERENCES Client(id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Task (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            machine_id INTEGER NOT NULL,
                            description TEXT,
                            date DATE NOT NULL,
                            user TEXT NOT NULL,
                            hours INTEGER NOT NULL,
                            FOREIGN KEY(machine_id) REFERENCES Machine(id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Piece (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            reference TEXT NOT NULL,
                            content INTEGER NOT NULL)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS TaskPiece (
                            task_id INTEGER NOT NULL,
                            piece_id INTEGER NOT NULL,
                            PRIMARY KEY(task_id, piece_id),
                            FOREIGN KEY(task_id) REFERENCES Task(id),
                            FOREIGN KEY(piece_id) REFERENCES Piece(id))""")
        
        self.conn.commit()

    def refresh_client_list(self):
        """Refresh the client list in the add_invoice window."""
        if self.client_combo:
            self.cursor.execute("SELECT id, registre_comars FROM Client")
            clients = self.cursor.fetchall()
            self.client_combo['values'] = [f"{c[0]} - {c[1]}" for c in clients]
            if clients:
                self.client_combo.set('')  # Clear the selection if there are clients

    def refresh_machine_list(self):
        """Refresh the machine list in the add_invoice window."""
        if self.machine_combo:
            self.cursor.execute("SELECT id, name FROM Machine")
            machines = self.cursor.fetchall()
            self.machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in machines]
            if machines:
                self.machine_combo.set('')  # Clear the selection if there are machines

    def add_client(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Client")
        
        fields = ["Registre Comars", "NIF", "NIS", "AI"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)
        
        def save_client():
            data = [entries[field].get() for field in fields]
            try:
                self.cursor.execute(
                    "INSERT INTO Client (registre_comars, nif, nis, ai) VALUES (?, ?, ?, ?)",
                    data
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Client added successfully!")
                self.refresh_client_list()  # Refresh the client list
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(window, text="Save", command=save_client).grid(row=len(fields), columnspan=2, pady=10)

    def add_machine(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Machine")
        
        ttk.Label(window, text="Machine Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(window)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine model:").grid(row=2, column=0, padx=5, pady=5)
        model_entry = ttk.Entry(window)
        model_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine company:").grid(row=3, column=0, padx=5, pady=5)
        company_entry = ttk.Entry(window)
        company_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine ns:").grid(row=4, column=0, padx=5, pady=5)
        ns_entry = ttk.Entry(window)
        ns_entry.grid(row=4, column=1, padx=5, pady=5)
        def save_machine():
            try:
                self.cursor.execute(
                    "INSERT INTO Machine (name, model, company, ns) VALUES (?, ?, ?, ?)",
                    (name_entry.get(), model_entry.get(), company_entry.get(), ns_entry.get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Machine added successfully!")
                self.refresh_machine_list()  # Refresh the machine list
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(window, text="Save", command=save_machine).grid(row=5, columnspan=2, pady=10)

    def add_task(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Task")

        ttk.Label(window, text="Machine Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(window)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine model:").grid(row=2, column=0, padx=5, pady=5)
        model_entry = ttk.Entry(window)
        model_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine company:").grid(row=3, column=0, padx=5, pady=5)
        company_entry = ttk.Entry(window)
        company_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(window, text="Machine ns:").grid(row=4, column=0, padx=5, pady=5)
        ns_entry = ttk.Entry(window)
        ns_entry.grid(row=4, column=1, padx=5, pady=5)

        def save_machine():
            try:
                self.cursor.execute(
                    "INSERT INTO Machine (name, model, company, ns) VALUES (?, ?, ?, ?)",
                    (name_entry.get(), model_entry.get(), company_entry.get(), ns_entry.get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Machine added successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(window, text="Save", command=save_machine).grid(row=5, columnspan=2, pady=10)

        # Get machines for dropdown
        self.cursor.execute("SELECT id, name FROM Machine")
        machines = self.cursor.fetchall()

        ttk.Label(window, text="Machine:").grid(row=6, column=0, padx=5, pady=5)
        machine_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(window, textvariable=machine_var, 
                                           values=[f"{m[0]} - {m[1]}" for m in machines])
        self.machine_combo.grid(row=6, column=1, padx=5, pady=5)

        # Set default to "None" if no machines exist
        if not machines:
            self.machine_combo.set("None")
        else:
            self.machine_combo.set('')  # Clear the selection if there are machines

        fields = ["Description", "Date (YYYY-MM-DD)", "User  ", "Hours"]
        entries = {}
        
        for i, field in enumerate(fields, start=7):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Set today's date as the default value for the date entry
        today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date in YYYY-MM-DD format
        entries["Date (YYYY-MM-DD)"].insert(0, today_date)  # Set the default date

        def save_task():
            machine_id = self.machine_combo.get().split(" - ")[0]
            if machine_id == "None":
                machine_id = None  # Handle the case where "None" is selected
            try:
                self.cursor.execute(
                    """INSERT INTO Task (machine_id, description, date, user, hours)
                    VALUES (?, ?, ?, ?, ?)""",
                    (machine_id, entries["Description"].get(), 
                     entries["Date (YYYY-MM-DD)"].get(),
                     entries["User  "].get(), entries["Hours"].get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Task added successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(window, text="Save Task", command=save_task).grid(row=11, columnspan=2, pady=10)

    def add_invoice(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Invoice")
        
        # Get clients for dropdown
        self.cursor.execute("SELECT id, registre_comars FROM Client")
        clients = self.cursor.fetchall()
        
        ttk.Label(window, text="Client:").grid(row=0, column=0, padx=5, pady=5)
        Client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(window, textvariable=Client_var, 
                                           values=[f"{c[0]} - {c[1]}" for c in clients])
        self.client_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(window, text="Add Client", command=self.add_client).grid(row=0, column=2, padx=10, pady=5)

        fields = ["Date (YYYY-MM-DD)"]
        entries = {}
        
        for i, field in enumerate(fields, start=1):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Set today's date as the default value for the date entry
        today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date in YYYY-MM-DD format
        entries["Date (YYYY-MM-DD)"].insert(0, today_date)  # Set the default date

        # ttk.Label(window, text="Machine:").grid(row=5, column=0, padx=5, pady=5)
        # machine_var = tk.StringVar()
        # self.machine_combo = ttk.Combobox(window, textvariable=machine_var)
        # self.machine_combo.grid(row=5, column=1, padx=5, pady=5)

        # ttk.Button(window, text="Add Client", command=self.add_machine).grid(row=5, column=2, padx=10, pady=5)
        # Get clients for dropdown
        self.cursor.execute("SELECT id, name FROM Machine")
        clients = self.cursor.fetchall()
        
        ttk.Label(window, text="Machine:").grid(row=2, column=0, padx=5, pady=5)
        Client_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(window, textvariable=Client_var, 
                                           values=[f"{c[0]} - {c[1]}" for c in clients])
        self.machine_combo.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(window, text="Add machine", command=self.add_machine).grid(row=2, column=2, padx=10, pady=5)

        fields = ["Description", "User  ", "Hours"]
        entries = {}
        
        for i, field in enumerate(fields, start=6):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        def save_invoice():
            client_id = self.client_combo.get().split(" - ")[0]
            machine_id = self.machine_combo.get().split (" - ")[0]
            try:
                self.cursor.execute(
                    """INSERT INTO Invoice (client_id, invoice_date)
                    VALUES (?, ?)""",
                    (client_id, entries["Date (YYYY-MM-DD)"].get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Invoice added successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(window, text="Save", command=save_invoice).grid(row=10, columnspan=2, pady=10)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()