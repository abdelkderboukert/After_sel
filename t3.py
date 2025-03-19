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

        # Frame for list display
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeviews for different data types
        self.create_treeviews()

        # Show invoices by default
        self.show_invoices()

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

    def create_treeviews(self):
        # Create Treeview for Invoices
        self.invoice_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Client", "machine", "user", "hour", "date"), show='headings')
        self.invoice_treeview.heading("ID", text="ID")
        self.invoice_treeview.heading("Client", text="Client")
        self.invoice_treeview.heading("machine", text="machine")
        self.invoice_treeview.heading("user", text="user")
        self.invoice_treeview.heading("hour", text="hour")
        self.invoice_treeview.heading("date", text="date")
        self.invoice_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview for Clients
        self.client_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Registre Comars", "NIF", "NIS", "AI"), show='headings')
        self.client_treeview.heading("ID", text="ID")
        self.client_treeview.heading("Registre Comars", text="Registre Comars")
        self.client_treeview.heading("NIF", text="NIF")
        self.client_treeview.heading("NIS", text="NIS")
        self.client_treeview.heading("AI", text="AI")
        self.client_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview for Machines
        self.machine_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Name", "Model", "Company", "NS"), show='headings')
        self.machine_treeview.heading("ID", text="ID")
        self.machine_treeview.heading("Name", text="Name")
        self.machine_treeview.heading("Model", text="Model")
        self.machine_treeview.heading("Company", text="Company")
        self.machine_treeview.heading("NS", text="NS")
        self.machine_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview for Spare Parts
        self.spare_part_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Name", "Serial Number", "Machine ID"), show='headings')
        self.spare_part_treeview.heading("ID", text="ID")
        self.spare_part_treeview.heading("Name", text="Name")
        self.spare_part_treeview.heading("Serial Number", text="Serial Number")
        self.spare_part_treeview.heading("Machine ID", text="Machine ID")
        self.spare_part_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Hide all treeviews initially
        self.hide_all_treeviews()

    def hide_all_treeviews(self):
        """Hide all treeviews."""
        self.invoice_treeview.pack_forget()
        self.client_treeview.pack_forget()
        self.machine_treeview.pack_forget()
        self.spare_part_treeview.pack_forget()

    def show_invoices(self):
        """Show the invoice treeview and refresh its data."""
        self.hide_all_treeviews()
        self.invoice_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_invoice_list()

    def show_machines(self):
        """Show the machine treeview and refresh its data."""
        self.hide_all_treeviews()
        self.machine_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_machine_list()

    def show_spare_parts(self):
        """Show the spare part treeview and refresh its data."""
        self.hide_all_treeviews()
        self.spare_part_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_spare_p_list()

    def show_clients(self):
        """Show the machine treeview and refresh its data."""
        self.hide_all_treeviews()
        self.client_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_client_list()

    def refresh_invoice_list(self):
        """Refresh the invoice list."""
        self.invoice_treeview.delete(*self.invoice_treeview.get_children())  # Clear the treeview
        self.cursor.execute("""
                                SELECT 
                                    Invoice.id,
                                    Client.nif,
                                    Machine.name AS machine_name,
                                    Task.user,
                                    Task.hours,
                                    Invoice.invoice_date
                                FROM 
                                    Invoice
                                JOIN 
                                    Client ON Invoice.client_id = Client.id
                                JOIN 
                                    Task ON Invoice.task_id = Task.id
                                JOIN 
                                    TaskMachine ON Task.id = TaskMachine.task_id
                                JOIN 
                                    Machine ON TaskMachine.machine_id = Machine.id
                            """)
        invoices = self.cursor.fetchall()
        for inv in invoices:
            self.invoice_treeview.insert("", tk.END, values=(inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]))
            # Create a button for each row
            button = tk.Button(self.root, text="Get ID", command=lambda id=inv[0]: self.get_id(id))
            button.pack(side=tk.TOP, anchor=tk.W)  # Adjust the position as needed

    def refresh_client_list(self):
        """Refresh the client list."""
        self.client_treeview.delete(*self.client_treeview.get_children())  # Clear the treeview
        self.cursor.execute("SELECT id, registre_comars, nif, nis, ai FROM Client")
        clients = self.cursor.fetchall()
        for client in clients:
            self.client_treeview.insert("", tk.END, values=client)

    def refresh_machine_list(self):
        """Refresh the machine list."""
        self.machine_treeview.delete(*self.machine_treeview.get_children())  # Clear the treeview
        self.cursor.execute("SELECT id, name, model, company, ns FROM Machine")
        machines = self.cursor.fetchall()
        for machine in machines:
            self.machine_treeview.insert("", tk.END, values=machine)

    def refresh_spare_p_list(self):
        """Refresh the spare part list with machine names."""
        self.spare_part_treeview.delete(*self.spare_part_treeview.get_children())  # Clear the treeview
        self.cursor.execute("""
            SELECT sp.id, sp.name, sp.serial_number, sp.machine_id 
            FROM SparePart sp
        """)
        spare_parts = self.cursor.fetchall()
        for sp in spare_parts:
            self.spare_part_treeview.insert("", tk.END, values=sp)

    def show_add_client(self):
        self.clear_form_frame()
        self.add_client()
        self.show_clients()  # Show the client list

    def show_add_machine(self):
        self.clear_form_frame()
        self.add_machine()
        self.show_machines()  # Show the machine list

    def show_add_spare_part(self):
        self.clear_form_frame()
        self.add_spare_part()
        self.show_spare_parts()  # Show the spare part list

    def show_add_invoice(self):
        self.clear_form_frame()
        self.add_invoice()
        self.show_invoices()  # Show the invoice list

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
                self.refresh_client_list()  # Refresh the client list
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
                self.refresh_machine_list()  # Refresh the machine list
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
        self.machine_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(self.form_frame, textvariable=self.machine_var)
        self.machine_combo.grid(row=2, column=1, padx=5, pady=5)

        # Fetch machines from the database
        self.cursor.execute("SELECT id, name FROM Machine")
        self.machines = self.cursor.fetchall()  # Store machines for autofill
        self.machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in self.machines]

        # Bind key release event for autofill
        self.machine_combo.bind("<KeyRelease>", self.on_machine_keyrelease)

        def save_spare_part():
            machine_id = self.machine_var.get().split(" - ")[0]
            data = [entries[field].get() for field in fields]  # Get data from entries
            try:
                self.cursor.execute(
                    "INSERT INTO SparePart (name, serial_number, machine_id) VALUES (?, ?, ?)",
                    (data[0], data[1], machine_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Spare part added successfully!")
                self.refresh_spare_p_list()  # Refresh the spare part list
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(self.form_frame, text="Save", command=save_spare_part).grid(row=3, columnspan=2, pady=10)

    def add_invoice(self):
        # Get clients for dropdown
        self.cursor.execute("SELECT id, registre_comars FROM Client")
        self.clients = self.cursor.fetchall()  # Store clients for autofill

        ttk.Label(self.form_frame, text="Client:").grid(row=0, column=0, padx=5, pady=5)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(self.form_frame, textvariable=self.client_var)
        self.client_combo.grid(row=0, column=1, padx=5, pady=5)
        self.client_combo['values'] = [f"{c[0]} - {c[1]}" for c in self.clients]
        self.client_combo.bind("<KeyRelease>", self.on_client_keyrelease)

        fields = ["Date (YYYY-MM-DD)", "Description", "User     ", "Hours"]
        entries = {}
        
        for i, field in enumerate(fields, start=1):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        # Set today's date as the default value for the date entry
        today_date = datetime.now().strftime("%Y-%m-%d")
        entries["Date (YYYY-MM-DD)"].insert(0, today_date)

        # Get machines for combo box
        self.cursor.execute("SELECT id, name FROM Machine")
        self.machines = self.cursor.fetchall()  # Store machines for autofill

        ttk.Label(self.form_frame, text="Machine:").grid(row=5, column=0, padx=5, pady=5)
        self.machine_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(self.form_frame, textvariable=self.machine_var)
        self.machine_combo.grid(row=5, column=1, padx=5, pady=5)
        self.machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in self.machines]
        self.machine_combo.bind("<KeyRelease>", self.on_machine_keyrelease)

        # Spare parts list
        ttk.Label(self.form_frame, text="Select Spare Parts:").grid(row=6, column=0, padx=5, pady=5)
        self.spare_part_listbox = tk.Listbox(self.form_frame, selectmode=tk.MULTIPLE, height=5)
        self.spare_part_listbox.grid(row=6, column=1, padx=5, pady=5)

        self.refresh_spare_part_list()

        def save_invoice():
            client_id = self.client_combo.get().split(" - ")[0]
            selected_machine = self.machine_combo.get().split(" - ")[0]
            selected_spare_parts_indices = self.spare_part_listbox.curselection()
            if not selected_machine:
                messagebox.showerror("Error", "Please select a machine.")
                return
            
            try:
                # Insert the task
                self.cursor.execute(
                    "INSERT INTO Task (description, date, user, hours) VALUES (?, ?, ?, ?)",
                    (entries["Description"].get(), entries["Date (YYYY-MM-DD)"].get(), entries["User     "].get(), entries["Hours"].get())
                )
                self.conn.commit()
                
                # Get the ID of the newly created task
                task_id = self.cursor.lastrowid
                
                # Insert the machine-task relationship
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
                self.refresh_invoice_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add task or invoice: {str(e)}")

        ttk.Button(self.form_frame, text="Save", command=save_invoice).grid(row=11, columnspan=2, pady=10)

    def on_client_keyrelease(self, event):
        current_input = self.client_var.get().lower()
        filtered_clients = [f"{c[0]} - {c[1]}" for c in self.clients if current_input in f"{c[0]} - {c[1]}".lower()]
        self.client_combo['values'] = filtered_clients
        if filtered_clients:
            self.client_combo.current(0)

    def on_machine_keyrelease(self, event):
        current_input = self.machine_var.get().lower()
        filtered_machines = [f"{m[0]} - {m[1]}" for m in self.machines if current_input in f"{m[0]} - {m[1]}".lower()]
        self.machine_combo['values'] = filtered_machines
        if filtered_machines:
            self.machine_combo.current(0)

    def on_machine_select(self, event):
        selected_machine = self.machine_combo.get()
        if selected_machine:
            machine_id = selected_machine.split(" - ")[0]
            self.selected_machine_ids = [machine_id]
            self.refresh_spare_part_list()

    def refresh_spare_part_list(self):
        if self.spare_part_listbox and hasattr(self, 'selected_machine_ids'):
            self.spare_part_listbox.delete(0, tk.END)
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