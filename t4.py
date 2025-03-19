import tkinter as tk
from tkinter import ttk

class InvoiceApp:
    def __init__(self, master):
        self.master = master
        self.invoice_treeview = ttk.Treeview(master, columns=("ID", "NIF", "Machine Name", "User ", "Hours", "Invoice Date"), show='headings')
        self.invoice_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.invoice_treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.invoice_treeview.configure(yscrollcommand=scrollbar.set)

        # Define headings
        for col in self.invoice_treeview["columns"]:
            self.invoice_treeview.heading(col, text=col)

        # Sample data
        self.invoices = [
            (1, "NIF1", "Machine1", "User 1", 5, "2023-10-01"),
            (2, "NIF2", "Machine2", "User 2", 3, "2023-10-02"),
        ]

        self.refresh_invoice_list()

    def refresh_invoice_list(self):
        """Refresh the invoice list."""
        for inv in self.invoices:
            # Insert the invoice data into the treeview
            self.invoice_treeview.insert("", tk.END, values=inv[:-1])  # Exclude the last element for the button

            # Create a button for each row
            button = tk.Button(self.master, text="Get ID", command=lambda id=inv[0]: self.get_id(id))
            button.pack(side=tk.TOP, anchor=tk.W)  # Adjust the position as needed

    def get_id(self, id):
        """Handle button click to get the ID."""
        print(f"ID: {id}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()