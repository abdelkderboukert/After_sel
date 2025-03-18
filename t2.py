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
        ttk.Button(self.main_frame, text="Add Spare Part", command=self.add_spare_part).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(self.main_frame, text="Add Invoice", command=self.add_invoice).grid(row=0, column=3, padx=10, pady=5)

        self.client_combo = None  # Initialize client_combo to None
        self.machine_listbox = None  # Initialize machine_listbox to None
        self.spare_part_listbox = None  # Initialize spare_part_listbox to None

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

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS SparePart (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            serial_number TEXT NOT NULL,
                            machine_id INTEGER NOT NULL,
                            FOREIGN KEY(machine_id) REFERENCES Machine(id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Invoice (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            client_id INTEGER NOT NULL,
                            invoice_date DATE NOT NULL,
                            task_id INTEGER NOT NULL,
                            FOREIGN KEY(client_id) REFERENCES Client(id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Task (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            description TEXT,
                            date DATE NOT NULL,
                            user TEXT NOT NULL,
                            hours INTEGER NOT NULL)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS TaskMachine (
                            task_id INTEGER NOT NULL,
                            machine_id INTEGER NOT NULL,
                            PRIMARY KEY(task_id, machine_id),
                            FOREIGN KEY(task_id) REFERENCES Task(id),
                            FOREIGN KEY(machine_id) REFERENCES Machine(id))""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS TaskSparePart (
                            task_id INTEGER NOT NULL,
                            spare_part_id INTEGER NOT NULL,
                            PRIMARY KEY(task_id, spare_part_id),
                            FOREIGN KEY(task_id) REFERENCES Task(id),
                            FOREIGN KEY(spare_part_id) REFERENCES SparePart(id))""")
        
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
        if self.machine_listbox:
            self.cursor.execute("SELECT id, name FROM Machine")
            machines = self.cursor.fetchall()
            self.machine_listbox.delete(0, tk.END)  # Clear the listbox
            for m in machines:
                self.machine_listbox.insert(tk.END, f"{m[0]} - {m[1]}")  # Add machines to the listbox

    def refresh_spare_part_list(self):
        """Refresh the spare part list in the add_invoice window."""
        if self.spare_part_listbox:
            self.cursor.execute("SELECT id, name FROM SparePart")
            spare_parts = self.cursor.fetchall()
            self.spare_part_listbox.delete(0, tk.END)  # Clear the listbox
            for sp in spare_parts:
                self.spare_part_listbox.insert(tk.END, f"{sp[0]} - {sp[1]}")  # Add spare parts to the listbox

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

    def add_spare_part(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Spare Part")
        
        fields = ["Name", "Serial Number", "Machine ID"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Populate machine dropdown for spare part
        ttk.Label(window, text="Select Machine:").grid(row=3, column=0, padx=5, pady=5)
        machine_var = tk.StringVar()
        machine_combo = ttk.Combobox(window, textvariable=machine_var)
        machine_combo.grid(row=3, column=1, padx=5, pady=5)
        self.cursor.execute("SELECT id, name FROM Machine")
        machines = self.cursor.fetchall()
        machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in machines]

        def save_spare_part():
            machine_id = machine_var.get().split(" - ")[0]
            data = [entries[field].get() for field in fields[:-1]]  # Exclude machine ID from entries
            try:
                self.cursor.execute(
                    "INSERT INTO SparePart (name, serial_number, machine_id) VALUES (?, ?, ?)",
                    (data[0], data[1], machine_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Spare part added successfully!")
                self.refresh_spare_part_list()  # Refresh the spare part list
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(window, text="Save", command=save_spare_part).grid(row=4, columnspan=2, pady=10)

    def add_invoice(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Invoice")
        
        # Get clients for dropdown
        self.cursor.execute("SELECT id, registre_comars FROM Client")
        clients = self.cursor.fetchall()
        
        ttk.Label(window, text="Client:").grid(row=0, column=0, padx=5, pady=5)
        client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(window, textvariable=client_var, 
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

        # Get machines for listbox
        self.cursor.execute("SELECT id, name FROM Machine")
        machines = self.cursor.fetchall()
        
        ttk.Label(window, text="Select Machines:").grid(row=2, column=0, padx=5, pady=5)
        self.machine_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, height=5)
        self.machine_listbox.grid(row=2, column=1, padx=5, pady=5)
        self.refresh_machine_list()  # Populate the listbox with machines
        ttk.Button(window, text="Add Machine", command=self.add_machine).grid(row=2, column=2, padx=10, pady=5)

        # Spare parts list
        ttk.Label(window, text="Select Spare Parts:").grid(row=3, column=0, padx=5, pady=5)
        self.spare_part_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, height=5)
        self.spare_part_listbox.grid(row=3, column=1, padx=5, pady=5)
        self.refresh_spare_part_list()  # Populate the listbox with spare parts
        ttk.Button(window, text="Add Spare Part", command=self.add_spare_part).grid(row=3, column=2, padx=10, pady=5)

        fields = ["Description", "User   ", "Hours"]
        for i, field in enumerate(fields, start=4):
            ttk.Label(window, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        def save_invoice():
            client_id = self.client_combo.get().split(" - ")[0]
            selected_machines = self.machine_listbox.curselection()  # Get selected machines
            selected_spare_parts = self.spare_part_listbox.curselection()  # Get selected spare parts
            if not selected_machines:
                messagebox.showerror("Error", "Please select at least one machine.")
                return
            
            try:
                # Insert the task
                self.cursor.execute(
                    "INSERT INTO Task (description, date, user, hours) VALUES (?, ?, ?, ?)",
                    (entries["Description"].get(), entries["Date (YYYY-MM-DD)"].get(), entries["User   "].get(), entries["Hours"].get())
                )
                self.conn.commit()
                
                # Get the ID of the newly created task
                task_id = self.cursor.lastrowid  # Store the new task ID in variable task_id
                
                # Insert the machine-task relationships
                for index in selected_machines:
                    machine_id = self.machine_listbox.get(index).split(" - ")[0]
                    self.cursor.execute(
                        "INSERT INTO TaskMachine (task_id, machine_id) VALUES (?, ?)",
                        (task_id, machine_id)
                    )
                
                # Insert the spare part-task relationships
                for index in selected_spare_parts:
                    spare_part_id = self.spare_part_listbox.get(index).split(" - ")[0]
                    self.cursor.execute(
                        "INSERT INTO TaskSparePart (task_id, spare_part_id) VALUES (?, ?)",
                        (task_id, spare_part_id)
                    )
                
                self.conn.commit()
                
                # Insert the invoice
                self.cursor.execute(
                    """INSERT INTO Invoice (client_id, invoice_date, task_id)
                    VALUES (?, ?, ?)""",
                    (client_id, entries["Date (YYYY-MM-DD)"].get(), task_id)
                )
                self.conn.commit()
                
                messagebox.showinfo("Success", "Invoice added successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add task or invoice: {str(e)}")
            
        ttk.Button(window, text="Save", command=save_invoice).grid(row=10, columnspan=2, pady=10)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()