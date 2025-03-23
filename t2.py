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

        # Search entries
        self.search_client_var = tk.StringVar()
        self.search_client_entry = ttk.Entry(self.navbar_frame, textvariable=self.search_client_var)
        self.search_client_entry.pack(side=tk.LEFT, padx=10, pady=5)
        self.search_client_entry.bind("<KeyRelease>", self.search_clients)

        self.search_machine_var = tk.StringVar()
        self.search_machine_entry = ttk.Entry(self.navbar_frame, textvariable=self.search_machine_var)
        self.search_machine_entry.pack(side=tk.LEFT, padx=10, pady=5)
        self.search_machine_entry.bind("<KeyRelease>", self.search_machines)

        self.search_spare_part_var = tk.StringVar()
        self.search_spare_part_entry = ttk.Entry(self.navbar_frame, textvariable=self.search_spare_part_var)
        self.search_spare_part_entry.pack(side=tk.LEFT, padx=10, pady=5)
        self.search_spare_part_entry.bind("<KeyRelease>", self.search_spare_parts)

        # self.search_invoice_var = tk.StringVar()
        # self.search_invoice_entry = ttk.Entry(self.navbar_frame, textvariable=self.search_invoice_var)
        # self.search_invoice_entry.pack(side=tk.LEFT, padx=10, pady=5)
        # self.search_invoice_entry.bind("<KeyRelease>", self.search_invoices)

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

        # Add remove buttons
        self.remove_client_button = ttk.Button(self.navbar_frame, text="Remove Client", command=lambda: self.remove_client(self.get_selected_client_id()))
        self.remove_machine_button = ttk.Button(self.navbar_frame, text="Remove Machine", command=lambda: self.remove_machine(self.get_selected_machine_id()))
        self.remove_spare_part_button = ttk.Button(self.navbar_frame, text="Remove Spare Part", command=lambda: self.remove_spare_part(self.get_selected_spare_part_id()))

        # Pack the buttons in the navbar
        self.remove_client_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.remove_machine_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.remove_spare_part_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Initially disable the remove buttons
        self.remove_client_button.config(state=tk.DISABLED)
        self.remove_machine_button.config(state=tk.DISABLED)
        self.remove_spare_part_button.config(state=tk.DISABLED)

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
        self.invoice_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Client", "Machine", "User      ", "Hours", "Date"), show='headings')
        self.invoice_treeview.heading("ID", text="ID")
        self.invoice_treeview.heading("Client", text="Client")
        self.invoice_treeview.heading("Machine", text="Machine")
        self.invoice_treeview.heading("User      ", text="User      ")
        self.invoice_treeview.heading("Hours", text="Hours")
        self.invoice_treeview.heading("Date", text="Date")
        self.invoice_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.invoice_treeview.bind("<Double-1>", self.on_invoice_double_click)

        # Create Treeview for Clients
        self.client_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Registre Comars", "NIF", "NIS", "AI"), show='headings')
        self.client_treeview.heading("ID", text="ID")
        self.client_treeview.heading("Registre Comars", text="Registre Comars")
        self.client_treeview.heading("NIF", text="NIF")
        self.client_treeview.heading("NIS", text="NIS")
        self.client_treeview.heading("AI", text="AI")
        self.client_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.client_treeview.bind("<Double-1>", self.on_client_double_click)

        # Create Treeview for Machines
        self.machine_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Name", "Model", "Company", "NS"), show='headings')
        self.machine_treeview.heading("ID", text="ID")
        self.machine_treeview.heading("Name", text="Name")
        self.machine_treeview.heading("Model", text="Model")
        self.machine_treeview.heading("Company", text="Company")
        self.machine_treeview.heading("NS", text="NS")
        self.machine_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.machine_treeview.bind("<Double-1>", self.on_machine_double_click)

        # Create Treeview for Spare Parts
        self.spare_part_treeview = ttk.Treeview(self.list_frame, columns=("ID", "Name", "Serial Number", "Machine ID"), show='headings')
        self.spare_part_treeview.heading("ID", text="ID")
        self.spare_part_treeview.heading("Name", text="Name")
        self.spare_part_treeview.heading("Serial Number", text="Serial Number")
        self.spare_part_treeview.heading("Machine ID", text="Machine ID")
        self.spare_part_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.spare_part_treeview.bind("<Double-1>", self.on_spare_part_double_click)

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
        self.search_invoice_var.set("")  # Clear search entry

    def show_clients(self):
        """Show the client treeview and refresh its data."""
        self.hide_all_treeviews()
        self.client_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_client_list()
        self.search_client_var.set("")  # Clear search entry

    def show_machines(self):
        """Show the machine treeview and refresh its data."""
        self.hide_all_treeviews()
        self.machine_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_machine_list()
        self.search_machine_var.set("")  # Clear search entry

    def show_spare_parts(self):
        """Show the spare part treeview and refresh its data."""
        self.hide_all_treeviews()
        self.spare_part_treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_spare_p_list()
        self.search_spare_part_var.set("")  # Clear search entry

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

    def refresh_client_list(self):
        """Refresh the client list."""
        self.client_treeview.delete(*self.client_treeview.get_children())  # Clear the treeview
        self.cursor.execute("SELECT id, registre_comars, nif, nis, ai FROM Client")
        clients = self.cursor.fetchall()
        for client in clients:
            self.client_treeview.insert("", tk.END, values=client)
        
        # Enable or disable the remove button based on the client list
        if clients:
            self.remove_client_button.config(state=tk.NORMAL)
        else:
            self.remove_client_button.config(state=tk.DISABLED)

    def refresh_machine_list(self):
        """Refresh the machine list."""
        self.machine_treeview.delete(*self.machine_treeview.get_children())  # Clear the treeview
        self.cursor.execute("SELECT id, name, model, company, ns FROM Machine")
        machines = self.cursor.fetchall()
        for machine in machines:
            self.machine_treeview.insert("", tk.END, values=machine)
        
        # Enable or disable the remove button based on the machine list
        if machines:
            self.remove_machine_button.config(state=tk.NORMAL)
        else:
            self.remove_machine_button.config(state=tk.DISABLED)

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
        
        # Enable or disable the remove button based on the spare part list
        if spare_parts:
            self.remove_spare_part_button.config(state=tk.NORMAL)
        else:
            self.remove_spare_part_button.config(state=tk.DISABLED)

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

        # Bind selection event for autofill
        self.machine_combo.bind("<<ComboboxSelected>>", self.on_machine_select)

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

        fields = ["Date (YYYY-MM-DD)", "Description", "User            ", "Hours"]
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
        self.machine_combo.bind("<<ComboboxSelected>>", self.on_machine_select)  # Bind selection event

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
                    (entries["Description"].get(), entries["Date (YYYY-MM-DD)"].get(), entries["User            "].get(), entries["Hours"].get())
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
            query = "SELECT id, name FROM SparePart WHERE machine_id = ?"
            self.cursor.execute(query, (self.selected_machine_ids[0],))  # Use the selected machine ID
            spare_parts = self.cursor.fetchall()
            for sp in spare_parts:
                self.spare_part_listbox.insert(tk.END, f"{sp[0]} - {sp[1]}")  # Add spare parts to the listbox

    def on_invoice_double_click(self, event):
        selected_item = self.invoice_treeview.selection()
        if selected_item:
            item = self.invoice_treeview.item(selected_item, 'values')  # Get the values of the selected invoice
            self.show_id_window("Invoice Details", {
                "ID": item[0],
                "Client": item[1],
                "Machine": item[2],
                "User     ": item[3],
                "Hours": item[4],
                "Date": item[5]
            })

    def on_client_double_click(self, event):
        selected_item = self.client_treeview.selection()
        if selected_item:
            item = self.client_treeview.item(selected_item, 'values')  # Get the values of the selected client
            client_id = item[0]  # Get the ID of the selected client
            self.show_edit_client(client_id)  # Show edit form

    def on_machine_double_click(self, event):
        selected_item = self.machine_treeview.selection()
        if selected_item:
            item = self.machine_treeview.item(selected_item, 'values')  # Get the values of the selected machine
            machine_id = item[0]  # Get the ID of the selected machine
            self.show_edit_machine(machine_id)  # Show edit form

    def on_spare_part_double_click(self, event):
        selected_item = self.spare_part_treeview.selection()
        if selected_item:
            item = self.spare_part_treeview.item(selected_item, 'values')  # Get the values of the selected spare part
            spare_part_id = item[0]  # Get the ID of the selected spare part
            self.show_edit_spare_part(spare_part_id)  # Show edit form

    def show_edit_client(self, client_id):
        """Show the edit form for a client."""
        self.clear_form_frame()
        self.cursor.execute("SELECT * FROM Client WHERE id = ?", (client_id,))
        client = self.cursor.fetchone()
        
        fields = ["Registre Comars", "NIF", "NIS", "AI"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)
            entries[field].insert(0, client[i + 1])  # Fill with existing data

        def save_client():
            data = [entries[field].get() for field in fields]
            try:
                self.cursor.execute(
                    "UPDATE Client SET registre_comars = ?, nif = ?, nis = ?, ai = ? WHERE id = ?",
                    (*data, client_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Client updated successfully!")
                self.refresh_client_list()  # Refresh the client list
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.form_frame, text="Save", command=save_client).grid(row=len(fields), columnspan=2, pady=10)

    def remove_client(self, client_id):
        """Remove a client from the database."""
        try:
            self.cursor.execute("DELETE FROM Client WHERE id = ?", (client_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Client removed successfully!")
            self.refresh_client_list()  # Refresh the client list
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_edit_machine(self, machine_id):
        """Show the edit form for a machine."""
        self.clear_form_frame()
        self.cursor.execute("SELECT * FROM Machine WHERE id = ?", (machine_id,))
        machine = self.cursor.fetchone()
        
        fields = ["Name", "Model", "Company", "NS"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)
            entries[field].insert(0, machine[i + 1])  # Fill with existing data

        def save_machine():
            data = [entries[field].get() for field in fields]
            try:
                self.cursor.execute(
                    "UPDATE Machine SET name = ?, model = ?, company = ?, ns = ? WHERE id = ?",
                    (*data, machine_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Machine updated successfully!")
                self.refresh_machine_list()  # Refresh the machine list
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.form_frame, text="Save", command=save_machine).grid(row=len(fields), columnspan=2, pady=10)

    def remove_machine(self, machine_id):
        """Remove a machine from the database."""
        try:
            self.cursor.execute("DELETE FROM Machine WHERE id = ?", (machine_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Machine removed successfully!")
            self.refresh_machine_list()  # Refresh the machine list
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_edit_spare_part(self, spare_part_id):
        """Show the edit form for a spare part."""
        self.clear_form_frame()
        self.cursor.execute("SELECT * FROM SparePart WHERE id = ?", (spare_part_id,))
        spare_part = self.cursor.fetchone()
        
        fields = ["Name", "Serial Number"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(self.form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            entries[field] = ttk.Entry(self.form_frame)
            entries[field].grid(row=i, column=1, padx=5, pady=5)
            entries[field].insert(0, spare_part[i + 1])  # Fill with existing data

        # Populate machine dropdown for spare part
        ttk.Label(self.form_frame, text="Select Machine:").grid(row=2, column=0, padx=5, pady=5)
        self.machine_var = tk.StringVar()
        self.machine_combo = ttk.Combobox(self.form_frame, textvariable=self.machine_var)
        self.machine_combo.grid(row=2, column=1, padx=5, pady=5)

        # Fetch machines from the database
        self.cursor.execute("SELECT id, name FROM Machine")
        self.machines = self.cursor.fetchall()  # Store machines for autofill
        self.machine_combo['values'] = [f"{m[0]} - {m[1]}" for m in self.machines]
        self.machine_combo.set(f"{spare_part[3]} - {self.get_machine_name(spare_part[3])}")  # Set current machine

        def save_spare_part():
            machine_id = self.machine_var.get().split(" - ")[0]
            data = [entries[field].get() for field in fields]  # Get data from entries
            try:
                self.cursor.execute(
                    "UPDATE SparePart SET name = ?, serial_number = ?, machine_id = ? WHERE id = ?",
                    (*data, machine_id, spare_part_id)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "Spare part updated successfully!")
                self.refresh_spare_p_list()  # Refresh the spare part list
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.form_frame, text="Save", command=save_spare_part).grid(row=3, columnspan=2, pady=10)

    def remove_spare_part(self, spare_part_id):
        """Remove a spare part from the database."""
        try:
            self.cursor.execute("DELETE FROM SparePart WHERE id = ?", (spare_part_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Spare part removed successfully!")
            self.refresh_spare_p_list()  # Refresh the spare part list
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_machine_name(self, machine_id):
        """Get the name of a machine by its ID."""
        self.cursor.execute("SELECT name FROM Machine WHERE id = ?", (machine_id,))
        return self.cursor.fetchone()[0]

    def show_id_window(self, title, details):
        """Create a new window to display the details of the selected item."""
        id_window = tk.Toplevel(self.root)
        id_window.title(title)
        
        # Create labels for each piece of information
        for field, value in details.items():
            ttk.Label(id_window, text=f"{field}: {value}").pack(padx=20, pady=5)

        ttk.Button(id_window, text="Close", command=id_window.destroy).pack(pady=10)

    def get_selected_client_id(self):
        selected_item = self.client_treeview.selection()
        if selected_item:
            return self.client_treeview.item(selected_item, 'values')[0]
        return None

    def get_selected_machine_id(self):
        selected_item = self.machine_treeview.selection()
        if selected_item:
            return self.machine_treeview.item(selected_item, 'values')[0]
        return None

    def get_selected_spare_part_id(self):
        selected_item = self.spare_part_treeview.selection()
        if selected_item:
            return self.spare_part_treeview.item(selected_item, 'values')[0]
        return None

    def run(self):
        self.root.mainloop()

    def search_clients(self, event):
        search_term = self.search_client_var.get().lower()
        self.client_treeview.delete(*self.client_treeview.get_children())
        self.cursor.execute("SELECT id, registre_comars, nif, nis, ai FROM Client")
        clients = self.cursor.fetchall()
        for client in clients:
            if search_term in client[2].lower():  # Search by NIF
                self.client_treeview.insert("", tk.END, values=client)

    def search_machines(self, event):
        search_term = self.search_machine_var.get().lower()
        self.machine_treeview.delete(*self.machine_treeview.get_children())
        self.cursor.execute("SELECT id, name, model, company, ns FROM Machine")
        machines = self.cursor.fetchall()
        for machine in machines:
            if search_term in machine[1].lower() or search_term in machine[2].lower():  # Search by Name or Model
                self.machine_treeview.insert("", tk.END, values=machine)

    def search_spare_parts(self, event):
        search_term = self.search_spare_part_var.get().lower()
        self.spare_part_treeview.delete(*self.spare_part_treeview.get_children())
        self.cursor.execute("SELECT id, name, serial_number, machine_id FROM SparePart")
        spare_parts = self.cursor.fetchall()
        for sp in spare_parts:
            if search_term in sp[1].lower():  # Search by Name
                self.spare_part_treeview.insert("", tk.END, values=sp)

    def search_invoices(self, event):
        search_term = self.search_invoice_var.get().lower()
        self.invoice_treeview.delete(*self.invoice_treeview.get_children())
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
            if search_term in inv[1].lower():  # Search by Client NIF
                self.invoice_treeview.insert("", tk.END, values=inv)

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    app.run()