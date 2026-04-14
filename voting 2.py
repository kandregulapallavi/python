import sqlite3
import threading
import time
import cv2
import customtkinter as ctk
from pyzbar import pyzbar
from tkinter import messagebox

# ---------------------------- NEW: MATPLOTLIB FOR CHARTS ----------------------------
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------- DATABASE SETUP ----------------------------
def init_db():
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    has_voted INTEGER DEFAULT 0,
                    registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    # NEW: table to store which candidate each voter chose
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    voter_id TEXT PRIMARY KEY,
                    candidate TEXT,
                    voted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(voter_id) REFERENCES voters(id)
                )''')
    conn.commit()
    conn.close()

def register_voter(voter_id, name):
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO voters (id, name, has_voted) VALUES (?, ?, 0)", (voter_id, name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def is_voter_valid(voter_id):
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    c.execute("SELECT has_voted FROM voters WHERE id = ?", (voter_id,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return "not_registered"
    elif row[0] == 1:
        return "already_voted"
    else:
        return "ok"

# NEW: record vote (marks voter as voted + stores candidate)
def record_vote(voter_id, candidate):
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    try:
        c.execute("UPDATE voters SET has_voted = 1 WHERE id = ?", (voter_id,))
        c.execute("INSERT INTO votes (voter_id, candidate) VALUES (?, ?)", (voter_id, candidate))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
    finally:
        conn.close()

# NEW: get vote counts per candidate
def get_vote_counts():
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
    rows = c.fetchall()
    conn.close()
    counts = {"Candidate A": 0, "Candidate B": 0, "Candidate C": 0, "NOTA": 0}
    for cand, cnt in rows:
        if cand in counts:
            counts[cand] = cnt
    return counts

def get_all_voters():
    conn = sqlite3.connect("voting_system.db")
    c = conn.cursor()
    c.execute("SELECT id, name, has_voted FROM voters ORDER BY registered_on DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------------------- MAIN APP ----------------------------
class VotingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("College Voting System")
        self.geometry("900x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Initialize database first
        init_db()

        # State variables
        self.current_valid_id = None
        self.camera_running = False

        # Tabbed interface
        self.tabview = ctk.CTkTabview(self, width=850, height=600)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Create tabs
        self.vote_tab = self.tabview.add("🗳️ Cast Vote")
        self.register_tab = self.tabview.add("📝 Register Voter")
        self.list_tab = self.tabview.add("📋 Voter List")
        self.chart_tab = self.tabview.add("📊 Results Chart")   # NEW CHART TAB

        # Setup each tab
        self.setup_vote_tab()
        self.setup_register_tab()
        self.setup_list_tab()
        self.setup_chart_tab()   # NEW

    # ---------------------------- VOTE TAB ----------------------------
    def setup_vote_tab(self):
        # Left frame (scanning)
        left_frame = ctk.CTkFrame(self.vote_tab, width=400)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Scan ID Card", font=("Arial", 20, "bold")).pack(pady=10)

        self.scan_label = ctk.CTkLabel(left_frame, text="No ID scanned", font=("Arial", 14))
        self.scan_label.pack(pady=5)

        self.scan_btn = ctk.CTkButton(left_frame, text="📷 Scan ID (Webcam)", command=self.start_scan_thread, width=200)
        self.scan_btn.pack(pady=10)

        self.manual_entry = ctk.CTkEntry(left_frame, placeholder_text="Or enter ID manually", width=250)
        self.manual_entry.pack(pady=5)

        self.manual_verify_btn = ctk.CTkButton(left_frame, text="Verify Manual ID", command=self.verify_manual_id, width=200)
        self.manual_verify_btn.pack(pady=5)

        self.vote_status = ctk.CTkLabel(left_frame, text="", font=("Arial", 12))
        self.vote_status.pack(pady=10)

        # Right frame (candidates)
        right_frame = ctk.CTkFrame(self.vote_tab, width=400)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Select Candidate", font=("Arial", 20, "bold")).pack(pady=10)

        self.candidate_var = ctk.StringVar(value="Candidate A")
        candidates = ["Candidate A", "Candidate B", "Candidate C", "NOTA"]
        for cand in candidates:
            ctk.CTkRadioButton(right_frame, text=cand, variable=self.candidate_var, value=cand).pack(anchor="w", padx=30, pady=5)

        self.cast_btn = ctk.CTkButton(right_frame, text="🗳️ Cast Vote", command=self.cast_vote, state="disabled", width=200)
        self.cast_btn.pack(pady=20)

    def start_scan_thread(self):
        if self.camera_running:
            return
        self.scan_btn.configure(state="disabled")
        threading.Thread(target=self.scan_webcam, daemon=True).start()

    def scan_webcam(self):
        self.camera_running = True
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.after(0, lambda: messagebox.showerror("Camera Error", "Cannot open webcam. Check if camera is connected and not in use."))
            self.camera_running = False
            self.scan_btn.configure(state="normal")
            return

        cv2.namedWindow("Scan QR/Barcode - Press 'q' to cancel", cv2.WINDOW_NORMAL)
        scanned_id = None

        while self.camera_running:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Scan QR/Barcode - Press 'q' to cancel", frame)
            decoded_objs = pyzbar.decode(frame)
            for obj in decoded_objs:
                scanned_id = obj.data.decode("utf-8").strip()
                self.camera_running = False
                break

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q') or key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camera_running = False
        self.scan_btn.configure(state="normal")

        if scanned_id:
            self.after(0, lambda: self.process_scanned_id(scanned_id))
        else:
            self.after(0, lambda: messagebox.showinfo("Scan Cancelled", "No QR/barcode detected or scan cancelled."))

    def verify_manual_id(self):
        voter_id = self.manual_entry.get().strip()
        if not voter_id:
            messagebox.showwarning("Input Error", "Please enter an ID")
            return
        self.process_scanned_id(voter_id)

    def process_scanned_id(self, voter_id):
        self.current_valid_id = voter_id
        self.scan_label.configure(text=f"Scanned ID: {voter_id}")
        status = is_voter_valid(voter_id)

        if status == "not_registered":
            self.vote_status.configure(text="❌ Not registered. Please register first.", text_color="red")
            self.cast_btn.configure(state="disabled")
            if messagebox.askyesno("Not Registered", f"ID {voter_id} is not registered.\nRegister now?"):
                self.open_quick_register(voter_id)
        elif status == "already_voted":
            self.vote_status.configure(text="⛔ This ID has already voted! Rejected.", text_color="red")
            self.cast_btn.configure(state="disabled")
        else:
            self.vote_status.configure(text=f"✅ Verified! You can vote for ID: {voter_id}", text_color="green")
            self.cast_btn.configure(state="normal")

    def open_quick_register(self, voter_id):
        reg_window = ctk.CTkToplevel(self)
        reg_window.title("Register Voter")
        reg_window.geometry("400x250")
        ctk.CTkLabel(reg_window, text=f"Register ID: {voter_id}", font=("Arial", 14)).pack(pady=10)
        name_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter Voter Name", width=250)
        name_entry.pack(pady=10)

        def do_register():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            if register_voter(voter_id, name):
                messagebox.showinfo("Success", f"Voter {name} registered!")
                reg_window.destroy()
                self.process_scanned_id(voter_id)
            else:
                messagebox.showerror("Error", "ID already exists or registration failed")

        ctk.CTkButton(reg_window, text="Register", command=do_register).pack(pady=20)

    def cast_vote(self):
        if not self.current_valid_id:
            messagebox.showerror("Error", "No verified ID. Please scan or enter an ID first.")
            return
        candidate = self.candidate_var.get()
        record_vote(self.current_valid_id, candidate)
        messagebox.showinfo("Vote Cast", f"Your vote for {candidate} has been recorded.")
        # Reset UI
        self.cast_btn.configure(state="disabled")
        self.vote_status.configure(text="Vote cast. Next voter can scan.", text_color="gray")
        self.current_valid_id = None
        self.scan_label.configure(text="No ID scanned")
        self.manual_entry.delete(0, 'end')
        # NEW: refresh the chart after vote
        self.refresh_chart()

    # ---------------------------- REGISTER TAB ----------------------------
    def setup_register_tab(self):
        frame = ctk.CTkFrame(self.register_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Register New Voter", font=("Arial", 24, "bold")).pack(pady=20)

        ctk.CTkLabel(frame, text="Voter ID (from card)").pack()
        self.reg_id_entry = ctk.CTkEntry(frame, placeholder_text="Scan or type ID", width=300)
        self.reg_id_entry.pack(pady=5)

        ctk.CTkLabel(frame, text="Full Name").pack()
        self.reg_name_entry = ctk.CTkEntry(frame, placeholder_text="Enter full name", width=300)
        self.reg_name_entry.pack(pady=5)

        ctk.CTkButton(frame, text="📷 Scan ID from Card", command=self.register_scan_id).pack(pady=10)

        def submit_reg():
            vid = self.reg_id_entry.get().strip()
            name = self.reg_name_entry.get().strip()
            if not vid or not name:
                messagebox.showerror("Error", "Both ID and Name are required")
                return
            if register_voter(vid, name):
                messagebox.showinfo("Success", f"Voter {name} registered successfully!")
                self.reg_id_entry.delete(0, 'end')
                self.reg_name_entry.delete(0, 'end')
                self.refresh_voter_list()
            else:
                messagebox.showerror("Error", "ID already exists in database")

        ctk.CTkButton(frame, text="Register", command=submit_reg, width=200).pack(pady=20)

    def register_scan_id(self):
        def scan_thread():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.after(0, lambda: messagebox.showerror("Camera Error", "Cannot open webcam"))
                return

            cv2.namedWindow("Scan for Registration - Press 'q' to cancel", cv2.WINDOW_NORMAL)
            scanned_id = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Scan for Registration - Press 'q' to cancel", frame)
                decoded = pyzbar.decode(frame)
                for obj in decoded:
                    scanned_id = obj.data.decode("utf-8").strip()
                    break
                if scanned_id:
                    break
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            if scanned_id:
                self.after(0, lambda: self.reg_id_entry.delete(0, 'end'))
                self.after(0, lambda: self.reg_id_entry.insert(0, scanned_id))
            else:
                self.after(0, lambda: messagebox.showwarning("Scan Cancelled", "No QR/barcode detected or cancelled."))

        threading.Thread(target=scan_thread, daemon=True).start()

    # ---------------------------- VOTER LIST TAB ----------------------------
    def setup_list_tab(self):
        frame = ctk.CTkFrame(self.list_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Registered Voters", font=("Arial", 20, "bold")).pack(pady=10)

        self.list_textbox = ctk.CTkTextbox(frame, width=700, height=400)
        self.list_textbox.pack(pady=10, fill="both", expand=True)

        refresh_btn = ctk.CTkButton(frame, text="Refresh List", command=self.refresh_voter_list)
        refresh_btn.pack(pady=10)

        self.refresh_voter_list()

    def refresh_voter_list(self):
        voters = get_all_voters()
        self.list_textbox.delete("1.0", "end")
        if not voters:
            self.list_textbox.insert("1.0", "No voters registered yet.")
        else:
            header = f"{'ID':<20} {'Name':<25} {'Voted':<10}\n{'-'*55}\n"
            self.list_textbox.insert("1.0", header)
            for vid, name, voted in voters:
                status = "✅ Voted" if voted else "❌ Not Voted"
                line = f"{vid:<20} {name:<25} {status:<10}\n"
                self.list_textbox.insert("end", line)

    # ---------------------------- NEW CHART TAB (3 CHART TYPES) ----------------------------
    def setup_chart_tab(self):
        self.chart_frame = ctk.CTkFrame(self.chart_tab)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.chart_frame, text="Live Voting Results", font=("Arial", 20, "bold")).pack(pady=10)

        # Dropdown to select chart type
        self.chart_type_var = ctk.StringVar(value="Bar Chart")
        chart_types = ["Bar Chart", "Pie Chart", "Horizontal Bar Chart"]
        ctk.CTkLabel(self.chart_frame, text="Select Chart Type:").pack(pady=(5,0))
        chart_menu = ctk.CTkComboBox(self.chart_frame, values=chart_types, variable=self.chart_type_var,
                                     command=lambda _: self.refresh_chart())
        chart_menu.pack(pady=5)

        # Refresh button
        refresh_chart_btn = ctk.CTkButton(self.chart_frame, text="Refresh Chart", command=self.refresh_chart)
        refresh_chart_btn.pack(pady=5)

        # Matplotlib figure and canvas
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

        self.refresh_chart()

    def refresh_chart(self):
        """Fetch latest vote counts and draw selected chart type."""
        counts = get_vote_counts()
        candidates = list(counts.keys())
        votes = list(counts.values())
        chart_type = self.chart_type_var.get()

        self.ax.clear()

        if chart_type == "Bar Chart":
            bars = self.ax.bar(candidates, votes, color=['#4CAF50', '#2196F3', '#FF9800', '#9E9E9E'])
            self.ax.set_title("Vote Distribution (Bar Chart)")
            self.ax.set_xlabel("Candidates")
            self.ax.set_ylabel("Number of Votes")
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(height)}', ha='center', va='bottom')

        elif chart_type == "Pie Chart":
            # Filter out zero votes for pie chart to avoid clutter
            non_zero = [(c, v) for c, v in zip(candidates, votes) if v > 0]
            if non_zero:
                labels, sizes = zip(*non_zero)
                self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                            colors=['#4CAF50', '#2196F3', '#FF9800', '#9E9E9E'])
                self.ax.set_title("Vote Distribution (Pie Chart)")
                self.ax.axis('equal')
            else:
                self.ax.text(0.5, 0.5, "No votes yet", ha='center', va='center', transform=self.ax.transAxes)
                self.ax.set_title("Pie Chart (No Data)")

        elif chart_type == "Horizontal Bar Chart":
            bars = self.ax.barh(candidates, votes, color=['#4CAF50', '#2196F3', '#FF9800', '#9E9E9E'])
            self.ax.set_title("Vote Distribution (Horizontal Bar Chart)")
            self.ax.set_xlabel("Number of Votes")
            self.ax.set_ylabel("Candidates")
            self.ax.grid(axis='x', linestyle='--', alpha=0.7)
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                self.ax.text(width, bar.get_y() + bar.get_height()/2.,
                             f'{int(width)}', ha='left', va='center')

        self.canvas.draw()

# ---------------------------- RUN ----------------------------
if __name__ == "__main__":
    app = VotingApp()
    app.mainloop()
