import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database connection
con = sqlite3.connect("contacts.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT
)
""")
con.commit()

# Main window
root = tk.Tk()
root.title("Contact Book")
root.geometry("700x550")
root.configure(bg="#eaf2f8")

tk.Label(root, text="CONTACT BOOK",
         font=("Arial", 22, "bold"),
         bg="#1e3a5f", fg="white",
         pady=15).pack(fill="x")

# Input fields
frame = tk.Frame(root, bg="#eaf2f8")
frame.pack(pady=15)

entries = {}

for i, field in enumerate(["Name", "Phone", "Email"]):
    tk.Label(frame, text=field, bg="#eaf2f8",
             font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=8)

    entry = tk.Entry(frame, width=30, font=("Arial", 11))
    entry.grid(row=i, column=1, padx=10, pady=8)
    entries[field] = entry

# Contact table
columns = ("ID", "Name", "Phone", "Email")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(pady=15, fill="both", expand=True, padx=15)

selected_id = None

# Clear input fields
def clear():
    global selected_id
    for entry in entries.values():
        entry.delete(0, tk.END)
    selected_id = None
    tree.selection_remove(tree.selection())

# Display contacts
def display():
    tree.delete(*tree.get_children())
    cur.execute("SELECT * FROM contacts")
    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)

# Add contact
def add():
    name = entries["Name"].get().strip()
    phone = entries["Phone"].get().strip()
    email = entries["Email"].get().strip()

    if not name or not phone or not email:
        messagebox.showwarning("Warning", "Fill all fields")
        return

    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("Error", "Enter valid 10 digit phone")
        return

    if "@" not in email or "." not in email:
        messagebox.showerror("Error", "Enter valid email")
        return

    cur.execute("INSERT INTO contacts(name, phone, email) VALUES(?,?,?)",
                (name, phone, email))
    con.commit()
    display()
    clear()
    messagebox.showinfo("Success", "Contact added")

# Select contact
def select(event):
    global selected_id
    item = tree.selection()
    if item:
        row = tree.item(item[0])["values"]
        selected_id = row[0]
        for i, field in enumerate(["Name", "Phone", "Email"]):
            entries[field].delete(0, tk.END)
            entries[field].insert(0, row[i+1])

# Update contact
def update():
    if selected_id is None:
        messagebox.showwarning("Warning", "Select a contact")
        return

    name = entries["Name"].get().strip()
    phone = entries["Phone"].get().strip()
    email = entries["Email"].get().strip()

    if not name or not phone or not email:
        messagebox.showwarning("Warning", "Fill all fields")
        return

    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("Error", "Enter valid phone")
        return

    if "@" not in email or "." not in email:
        messagebox.showerror("Error", "Enter valid email")
        return

    cur.execute("UPDATE contacts SET name=?, phone=?, email=? WHERE id=?",
                (name, phone, email, selected_id))
    con.commit()
    display()
    clear()
    messagebox.showinfo("Success", "Contact updated")

# Delete contact
def delete():
    if selected_id is None:
        messagebox.showwarning("Warning", "Select a contact")
        return

    if messagebox.askyesno("Confirm", "Delete contact?"):
        # Delete the selected contact
        cur.execute("DELETE FROM contacts WHERE id=?", (selected_id,))
        
        # Check if the table is now empty
        cur.execute("SELECT COUNT(*) FROM contacts")
        if cur.fetchone()[0] == 0:
            # Reset the AUTOINCREMENT counter back to 0 (next entry will be 1)
            cur.execute("DELETE FROM sqlite_sequence WHERE name='contacts'")
            
        con.commit()
        display()
        clear()
        messagebox.showinfo("Success", "Contact deleted")

# Search contact
def search():
    keyword = entries["Name"].get().strip()
    tree.delete(*tree.get_children())

    cur.execute("SELECT * FROM contacts WHERE name LIKE ?",
                ('%' + keyword + '%',))

    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)

# Buttons
buttons = tk.Frame(root, bg="#eaf2f8")
buttons.pack(pady=10)

for text, command in [
    ("Add", add),
    ("Update", update),
    ("Delete", delete),
    ("Search", search),
    ("View All", display),
    ("Clear", clear)
]:
    tk.Button(buttons, text=text, command=command,
              width=10, bg="#1e3a5f", fg="white",
              font=("Arial", 10, "bold")).pack(side="left", padx=4)

tree.bind("<<TreeviewSelect>>", select)

display()
root.mainloop()

con.close()