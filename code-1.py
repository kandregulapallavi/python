import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("voting.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS voters (
    voter_id TEXT PRIMARY KEY,
    has_voted INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    candidate TEXT,
    count INTEGER
)
""")

# Insert candidates if not exists
candidates = ["Alice", "Bob", "Charlie"]
for c in candidates:
    cursor.execute("SELECT * FROM votes WHERE candidate=?", (c,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO votes VALUES (?, ?)", (c, 0))

conn.commit()

# ---------------- MAIN APP ----------------
root = tk.Tk()
root.title("Online Voting System")
root.geometry("500x400")

# ---------------- LOGIN SCREEN ----------------
def login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Voter Login", font=("Arial", 18)).pack(pady=20)

    tk.Label(root, text="Enter Voter ID").pack()
    voter_entry = tk.Entry(root)
    voter_entry.pack()

    def login():
        voter_id = voter_entry.get()

        if voter_id == "":
            messagebox.showerror("Error", "Enter Voter ID")
            return

        cursor.execute("SELECT * FROM voters WHERE voter_id=?", (voter_id,))
        user = cursor.fetchone()

        if user is None:
            cursor.execute("INSERT INTO voters (voter_id) VALUES (?)", (voter_id,))
            conn.commit()

        vote_screen(voter_id)

    tk.Button(root, text="Login", command=login).pack(pady=10)
    tk.Button(root, text="Admin Dashboard", command=admin_login).pack(pady=5)

# ---------------- VOTING SCREEN ----------------
def vote_screen(voter_id):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Welcome {voter_id}", font=("Arial", 16)).pack(pady=10)

    cursor.execute("SELECT has_voted FROM voters WHERE voter_id=?", (voter_id,))
    status = cursor.fetchone()[0]

    if status == 1:
        tk.Label(root, text="You have already voted!", fg="red").pack()
        tk.Button(root, text="Back", command=login_screen).pack(pady=10)
        return

    tk.Label(root, text="Select Candidate", font=("Arial", 14)).pack(pady=10)

    selected = tk.StringVar()

    for c in candidates:
        tk.Radiobutton(root, text=c, variable=selected, value=c).pack()

    def submit_vote():
        choice = selected.get()
        if choice == "":
            messagebox.showerror("Error", "Select a candidate")
            return

        cursor.execute("UPDATE votes SET count = count + 1 WHERE candidate=?", (choice,))
        cursor.execute("UPDATE voters SET has_voted=1 WHERE voter_id=?", (voter_id,))
        conn.commit()

        messagebox.showinfo("Success", "Vote Submitted!")
        login_screen()

    tk.Button(root, text="Submit Vote", command=submit_vote).pack(pady=10)

# ---------------- ADMIN LOGIN ----------------
def admin_login():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Admin Login", font=("Arial", 18)).pack(pady=20)

    tk.Label(root, text="Enter Password").pack()
    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    def check():
        if pass_entry.get() == "admin123":
            dashboard()
        else:
            messagebox.showerror("Error", "Wrong Password")

    tk.Button(root, text="Login", command=check).pack(pady=10)

# ---------------- DASHBOARD ----------------
def dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Voting Results", font=("Arial", 18)).pack(pady=20)

    cursor.execute("SELECT * FROM votes")
    results = cursor.fetchall()

    for candidate, count in results:
        tk.Label(root, text=f"{candidate}: {count} votes", font=("Arial", 14)).pack()

    def refresh():
        dashboard()

    tk.Button(root, text="Refresh", command=refresh).pack(pady=5)
    tk.Button(root, text="Back", command=login_screen).pack(pady=5)

# ---------------- START APP ----------------
login_screen()
root.mainloop()
