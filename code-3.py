import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("voting.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    voter_id TEXT PRIMARY KEY,
    password TEXT,
    has_voted INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    name TEXT PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    candidate TEXT,
    count INTEGER
)
""")

# Default candidates
default_candidates = ["Alice", "Bob"]
for c in default_candidates:
    cursor.execute("SELECT * FROM candidates WHERE name=?", (c,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO candidates VALUES (?)", (c,))
        cursor.execute("INSERT INTO votes VALUES (?, 0)", (c, 0))

conn.commit()

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Online Voting System")
root.geometry("500x500")

# ---------------- REGISTER ----------------
def register():
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Register", font=("Arial", 18)).pack(pady=10)

    id_entry = tk.Entry(root)
    pass_entry = tk.Entry(root, show="*")

    tk.Label(root, text="Voter ID").pack()
    id_entry.pack()

    tk.Label(root, text="Password").pack()
    pass_entry.pack()

    def save():
        vid = id_entry.get()
        pwd = pass_entry.get()

        try:
            cursor.execute("INSERT INTO users (voter_id, password) VALUES (?,?)", (vid, pwd))
            conn.commit()
            messagebox.showinfo("Success", "Registered Successfully")
            login_screen()
        except:
            messagebox.showerror("Error", "User already exists")

    tk.Button(root, text="Register", command=save).pack(pady=10)
    tk.Button(root, text="Back", command=login_screen).pack()

# ---------------- LOGIN ----------------
def login_screen():
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Login", font=("Arial", 18)).pack(pady=10)

    id_entry = tk.Entry(root)
    pass_entry = tk.Entry(root, show="*")

    tk.Label(root, text="Voter ID").pack()
    id_entry.pack()

    tk.Label(root, text="Password").pack()
    pass_entry.pack()

    def login():
        vid = id_entry.get()
        pwd = pass_entry.get()

        cursor.execute("SELECT * FROM users WHERE voter_id=? AND password=?", (vid, pwd))
        user = cursor.fetchone()

        if user:
            vote_screen(vid)
        else:
            messagebox.showerror("Error", "Invalid Login")

    tk.Button(root, text="Login", command=login).pack(pady=10)
    tk.Button(root, text="Register", command=register).pack()
    tk.Button(root, text="Admin", command=admin_login).pack()

# ---------------- VOTING ----------------
def vote_screen(voter_id):
    for w in root.winfo_children():
        w.destroy()

    cursor.execute("SELECT has_voted FROM users WHERE voter_id=?", (voter_id,))
    if cursor.fetchone()[0] == 1:
        tk.Label(root, text="You already voted!", fg="red").pack()
        tk.Button(root, text="Back", command=login_screen).pack()
        return

    tk.Label(root, text="Vote", font=("Arial", 18)).pack(pady=10)

    selected = tk.StringVar()

    cursor.execute("SELECT name FROM candidates")
    for c in cursor.fetchall():
        tk.Radiobutton(root, text=c[0], variable=selected, value=c[0]).pack()

    def submit():
        choice = selected.get()
        if choice == "":
            messagebox.showerror("Error", "Select candidate")
            return

        cursor.execute("UPDATE votes SET count = count + 1 WHERE candidate=?", (choice,))
        cursor.execute("UPDATE users SET has_voted = 1 WHERE voter_id=?", (voter_id,))
        conn.commit()

        messagebox.showinfo("Success", "Vote Submitted")
        login_screen()

    tk.Button(root, text="Submit Vote", command=submit).pack(pady=10)

# ---------------- ADMIN LOGIN ----------------
def admin_login():
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Admin Login", font=("Arial", 18)).pack(pady=10)

    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    def check():
        if pass_entry.get() == "admin123":
            admin_dashboard()
        else:
            messagebox.showerror("Error", "Wrong Password")

    tk.Button(root, text="Login", command=check).pack(pady=10)
    tk.Button(root, text="Back", command=login_screen).pack()

# ---------------- ADMIN DASHBOARD ----------------
def admin_dashboard():
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Admin Dashboard", font=("Arial", 18)).pack(pady=10)

    cursor.execute("SELECT * FROM votes")
    results = cursor.fetchall()

    for candidate, count in results:
        tk.Label(root, text=f"{candidate}: {count} votes", font=("Arial", 14)).pack()

    tk.Button(root, text="Add Candidate", command=add_candidate).pack(pady=5)
    tk.Button(root, text="Delete Candidate", command=delete_candidate).pack(pady=5)
    tk.Button(root, text="Refresh", command=admin_dashboard).pack(pady=5)
    tk.Button(root, text="Back", command=login_screen).pack(pady=5)

# ---------------- ADD CANDIDATE ----------------
def add_candidate():
    win = tk.Toplevel(root)
    win.title("Add Candidate")

    entry = tk.Entry(win)
    entry.pack(pady=5)

    def add():
        name = entry.get()
        try:
            cursor.execute("INSERT INTO candidates VALUES (?)", (name,))
            cursor.execute("INSERT INTO votes VALUES (?, 0)", (name,))
            conn.commit()
            messagebox.showinfo("Success", "Candidate Added")
            win.destroy()
        except:
            messagebox.showerror("Error", "Candidate already exists")

    tk.Button(win, text="Add", command=add).pack(pady=5)

# ---------------- DELETE CANDIDATE ----------------
def delete_candidate():
    win = tk.Toplevel(root)
    win.title("Delete Candidate")

    entry = tk.Entry(win)
    entry.pack(pady=5)

    def delete():
        name = entry.get()
        cursor.execute("DELETE FROM candidates WHERE name=?", (name,))
        cursor.execute("DELETE FROM votes WHERE candidate=?", (name,))
        conn.commit()
        messagebox.showinfo("Success", "Candidate Deleted")
        win.destroy()

    tk.Button(win, text="Delete", command=delete).pack(pady=5)

# ---------------- START ----------------
login_screen()
root.mainloop()
