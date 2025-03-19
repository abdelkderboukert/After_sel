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

        # Navigation Bar
        self.navbar_frame = ttk.Frame(self.main_frame)
        self.navbar_frame.pack(side=tk.TOP, fill=tk.X)

        # Buttons in the navigation bar
        ttk.Button(self.navbar_frame, text="Add Client", command=self.show_add_client).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(self.navbar_frame, text="Add Machine", command=self.show_add_machine).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(self.navbar_frame, text="Add Spare Part", command=self.show_add_spare_part).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(self.navbar_frame, text="Add Invoice", command=self.show_add_invoice).pack(side=tk.LEFT, padx=10, pady=5)

        # Frame for forms
        self.form_frame = ttk.Frame(self.main_frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for invoice list
        self.invoice_frame = ttk.Frame(self.main_frame)
        self.invoice_frame.pack(fill=tk.BOTH, expand=True)

        self.invoice_listbox = tk.Listbox(self.invoice_frame, height=10)
        self.invoice_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.refresh_invoice_list()  # Load invoices into the listbox

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

    def refresh_invoice_list(self):
        """Refresh the invoice list."""
        self.invoice_listbox.delete(0, tk.END)  # Clear the listbox
        self.cursor.execute("SELECT id, client_id, invoice_date FROM Invoice")
        invoices = self.cursor.fetchall()
        for inv in invoices:
            self.invoice_listbox.insert(tk.END, f"Invoice ID: {inv[0]}, Client ID: {inv[1]}, Date: {inv[2]}")

    def show_add_client(self):
        self.clear_form_frame()
        self.add_client()

    def show_add_machine(self):
        self.clear_form_frame()
        self.add_machine()

    def show_add_spare_part(self):
        self.clear_form_frame()
        self.add_spare_part()

    def show_add_invoice(self):
        self.clear_form_frame()
        self.add_invoice()

    def clear_form_frame(self):
        """Clear the form frame before displaying a new form."""
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def add_client(self):
        fields = ["Registre Comars", "NIF", "NIS", "AI"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
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
                self.refresh_invoice_list()  # Refresh the invoice list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(self.form_frame, text="Save", command=save_client).grid(row=len(fields), columnspan=2, pady=10)

    def add_machine(self):
        ttk.Label(self.form_frame, text="Machine Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(self.form_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.form_frame, text="Machine Model:").grid(row=1, column=0, padx=5, pady=5)
        model_entry = ttk.Entry(self.form_frame)
        model_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.form_frame, text="Machine Company:").grid(row=2, column=0, padx=5, pady=5)
        company_entry = ttk.Entry(self.form_frame)
        company_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.form_frame, text="Machine NS:").grid(row=3, column=0, padx=5, pady=5)
        ns_entry = ttk.Entry(self.form_frame)
        ns_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def save_machine():
            try:
                self.cursor.execute(
                    "INSERT INTO Machine (name, model, company, ns) VALUES (?, ?, ?, ?)",
                    (name_entry.get(), model_entry.get(), company_entry.get(), ns_entry.get())
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Machine added successfully!")
                self.refresh_invoice_list()  # Refresh the invoice list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(self.form_frame, text="Save", command=save_machine).grid(row=4, columnspan=2, pady=10)

    def add_spare_part(self):
        fields = ["Name", "Serial Number"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Populate machine dropdown for spare part
        ttk.Label(self.form_frame, text="Select Machine:").grid(row=2, column=0, padx=5, pady=5)
        machine_var = tk.StringVar()
        machine_combo = ttk.Combobox(self.form_frame, textvariable=machine_var)
        machine_combo.grid(row=2, column=1, padx=5, pady=5)
        self.cursor.execute("SELECT id, name FROM Machine")
        machines = self.cursor.fetchall()
        machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in machines]

        def save_spare_part():
            machine_id = machine_var.get().split(" - ")[0]
            data = [entries[field].get() for field in fields]  # Get data from entries
            try:
                self.cursor.execute(
                    "INSERT INTO SparePart (name, serial_number, machine_id) VALUES (?, ?, ?)",
                    (data[0], data[1], machine_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Spare part added successfully!")
                self.refresh_invoice_list()  # Refresh the invoice list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(self.form_frame, text="Save", command=save_spare_part).grid(row=3, columnspan=2, pady=10)

    def add_invoice(self):
        # Get clients for dropdown
        self.cursor.execute("SELECT id, registre_comars FROM Client")
        clients = self.cursor.fetchall()
        
        ttk.Label(self.form_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5)
        client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(self.form_frame, textvariable=client_var, 
                                        values=[f"{c[0]} - {c[1]}" for c in clients])
        self.client_combo.grid(row=0, column=1, padx=5, pady=5)

        fields = ["Date (YYYY-MM-DD)", "Description", "User ", "Hours"]
        entries = {}
        
        for i, field in enumerate(fields, start=1):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Set today's date as the default value for the date entry
        today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date in YYYY-MM-DD format
        entries["Date (YYYY-MM-DD)"].insert(0, today_date)  # Set the default date

        # Get machines for combo box
        self.cursor.execute("SELECT id, name FROM Machine")
        machines = self.cursor.fetchall()
        
        ttk.Label(self.form_frame, text="Machine:").grid(row=5, column=0, padx=5, pady=5)
        Machine_var = tk.StringVar()
        self.Machine_combo = ttk.Combobox(self.form_frame, textvariable=Machine_var, 
                                        values=[f"{c[0]} - {c[1]}" for c in machines])
        self.Machine_combo.grid(row=5, column=1, padx=5, pady=5)
        self.Machine_combo.bind("<<ComboboxSelected>>", self.on_machine_select)  # Bind selection event

        # Spare parts list
        ttk.Label(self.form_frame, text="Select Spare Parts:").grid(row=6, column=0, padx=5, pady=5)
        self.spare_part_listbox = tk.Listbox(self.form_frame, selectmode=tk.MULTIPLE, height=5)
        self.spare_part_listbox.grid(row=6, column=1, padx=5, pady=5)

        self.refresh_spare_part_list()  # Populate the listbox with spare parts

        def save_invoice():
            client_id = self.client_combo.get().split(" - ")[0]
            selected_machine = self.Machine_combo.get().split(" - ")[0]
            selected_spare_parts_indices = self.spare_part_listbox.curselection()  # Get selected spare parts
            if not selected_machine:
                messagebox.showerror("Error", "Please select a machine.")
                return
            
            try:
                # Insert the task
                self.cursor.execute(
                    "INSERT INTO Task (description, date, user, hours) VALUES (?, ?, ?, ?)",
                    (entries["Description"].get(), entries["Date (YYYY-MM-DD)"].get(), entries["User "].get(), entries["Hours"].get())
                )
                self.conn.commit()
                
                # Get the ID of the newly created task
                task_id = self.cursor.lastrowid  # Store the new task ID in variable task_id
                
                # Insert the machine-task relationship (only one machine)
                self.cursor.execute(
                    "INSERT INTO TaskMachine (task_id, machine_id) VALUES (?, ?)",
                    (task_id, selected_machine)
                )
                
                # Insert the spare part-task relationships
                for index in selected_spare_parts_indices:
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
                self.refresh_invoice_list()  # Refresh the invoice list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add task or invoice: {str(e)}")

        # Create the button with the custom style
        ttk.Button(self.form_frame, text="Save", command=save_invoice).grid(row=11, columnspan=2, pady=10)

    def on_machine_select(self, event):
        """Update the spare part list based on the selected machine."""
        selected_machine = self.Machine_combo.get()  # Get the selected machine
        if selected_machine:
            machine_id = selected_machine.split(" - ")[0]  # Extract machine ID
            self.selected_machine_ids = [machine_id]  # Update the selected machine IDs
            self.refresh_spare_part_list()  # Refresh spare part list based on selected machine

    def refresh_spare_part_list(self):
        """Refresh the spare part list based on the selected machines."""
        if self.spare_part_listbox and hasattr(self, 'selected_machine_ids'):
            self.spare_part_listbox.delete(0, tk.END)  # Clear the listbox
            # Create a placeholder for the query
            query = "SELECT id, name FROM SparePart WHERE machine_id IN ({})".format(
                ','.join('?' for _ in self.selected_machine_ids)
            )
            self.cursor.execute(query, self.selected_machine_ids)
            spare_parts = self.cursor.fetchall()
            for sp in spare_parts:
                self.spare_part_listbox.insert(tk.END, f"{sp[0]} - {sp[1]}")  # Add spare parts to the listbox

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()