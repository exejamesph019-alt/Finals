import tkinter as tk
from tkinter import messagebox
import os
import ssl
import smtplib
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from email.message import EmailMessage
from html import escape
import sqlite3
import hashlib
import hmac
import secrets

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "exejamesph019@gmail.com").strip()
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "asus jpoq iauf lobs").replace(" ", "").strip()
PASSING_PERCENTAGE = 75
MIN_PASSWORD_LENGTH = 8

current_user = None

lessons_read = {}

DB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pycharm_reviewer.db"
)
HASH_ITERATIONS = 200_000

REQUIRED_USER_COLUMNS = {
    "id", "full_name", "username", "password_hash",
    "salt", "iterations", "gmail", "created_at",
}


def db_run(sql, params=(), fetch=None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor = conn.execute(sql, params)
            if fetch == "one":
                return cursor.fetchone()
            if fetch == "all":
                return cursor.fetchall()
    finally:
        conn.close()


def init_db():
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        try:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        finally:
            conn.close()

        if columns and not REQUIRED_USER_COLUMNS <= columns:
            os.replace(DB_FILE, DB_FILE + ".old")

    db_run("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT NOT NULL,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            iterations    INTEGER NOT NULL,
            gmail         TEXT NOT NULL DEFAULT '',
            created_at    TEXT NOT NULL
        )
    """)
    db_run("""
        CREATE TABLE IF NOT EXISTS progress (
            username TEXT NOT NULL,
            topic    TEXT NOT NULL,
            kind     TEXT NOT NULL CHECK (kind IN ('read', 'practice')),
            PRIMARY KEY (username, topic, kind),
            FOREIGN KEY (username) REFERENCES users (username)
                ON DELETE CASCADE
        )
    """)


def hash_password(password, salt=None, iterations=HASH_ITERATIONS):
    salt = salt if salt is not None else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return digest.hex(), salt.hex()


def verify_password(password, stored_hash, salt_hex, iterations):
    digest, _ = hash_password(password, bytes.fromhex(salt_hex), iterations)
    return hmac.compare_digest(digest, stored_hash)


def get_user(username):
    return db_run(
        "SELECT * FROM users WHERE username = ?", (username,), fetch="one"
    )


def create_user(full_name, username, password, gmail):
    password_hash, salt = hash_password(password)
    try:
        db_run(
            "INSERT INTO users (full_name, username, password_hash, salt, "
            "iterations, gmail, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (full_name, username, password_hash, salt, HASH_ITERATIONS,
             gmail, datetime.now().isoformat(timespec="seconds"))
        )
        return True
    except sqlite3.IntegrityError:
        return False


def load_progress(username):
    lessons_read[username] = set()
    practice_passed[username] = set()
    rows = db_run(
        "SELECT topic, kind FROM progress WHERE username = ?",
        (username,), fetch="all"
    )
    for row in rows:
        target = lessons_read if row["kind"] == "read" else practice_passed
        target[username].add(row["topic"])


def save_progress(username, topic, kind):
    db_run(
        "INSERT OR IGNORE INTO progress (username, topic, kind) VALUES (?, ?, ?)",
        (username, topic, kind)
    )


def mark_read(topic_name):
    lessons_read.setdefault(current_user, set()).add(topic_name)
    save_progress(current_user, topic_name, "read")


def mark_practice(topic_name):
    practice_passed.setdefault(current_user, set()).add(topic_name)
    save_progress(current_user, topic_name, "practice")


REQUIRE_ALL_LESSONS_FOR_QUIZ = True

topics = {
    "Introduction to Programming": (
        "CHAPTER 1: INTRODUCTION TO PROGRAMMING",
        "Programming is the process of giving instructions "
        "to a computer. A program is a set of instructions "
        "that performs a specific task.\n\n"
        "An algorithm is a step-by-step procedure for solving "
        "a problem. Python is a programming language used "
        "to create different types of programs.",
        '''print("Hello, Python!")
print("Welcome to programming.")''',
        '''Hello, Python!
Welcome to programming.'''
    ),
    "Python Basic Syntax": (
        "CHAPTER 2: PYTHON BASIC SYNTAX",
        "Syntax refers to the rules of writing Python code. "
        "Python uses indentation to organize statements. "
        "Python is also case-sensitive.",
        '''if 5 > 2:
    print("Five is greater than two")''',
        "Five is greater than two"
    ),
    "Printing Output": (
        "PRINTING OUTPUT",
        "The print() function displays text, numbers, "
        "and other information on the screen.",
        '''print("Hello, world!")
print("Age:", 17)
print(10 + 5)''',
        '''Hello, world!
Age: 17
15'''
    ),
    "Python Comments": (
        "PYTHON COMMENTS",
        "Comments are notes written inside the code. "
        "Python ignores comments when executing a program. "
        "A single-line comment starts with #.",
        '''# This is a comment
name = "Alex"

print(name)''',
        "Alex"
    ),
    "Variables, Constants, and Data Types": (
        "VARIABLES, CONSTANTS, AND DATA TYPES",
        "A variable stores a value. A constant is a value "
        "that should not change. In Python, uppercase names "
        "are commonly used for constants.",
        '''name = "Alex"
age = 17

PI = 3.14159

print(name)
print(age)
print(PI)''',
        '''Alex
17
3.14159'''
    ),
    "Basic Data Types in Python": (
        "BASIC DATA TYPES IN PYTHON",
        "Python has different data types:\n\n"
        "int - whole numbers\n"
        "float - decimal numbers\n"
        "str - text\n"
        "bool - True or False",
        '''number = 10
price = 25.50
message = "Hello"
is_ready = True

print(type(number))
print(type(price))
print(type(message))
print(type(is_ready))''',
        '''<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>'''
    ),
    "Arithmetic Operators and Expressions": (
        "CHAPTER 3: ARITHMETIC OPERATORS AND EXPRESSIONS",
        "Arithmetic operators perform mathematical operations.\n\n"
        "+ Addition\n"
        "- Subtraction\n"
        "* Multiplication\n"
        "/ Division\n"
        "// Floor Division\n"
        "% Modulus (remainder)\n"
        "** Exponentiation",
        '''a = 10
b = 3

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)''',
        '''13
7
30
3.3333333333333335
3
1
1000'''
    ),
    "Basic Input and Output": (
        "CHAPTER 4: BASIC INPUT AND OUTPUT",
        "The input() function accepts information from the user. "
        "The print() function displays information.\n\n"
        "The input() function returns a string. Use int() "
        "or float() to convert input into a number.",
        '''name = input("Enter your name: ")
age = int(input("Enter your age: "))

print("Hello,", name)
print("Next year:", age + 1)''',
        '''Enter your name: Alex
Enter your age: 17
Hello, Alex
Next year: 18'''
    ),
    "Conditional Statements": (
        "MIDTERM: CONDITIONAL STATEMENTS",
        "Conditional statements allow a program to make decisions.\n\n"
        "if - checks a condition\n"
        "elif - checks another condition\n"
        "else - runs when the conditions are False",
        '''score = int(input("Enter your score: "))

if score >= 90:
    print("Excellent")

elif score >= 75:
    print("Passed")

else:
    print("Needs improvement")''',
        '''Enter your score: 85
Passed'''
    ),
    "Logical Operators": (
        "MIDTERM: LOGICAL OPERATORS",
        "Logical operators combine conditions.\n\n"
        "and - both conditions must be True\n"
        "or - at least one condition must be True\n"
        "not - reverses the Boolean value",
        '''age = 17
has_id = True

print(age >= 18 and has_id)
print(age >= 18 or has_id)
print(not has_id)''',
        '''False
True
False'''
    ),
    "Iteration and Loops": (
        "FINALS: INTRODUCTION TO ITERATION AND LOOPS",
        "A loop repeats a block of code.\n\n"
        "for loop - repeats through a sequence or range\n"
        "while loop - repeats while a condition is True\n\n"
        "Loops help reduce repeated code.",
        '''for number in range(1, 4):
    print(number)

count = 1

while count <= 3:
    print("Count:", count)
    count += 1''',
        '''1
2
3
Count: 1
Count: 2
Count: 3'''
    )
}


REQUIRE_EXERCISE_TO_CONTINUE = False
RUN_TIMEOUT = 5

practice_passed = {}

exercises = {
    "Introduction to Programming": {
        "task": "Print the text Welcome to programming. on the screen.",
        "tests": [("", "Welcome to programming.")],
    },
    "Python Basic Syntax": {
        "task": "Assign the text John to first_name and print the value of "
                "first_name.\n\nUse only the Python syntax you have learned so far.",
        "tests": [("", "John")],
    },
    "Printing Output": {
        "task": "Use print() to display the result of 10 + 5.",
        "tests": [("", "15")],
    },
    "Python Comments": {
        "task": "Write a comment, then assign the text Alex to a variable "
                "named name and print it.",
        "tests": [("", "Alex")],
    },
    "Variables, Constants, and Data Types": {
        "task": "Assign 17 to a variable named age, then print age.",
        "tests": [("", "17")],
    },
    "Basic Data Types in Python": {
        "task": "Assign 25.5 to a variable named price, then print "
                "the data type of price using type().",
        "tests": [("", "<class 'float'>")],
    },
    "Arithmetic Operators and Expressions": {
        "task": "Assign 20 to a and 6 to b. Print a // b on the first line "
                "and a % b on the second line.",
        "tests": [("", "3\n2")],
    },
    "Basic Input and Output": {
        "task": "Use input() (with nothing inside the parentheses) to get a "
                "name, then print Hello, followed by a space and the name.",
        "tests": [("Alex", "Hello, Alex"), ("Maria", "Hello, Maria")],
    },
    "Conditional Statements": {
        "task": "Get a score using input() and convert it to an integer. "
                "Print Passed if the score is 75 or higher, otherwise print "
                "Needs improvement.",
        "tests": [("85", "Passed"), ("75", "Passed"), ("60", "Needs improvement")],
    },
    "Logical Operators": {
        "task": "Assign 20 to age and True to has_id. Then print the result of "
                "age >= 18 and has_id.",
        "tests": [("", "True")],
    },
    "Iteration and Loops": {
        "task": "Use a for loop with range() to print the numbers 1 to 5, "
                "one number per line.",
        "tests": [("", "1\n2\n3\n4\n5")],
    },
}


def passed_set():
    return practice_passed.setdefault(current_user, set())


def can_continue(topic_name):
    if not REQUIRE_EXERCISE_TO_CONTINUE or topic_name not in exercises:
        return True
    return topic_name in passed_set()


def run_python(code, stdin_text):
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            input=stdin_text, capture_output=True, text=True,
            timeout=RUN_TIMEOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", f"Stopped: the program ran longer than {RUN_TIMEOUT} seconds."


def same_output(got, expected):
    clean = lambda s: [line.rstrip() for line in s.strip().splitlines()]
    return clean(got) == clean(expected)


def read_set():
    return lessons_read.setdefault(current_user, set())


def is_unlocked(topic_name):
    names = list(topics)
    idx = names.index(topic_name)
    return all(n in read_set() for n in names[:idx])


def first_unread_before(topic_name):
    names = list(topics)
    for n in names[:names.index(topic_name)]:
        if n not in read_set():
            return n
    return None


def all_lessons_read():
    return all(n in read_set() for n in topics)


BG = "#0B1712"
SIDEBAR = "#0F1F18"
CARD = "#14271E"
CARD_HOVER = "#1C3629"
INPUT = "#1A3126"
BORDER = "#27463A"
CODE_BG = "#08110D"
CODE_HEAD = "#0D1B14"

TEXT = "#EAF4EF"
MUTED = "#8DA89B"
ACCENT = "#2FD9A4"
ACCENT_HOVER = "#5BE8BD"
ON_ACCENT = "#06251B"
DANGER = "#FF7A7A"
WARN = "#F5C26B"
OUTPUT_TEXT = "#9FE8C8"

UI = "Segoe UI"
MONO = "Consolas"

root = tk.Tk()
root.title("PyCharm Reviewer")
root.geometry("1000x700")
root.minsize(850, 600)
root.configure(bg=BG)


class FlatButton(tk.Label):

    def __init__(self, parent, text, command, kind="primary",
                 font_size=10, weight="bold", padx=18, pady=9, **kw):
        styles = {
            "primary": (ACCENT, ON_ACCENT, ACCENT_HOVER),
            "secondary": (CARD, TEXT, CARD_HOVER),
            "danger": ("#3A1E22", DANGER, "#4A252A"),
            "ghost": (parent.cget("bg"), MUTED, CARD),
            "nav": (SIDEBAR, MUTED, CARD),
            "nav_active": (CARD, ACCENT, CARD),
            "nav_locked": (SIDEBAR, "#3F5A4D", SIDEBAR),
            "dot_done": (CARD, ACCENT, CARD_HOVER),
            "dot_todo": (INPUT, MUTED, CARD_HOVER),
            "dot_locked": (CODE_HEAD, "#3F5A4D", CODE_HEAD),
        }
        normal_bg, fg, hover_bg = styles[kind]
        super().__init__(
            parent, text=text, bg=normal_bg, fg=fg,
            font=(UI, font_size, weight), padx=padx, pady=pady,
            cursor="hand2", **kw
        )
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        self.on_click = command
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.normal_bg))
        self.bind("<Button-1>", lambda e: self.on_click())


class ScrollFrame(tk.Frame):

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(
            self, bg=bg, highlightthickness=0, bd=0, yscrollincrement=24
        )
        self.bar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )
        self.wrapped = []

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind("<Configure>", self._on_resize)

    def wrap(self, label, margin=0):
        self.wrapped.append((label, margin))
        return label

    def _on_resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)
        for label, margin in self.wrapped:
            label.configure(wraplength=max(200, event.width - margin))


def on_mousewheel(event):
    try:
        widget = root.winfo_containing(event.x_root, event.y_root)
    except (KeyError, tk.TclError):
        return

    while widget is not None:
        if isinstance(widget, ScrollFrame):
            if event.num == 4:
                step = -3
            elif event.num == 5:
                step = 3
            else:
                step = -3 if event.delta > 0 else 3
            widget.canvas.yview_scroll(step, "units")
            return
        widget = widget.master


root.bind_all("<MouseWheel>", on_mousewheel)
root.bind_all("<Button-4>", on_mousewheel)
root.bind_all("<Button-5>", on_mousewheel)


def autowrap(container, label, margin=0):
    container.bind(
        "<Configure>",
        lambda e: label.config(wraplength=max(200, e.width - margin)),
        add="+"
    )


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def new_screen():
    clear_screen()
    screen = tk.Frame(root, bg=BG)
    screen.pack(fill="both", expand=True)
    return screen


def show_toast(message, ms=2000):
    toast = tk.Label(
        root, text="\u2713  " + message, font=(UI, 12, "bold"),
        fg=ON_ACCENT, bg=ACCENT, padx=24, pady=12
    )
    toast.place(relx=0.5, rely=0.0, y=20, anchor="n")
    toast.lift()
    root.after(ms, lambda: toast.winfo_exists() and toast.destroy())


def make_field(parent, label, hidden=False):
    tk.Label(
        parent, text=label, font=(UI, 10), fg=MUTED,
        bg=parent.cget("bg"), anchor="w"
    ).pack(fill="x", pady=(9, 4))

    entry = tk.Entry(
        parent, font=(UI, 12), bg=INPUT, fg=TEXT,
        insertbackground=TEXT, relief="flat", bd=0,
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT, show="\u2022" if hidden else ""
    )
    entry.pack(fill="x", ipady=7)
    return entry


def auth_shell(title, subtitle):
    screen = new_screen()
    screen.grid_columnconfigure(1, weight=1)
    screen.grid_rowconfigure(0, weight=1)

    brand = tk.Frame(screen, bg=SIDEBAR, width=400)
    brand.grid(row=0, column=0, sticky="ns")
    brand.pack_propagate(False)

    tk.Label(
        brand, text="FINAL PRESENTATION",
        font=(UI, 14, "bold"), fg=ACCENT, bg=SIDEBAR
    ).pack(anchor="w", padx=40, pady=(40, 0))

    tk.Label(
        brand, text="Learn Basic Python with me.",
        font=(UI, 26, "bold"), fg=TEXT, bg=SIDEBAR,
        justify="left", anchor="w", wraplength=320
    ).pack(anchor="w", padx=40, pady=(40, 10))

    tk.Label(
        brand,
        text="A beginner-friendly reviewer. Read each lesson, try the "
             "sample code, then test yourself with a timed quiz.",
        font=(UI, 11), fg=MUTED, bg=SIDEBAR,
        justify="left", anchor="w", wraplength=320
    ).pack(anchor="w", padx=40, pady=(0, 24))

    info_rows = [
        (f"{len(topics)} lessons",
         "From programming basics to loops"),
        ("Basic exercise",
         "Practice coding after every lesson"),
        (f"{len(quiz_questions)}-question quiz",
         f"{QUESTION_SECONDS} seconds for each question"),
        ("Certificate by email",
         f"Score {PASSING_PERCENTAGE}% or higher to earn it"),
        ("Step-by-step unlocking",
         "Finish a lesson to open the next one"),
    ]

    for heading_text, detail_text in info_rows:
        row = tk.Frame(brand, bg=SIDEBAR)
        row.pack(fill="x", padx=40, pady=7)
        tk.Frame(row, bg=ACCENT, width=3).pack(side="left", fill="y")
        text_box = tk.Frame(row, bg=SIDEBAR)
        text_box.pack(side="left", padx=12)
        tk.Label(
            text_box, text=heading_text, font=(UI, 12, "bold"),
            fg=TEXT, bg=SIDEBAR, anchor="w"
        ).pack(fill="x")
        tk.Label(
            text_box, text=detail_text, font=(UI, 10),
            fg=MUTED, bg=SIDEBAR, anchor="w"
        ).pack(fill="x")

    tk.Label(
        brand, text="Python for beginners  \u2022  Final Presentation",
        font=(UI, 9), fg="#3F5A4D", bg=SIDEBAR, anchor="w"
    ).pack(side="bottom", anchor="w", padx=40, pady=20)

    right = tk.Frame(screen, bg=BG)
    right.grid(row=0, column=1, sticky="nsew")

    form = tk.Frame(right, bg=BG)
    form.place(relx=0.5, rely=0.5, anchor="center", width=360)

    tk.Label(
        form, text=title, font=(UI, 22, "bold"),
        fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x")
    tk.Label(
        form, text=subtitle, font=(UI, 11),
        fg=MUTED, bg=BG, anchor="w"
    ).pack(fill="x", pady=(2, 8))

    return form


def create_account_screen():
    form = auth_shell("Create your account", "Sign Up to Access My Lessons")

    full_name_entry = make_field(form, "Full Name ( Surname, Given Name ):")
    username_entry = make_field(form, "Username:")
    password_entry = make_field(
        form, "Password (at least 8 letters or numbers):", hidden=True
    )
    confirm_entry = make_field(form, "Confirm password:", hidden=True)
    gmail_entry = make_field(form, "Gmail (required, used to send your certificate):")

    def register():
        full_name = full_name_entry.get().strip()
        username = username_entry.get().strip().lower()
        password = password_entry.get()
        confirm = confirm_entry.get()
        gmail = gmail_entry.get().strip()

        if not full_name or not username or not password or not confirm:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all required fields."
            )
            return

        if len(password) < MIN_PASSWORD_LENGTH or not password.isalnum():
            messagebox.showerror(
                "Invalid Password",
                f"Your password must be at least {MIN_PASSWORD_LENGTH} characters "
                "and use only letters and numbers."
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Registration Failed",
                "Passwords do not match."
            )
            return

        if get_user(username) is not None:
            messagebox.showerror(
                "Registration Failed",
                "Username already exists."
            )
            return

        if gmail and ("@" not in gmail or "." not in gmail.split("@")[-1]):
            messagebox.showerror(
                "Invalid Gmail",
                "Please enter a valid email address or leave it blank."
            )
            return

        if not create_user(full_name, username, password, gmail):
            messagebox.showerror(
                "Registration Failed",
                "Username already exists."
            )
            return

        messagebox.showinfo(
            "Success",
            "Account created successfully! You can now login."
        )
        login_screen()

    for entry in (full_name_entry, username_entry, password_entry,
                  confirm_entry, gmail_entry):
        entry.bind("<Return>", lambda e: register())

    FlatButton(
        form, "Create account", register, kind="primary", pady=11
    ).pack(fill="x", pady=(20, 8))

    FlatButton(
        form, "I already have an account", login_screen,
        kind="ghost", weight="normal"
    ).pack(fill="x")

    full_name_entry.focus_set()


def login_screen():
    form = auth_shell("Log in", "Enter your account details.")

    username_entry = make_field(form, "Username:")
    password_entry = make_field(form, "Password:", hidden=True)

    def login():
        global current_user

        username = username_entry.get().strip().lower()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password."
            )
            return

        user = get_user(username)

        if user is None:
            messagebox.showerror(
                "Login Failed",
                "Username does not exist."
            )
            return

        if verify_password(
            password, user["password_hash"], user["salt"], user["iterations"]
        ):
            current_user = username
            load_progress(username)
            main_menu()
            show_toast("LOG IN SUCCESSFUL")
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect password."
            )

    username_entry.bind("<Return>", lambda e: password_entry.focus_set())
    password_entry.bind("<Return>", lambda e: login())

    FlatButton(
        form, "Log in", login, kind="primary", pady=11
    ).pack(fill="x", pady=(20, 8))

    FlatButton(
        form, "Create a new account", create_account_screen,
        kind="ghost", weight="normal"
    ).pack(fill="x")

    username_entry.focus_set()


def topic_card(parent, number, name, command, locked=False, done=False):
    card = tk.Frame(
        parent, bg=CARD, cursor="arrow" if locked else "hand2",
        highlightthickness=1, highlightbackground=BORDER
    )
    if locked:
        badge_text, badge_fg, title_fg = "\U0001F512", "#3F5A4D", MUTED
    elif done:
        badge_text, badge_fg, title_fg = "\u2713", ACCENT, TEXT
    else:
        badge_text, badge_fg, title_fg = str(number), ACCENT, TEXT

    badge = tk.Label(
        card, text=badge_text, font=(UI, 16, "bold"),
        fg=badge_fg, bg=CARD, width=3,
        cursor="arrow" if locked else "hand2"
    )
    badge.pack(side="left", padx=(8, 0), pady=14)

    title = tk.Label(
        card, text=name, font=(UI, 11, "bold"), fg=title_fg, bg=CARD,
        anchor="w", justify="left", wraplength=300,
        cursor="arrow" if locked else "hand2"
    )
    title.pack(side="left", fill="x", expand=True, padx=(4, 12))

    parts = (card, badge, title)

    def enter(_):
        if not locked:
            for part in parts:
                part.config(bg=CARD_HOVER)

    def leave(_):
        for part in parts:
            part.config(bg=CARD)

    for part in parts:
        part.bind("<Enter>", enter)
        part.bind("<Leave>", leave)
        part.bind("<Button-1>", lambda e: command())

    return card


def main_menu():
    screen = new_screen()

    full_name = get_user(current_user)["full_name"]

    bar = tk.Frame(screen, bg=SIDEBAR)
    bar.pack(fill="x")

    tk.Label(
        bar, text="PyCharm Reviewer", font=(UI, 14, "bold"),
        fg=ACCENT, bg=SIDEBAR
    ).pack(side="left", padx=24, pady=14)

    FlatButton(
        bar, "Log out", logout, kind="primary", padx=16, pady=6
    ).pack(side="right", padx=16, pady=8)

    tk.Label(
        bar, text=full_name, font=(UI, 10), fg=MUTED, bg=SIDEBAR
    ).pack(side="right", padx=4)

    body = tk.Frame(screen, bg=BG)
    body.pack(fill="both", expand=True, padx=40, pady=24)

    head = tk.Frame(body, bg=BG)
    head.pack(fill="x")

    greeting = tk.Frame(head, bg=BG)
    greeting.pack(side="left")

    tk.Label(
        greeting, text=f"Hi, {given_name(full_name)}",
        font=(UI, 22, "bold"), fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x")
    tk.Label(
        greeting, text="Choose a lesson. ( click to discuss )",
        font=(UI, 11), fg=MUTED, bg=BG, anchor="w"
    ).pack(fill="x")
    tk.Label(
        greeting,
        text=f"Progress: {len(read_set())}/{len(topics)} lessons read",
        font=(UI, 10), fg=ACCENT, bg=BG, anchor="w"
    ).pack(fill="x")

    FlatButton(
        head, "START EXERCISE QUIZ", start_quiz, kind="primary", pady=10
    ).pack(side="right")
    FlatButton(
        head, "READ ALL TOPICS", show_all_topics, kind="secondary", pady=10
    ).pack(side="right", padx=10)

    grid = tk.Frame(body, bg=BG)
    grid.pack(fill="both", expand=True, pady=(20, 0))
    grid.grid_columnconfigure(0, weight=1, uniform="topic")
    grid.grid_columnconfigure(1, weight=1, uniform="topic")

    for i, topic_name in enumerate(topics):
        card = topic_card(
            grid, i + 1, topic_name,
            lambda name=topic_name: show_topic(name),
            locked=not is_unlocked(topic_name),
            done=topic_name in read_set()
        )
        card.grid(row=i // 2, column=i % 2, sticky="ew", padx=5, pady=5)


def copy_code(button, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    button.config(text="Copied")
    root.after(
        1400,
        lambda: button.winfo_exists() and button.config(text="Copy")
    )


def code_block(parent, label, text, color, copyable=False):
    block = tk.Frame(
        parent, bg=CODE_BG, highlightthickness=1, highlightbackground=BORDER
    )
    block.pack(fill="x", pady=(6, 16))

    head = tk.Frame(block, bg=CODE_HEAD)
    head.pack(fill="x")

    tk.Label(
        head, text=label, font=(UI, 9, "bold"), fg=MUTED, bg=CODE_HEAD
    ).pack(side="left", padx=14, pady=6)

    if copyable:
        button = FlatButton(
            head, "Copy", None, kind="ghost",
            font_size=9, padx=10, pady=3
        )
        button.on_click = lambda: copy_code(button, text)
        button.pack(side="right", padx=6, pady=3)

    tk.Label(
        block, text=text, font=(MONO, 12), fg=color, bg=CODE_BG,
        justify="left", anchor="w", padx=16, pady=14
    ).pack(fill="x")


def practice_panel(parent, scroll, name):
    tests = exercises[name]["tests"]
    first_input, first_expected = tests[0]

    box = tk.Frame(
        parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER
    )
    box.pack(fill="x", pady=(8, 20))
    inner = tk.Frame(box, bg=CARD)
    inner.pack(fill="x", padx=18, pady=16)

    tk.Label(
        inner, text="BASIC EXERCISE", font=(UI, 10, "bold"),
        fg=ACCENT, bg=CARD, anchor="w"
    ).pack(fill="x")

    scroll.wrap(tk.Label(
        inner, text=exercises[name]["task"], font=(UI, 12, "bold"),
        fg=TEXT, bg=CARD, anchor="w", justify="left"
    ), 130).pack(fill="x", pady=(6, 10))

    sample_in = first_input.replace("\n", ", ") or "No input required"
    scroll.wrap(tk.Label(
        inner, text=f"Test input: {sample_in}\nExpected output:\n{first_expected}",
        font=(UI, 11, "bold"), fg=TEXT, bg=CARD, anchor="w", justify="left"
    ), 130).pack(fill="x", pady=(0, 10))

    tk.Label(
        inner, text="PYTHON EDITOR", font=(UI, 9, "bold"),
        fg=MUTED, bg=CARD, anchor="w"
    ).pack(fill="x")

    editor = tk.Text(
        inner, height=8, font=(MONO, 12), bg=CODE_BG, fg=TEXT,
        insertbackground=TEXT, relief="flat", bd=0, padx=14, pady=12,
        undo=True, wrap="none", highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=ACCENT
    )
    editor.pack(fill="x", pady=(4, 10))
    editor.bind("<Tab>", lambda e: (editor.insert("insert", "    "), "break")[1])

    output_label = tk.Label(
        inner, text="Output will appear here.", font=(MONO, 11),
        fg=MUTED, bg=CODE_BG, anchor="w", justify="left", padx=14, pady=10
    )
    output_label.pack(fill="x", pady=(0, 10))

    buttons = tk.Frame(inner, bg=CARD)
    buttons.pack(fill="x")

    status = tk.Label(
        buttons,
        text="\u2713 Completed" if name in passed_set() else "",
        font=(UI, 11, "bold"), fg=ACCENT, bg=CARD,
        anchor="w", justify="left", wraplength=420
    )

    def run(check):
        code = editor.get("1.0", "end")
        has_code = any(
            line.strip() and not line.strip().startswith("#")
            for line in code.splitlines()
        )
        if not has_code:
            messagebox.showwarning("No Code", "Write your program first.")
            return

        status.config(text="Running...", fg=MUTED)
        run_tests = tests if check else tests[:1]
        outcome = {}

        def worker():
            outcome["runs"] = [run_python(code, i) for i, _ in run_tests]

        def poll():
            if not status.winfo_exists():
                return
            if "runs" not in outcome:
                root.after(150, poll)
                return

            runs = outcome["runs"]
            shown_out, shown_err = runs[0]
            verdict, verdict_color = "", MUTED

            if check:
                verdict, verdict_color = (
                    f"\u2713 Correct! All {len(tests)} test(s) passed.", ACCENT
                )
                for n, ((_, expected), (out, err)) in enumerate(zip(tests, runs), 1):
                    if err.strip():
                        shown_out, shown_err = out, err
                        verdict, verdict_color = (
                            f"\u2717 Test {n} has an error. Read the message above.",
                            DANGER
                        )
                        break
                    if not same_output(out, expected):
                        shown_out, shown_err = out, ""
                        verdict, verdict_color = (
                            f"\u2717 Test {n} failed.\nExpected: {expected!r}\n"
                            f"Your output: {out.strip()!r}", DANGER
                        )
                        break
                if verdict_color == ACCENT:
                    mark_practice(name)
                    verdict += " Great job!"

            if shown_err.strip():
                output_label.config(text=shown_err.strip(), fg=DANGER)
            else:
                output_label.config(
                    text=shown_out.rstrip() or "(no output)", fg=OUTPUT_TEXT
                )
            status.config(text=verdict, fg=verdict_color)

        threading.Thread(target=worker, daemon=True).start()
        poll()

    FlatButton(
        buttons, "Run code", lambda: run(False), kind="secondary", pady=8
    ).pack(side="left")
    FlatButton(
        buttons, "Check answer", lambda: run(True), kind="primary", pady=8
    ).pack(side="left", padx=10)
    status.pack(side="left", padx=8)


def render_lesson(scroll, number, name, practice=False):
    title, discussion, code, output = topics[name]
    tag = title.split(":")[0].title() if ":" in title else ""

    page = tk.Frame(scroll.inner, bg=BG)
    page.pack(fill="x", padx=36, pady=(26, 10))

    if tag:
        tk.Label(
            page, text=tag, font=(UI, 10, "bold"),
            fg=ACCENT, bg=BG, anchor="w"
        ).pack(fill="x")

    heading = scroll.wrap(tk.Label(
        page, text=f"{number}. {name}", font=(UI, 22, "bold"),
        fg=TEXT, bg=BG, anchor="w", justify="left"
    ), 72)
    heading.pack(fill="x", pady=(2, 14))

    tk.Label(
        page, text="Discussion", font=(UI, 11, "bold"),
        fg=MUTED, bg=BG, anchor="w"
    ).pack(fill="x", pady=(0, 4))

    discussion_label = scroll.wrap(tk.Label(
        page, text=discussion, font=(UI, 12), fg=TEXT, bg=BG,
        anchor="w", justify="left"
    ), 72)
    discussion_label.pack(fill="x", pady=(0, 14))

    code_block(page, "Python code", code, TEXT, copyable=True)
    code_block(page, "Sample output", output, OUTPUT_TEXT)

    if practice and name in exercises:
        practice_panel(page, scroll, name)


def show_topic(topic_name):
    if not is_unlocked(topic_name):
        needed = first_unread_before(topic_name)
        messagebox.showwarning(
            "Lesson Locked",
            f"Read \"{needed}\" first, then press Next lesson to unlock this one."
        )
        return

    screen = new_screen()
    names = list(topics)
    idx = names.index(topic_name)

    sidebar = tk.Frame(screen, bg=SIDEBAR, width=270)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    FlatButton(
        sidebar, "\u2190 All lessons", main_menu,
        kind="ghost", weight="normal"
    ).pack(anchor="w", padx=12, pady=(14, 8))

    for i, name in enumerate(names):
        active = i == idx
        locked = not is_unlocked(name)
        mark = "  \U0001F512" if locked else ("  \u2713" if name in read_set() else "")
        FlatButton(
            sidebar, f"{i + 1}.  {name}{mark}",
            lambda n=name: show_topic(n),
            kind="nav_active" if active else ("nav_locked" if locked else "nav"),
            weight="bold" if active else "normal",
            padx=14, pady=7, anchor="w", justify="left", wraplength=225
        ).pack(fill="x", padx=10, pady=1)

    main = tk.Frame(screen, bg=BG)
    main.pack(side="left", fill="both", expand=True)

    footer = tk.Frame(main, bg=SIDEBAR)
    footer.pack(side="bottom", fill="x")

    scroll = ScrollFrame(main)
    scroll.pack(fill="both", expand=True)
    render_lesson(scroll, idx + 1, topic_name, practice=True)

    def go_next():
        if not can_continue(topic_name):
            messagebox.showinfo(
                "Try it yourself",
                "Solve the exercise at the bottom of the lesson "
                "(press Check answer) to continue."
            )
            return
        mark_read(topic_name)
        show_topic(names[idx + 1])

    def go_quiz():
        if not can_continue(topic_name):
            messagebox.showinfo(
                "Try it yourself",
                "Solve the exercise at the bottom of the lesson "
                "(press Check answer) to take the quiz."
            )
            return
        mark_read(topic_name)
        start_quiz()

    if idx > 0:
        FlatButton(
            footer, "Previous lesson",
            lambda: show_topic(names[idx - 1]), kind="secondary"
        ).pack(side="left", padx=24, pady=12)

    if idx < len(names) - 1:
        FlatButton(
            footer, "Next lesson", go_next, kind="primary"
        ).pack(side="right", padx=24, pady=12)
    else:
        FlatButton(
            footer, "Take the quiz", go_quiz, kind="primary"
        ).pack(side="right", padx=24, pady=12)


def show_all_topics():
    screen = new_screen()

    bar = tk.Frame(screen, bg=SIDEBAR)
    bar.pack(fill="x")

    FlatButton(
        bar, "\u2190 All lessons", main_menu, kind="ghost", weight="normal"
    ).pack(side="left", padx=12, pady=10)

    tk.Label(
        bar, text="Every lesson in one page",
        font=(UI, 12, "bold"), fg=TEXT, bg=SIDEBAR
    ).pack(side="left", padx=8)

    scroll = ScrollFrame(screen)
    scroll.pack(fill="both", expand=True)

    shown = 0
    for i, name in enumerate(topics):
        if not is_unlocked(name):
            break
        if shown > 0:
            tk.Frame(scroll.inner, bg=BORDER, height=1).pack(
                fill="x", padx=36, pady=(8, 0)
            )
        render_lesson(scroll, i + 1, name)
        shown += 1

    if shown < len(topics):
        tk.Label(
            scroll.inner,
            text="\U0001F512 The remaining lessons unlock as you finish each one.",
            font=(UI, 11), fg=MUTED, bg=BG
        ).pack(pady=24)


quiz_questions = [
    {
        "question": "What is programming?",
        "options": [
            "Giving instructions to a computer",
            "Designing computer hardware",
            "Repairing computer components",
            "Connecting computers to a network"
        ],
        "answer": 0,
        "explanation": "Programming means writing instructions that a computer can execute."
    },
    {
        "question": "Which Python function displays information on the screen?",
        "options": [
            "input()",
            "print()",
            "type()",
            "int()"
        ],
        "answer": 1,
        "explanation": "The print() function displays text, numbers, and other information."
    },
    {
        "question": "Which symbol starts a single-line comment in Python?",
        "options": [
            "//",
            "#",
            "@",
            "&"
        ],
        "answer": 1,
        "explanation": "The # symbol is used to start a single-line comment in Python."
    },
    {
        "question": "What is the data type of 25.5?",
        "options": [
            "int",
            "str",
            "float",
            "bool"
        ],
        "answer": 2,
        "explanation": "A float is a number that can contain a decimal point."
    },
    {
        "question": "What is the result of 10 // 3?",
        "options": [
            "3.33",
            "1",
            "4",
            "3"
        ],
        "answer": 3,
        "explanation": "The // operator performs floor division, so 10 // 3 equals 3."
    },
    {
        "question": "Which function accepts information from the user?",
        "options": [
            "print()",
            "input()",
            "type()",
            "str()"
        ],
        "answer": 1,
        "explanation": "The input() function accepts information entered by the user."
    },
    {
        "question": "What is the main purpose of an if statement?",
        "options": [
            "To repeat code",
            "To make decisions based on conditions",
            "To display output",
            "To store multiple values"
        ],
        "answer": 1,
        "explanation": "An if statement checks a condition and runs code depending on the result."
    },
    {
        "question": "Which of these is a logical operator in Python?",
        "options": [
            "and",
            "print",
            "input",
            "range"
        ],
        "answer": 0,
        "explanation": "and is a logical operator. The other choices are functions or built-in names."
    },
    {
        "question": "What does the not operator do?",
        "options": [
            "Adds two numbers",
            "Repeats a statement",
            "Reverses a Boolean value",
            "Displays a message"
        ],
        "answer": 2,
        "explanation": "The not operator reverses a Boolean value: True becomes False, and False becomes True."
    },
    {
        "question": "Which loop is commonly used to repeat code while a condition is True?",
        "options": [
            "if",
            "elif",
            "while",
            "print"
        ],
        "answer": 2,
        "explanation": "A while loop continues running as long as its condition is True."
    },
    {
        "question": "What is the output of this code?\n\nfor number in range(1, 4):\n    print(number)",
        "options": [
            "1 2 3",
            "1 2 3 4",
            "0 1 2 3",
            "3 2 1"
        ],
        "answer": 0,
        "explanation": "range(1, 4) generates 1, 2, and 3. The ending value 4 is not included."
    },
    {
        "question": "Which of the following is a valid variable name in Python?",
        "options": [
            "2name",
            "user_name",
            "user-name",
            "class"
        ],
        "answer": 1,
        "explanation": "Variable names can contain letters, numbers, and underscores, but cannot start with a number or use reserved keywords."
    },
    {
        "question": "What data type is the value True?",
        "options": [
            "str",
            "int",
            "bool",
            "float"
        ],
        "answer": 2,
        "explanation": "True and False are Boolean values. Their data type is bool."
    },
    {
        "question": "What is the result of 8 + 4 * 2?",
        "options": [
            "24",
            "16",
            "20",
            "12"
        ],
        "answer": 1,
        "explanation": "Multiplication comes first: 4 * 2 = 8, then 8 + 8 = 16."
    },
    {
        "question": "Which statement assigns the value 10 to a variable named score?",
        "options": [
            "score == 10",
            "10 = score",
            "score = 10",
            "score : 10"
        ],
        "answer": 2,
        "explanation": "The = operator assigns a value to a variable."
    }
]

quiz_answers = [None] * len(quiz_questions)
quiz_index = 0

QUESTION_SECONDS = 15
TIMED_OUT = -1
quiz_time_left = QUESTION_SECONDS
quiz_timer_job = None
timer_ui = {}


def timer_color(seconds_left):
    if seconds_left <= 3:
        return DANGER
    if seconds_left <= 5:
        return WARN
    return ACCENT


def stop_quiz_timer():
    global quiz_timer_job

    if quiz_timer_job is not None:
        root.after_cancel(quiz_timer_job)
        quiz_timer_job = None


def start_question_timer():
    global quiz_time_left, quiz_timer_job

    stop_quiz_timer()
    quiz_time_left = QUESTION_SECONDS
    quiz_timer_job = root.after(1000, tick_quiz_timer)


def update_timer_display():
    color = timer_color(quiz_time_left)
    label = timer_ui.get("label")
    fill = timer_ui.get("fill")

    if label is not None and label.winfo_exists():
        label.config(text=f"{quiz_time_left}s", fg=color)
    if fill is not None and fill.winfo_exists():
        fill.config(bg=color)
        fill.place_configure(relwidth=quiz_time_left / QUESTION_SECONDS)


def tick_quiz_timer():
    global quiz_time_left, quiz_timer_job

    quiz_time_left -= 1
    update_timer_display()

    if quiz_time_left <= 0:
        quiz_timer_job = None
        time_is_up()
    else:
        quiz_timer_job = root.after(1000, tick_quiz_timer)


def time_is_up():
    if quiz_answers[quiz_index] is None:
        quiz_answers[quiz_index] = TIMED_OUT
    advance_quiz()


def advance_quiz():
    global quiz_index

    if quiz_index < len(quiz_questions) - 1:
        quiz_index += 1
        start_question_timer()
        show_quiz_question()
    else:
        stop_quiz_timer()
        show_quiz_result()


def start_quiz():
    if REQUIRE_ALL_LESSONS_FOR_QUIZ and not all_lessons_read():
        messagebox.showwarning(
            "Quiz Locked",
            "Read all lessons first (press Next lesson on each one) to unlock the quiz."
        )
        return

    stop_quiz_timer()
    screen = new_screen()

    bar = tk.Frame(screen, bg=SIDEBAR)
    bar.pack(fill="x")

    tk.Label(
        bar, text="Exercise Quiz", font=(UI, 14, "bold"),
        fg=ACCENT, bg=SIDEBAR
    ).pack(side="left", padx=24, pady=14)

    FlatButton(
        bar, "Back to lessons", main_menu, kind="primary", padx=16, pady=6
    ).pack(side="right", padx=16, pady=8)

    card = tk.Frame(screen, bg=BG)
    card.place(relx=0.5, rely=0.5, anchor="center", width=580)

    head = tk.Frame(card, bg=BG)
    head.pack(fill="x", pady=(0, 18))

    tk.Label(
        head, text=str(QUESTION_SECONDS), font=(UI, 56, "bold"),
        fg=ACCENT, bg=BG
    ).pack(side="left", padx=(0, 18))

    head_text = tk.Frame(head, bg=BG)
    head_text.pack(side="left")
    tk.Label(
        head_text, text="seconds for each question",
        font=(UI, 18, "bold"), fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x")
    tk.Label(
        head_text, text="Read this before you begin.",
        font=(UI, 11), fg=MUTED, bg=BG, anchor="w"
    ).pack(fill="x")

    rules = [
        f"The timer starts as soon as a question appears. You have "
        f"{QUESTION_SECONDS} seconds to answer it.",
        "Choose an answer, then press Next. You can change your answer "
        "until time runs out.",
        "When time runs out, the quiz moves to the next question on its own. "
        "A question with no answer counts as wrong.",
        "You can't skip a question or go back to an earlier one.",
        f"Score {PASSING_PERCENTAGE}% or higher to get your certificate by email.",
    ]

    for rule in rules:
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", pady=4)
        tk.Frame(row, bg=ACCENT, width=4).pack(side="left", fill="y")
        tk.Label(
            row, text=rule, font=(UI, 11), fg=TEXT, bg=CARD,
            anchor="w", justify="left", wraplength=520, padx=14, pady=10
        ).pack(side="left", fill="x", expand=True)

    FlatButton(
        card, "Start Quiz", begin_quiz, kind="primary", pady=11
    ).pack(fill="x", pady=(20, 0))


def begin_quiz():
    global quiz_answers, quiz_index

    quiz_answers = [None] * len(quiz_questions)
    quiz_index = 0

    start_question_timer()
    show_quiz_question()


def select_answer(option_number):
    quiz_answers[quiz_index] = option_number
    show_quiz_question()


def next_question():
    if quiz_answers[quiz_index] is None:
        messagebox.showwarning(
            "No Answer",
            "Please select an answer before continuing."
        )
        return

    advance_quiz()


def show_quiz_question():
    screen = new_screen()

    total = len(quiz_questions)
    question_data = quiz_questions[quiz_index]
    color = timer_color(quiz_time_left)

    bar = tk.Frame(screen, bg=SIDEBAR)
    bar.pack(fill="x")

    tk.Label(
        bar, text="Exercise quiz", font=(UI, 14, "bold"),
        fg=ACCENT, bg=SIDEBAR
    ).pack(side="left", padx=24, pady=14)

    FlatButton(
        bar, "Leave Quiz", confirm_exit_quiz, kind="primary", padx=16, pady=6
    ).pack(side="right", padx=16, pady=8)

    track = tk.Frame(screen, bg=BORDER, height=4)
    track.pack(fill="x")
    fill = tk.Frame(track, bg=color)
    fill.place(
        relx=0, rely=0, relwidth=quiz_time_left / QUESTION_SECONDS, relheight=1
    )
    timer_ui["fill"] = fill

    footer = tk.Frame(screen, bg=SIDEBAR)
    footer.pack(side="bottom", fill="x")

    if quiz_index < total - 1:
        FlatButton(
            footer, "Next", next_question, kind="primary"
        ).pack(side="right", padx=24, pady=12)
    else:
        FlatButton(
            footer, "Submit quiz", finish_quiz, kind="primary"
        ).pack(side="right", padx=24, pady=12)

    content = tk.Frame(screen, bg=BG)
    content.pack(fill="both", expand=True, padx=48, pady=20)

    info = tk.Frame(content, bg=BG)
    info.pack(fill="x")
    tk.Label(
        info, text=f"Question {quiz_index + 1} of {total}",
        font=(UI, 11, "bold"), fg=TEXT, bg=BG
    ).pack(side="left")

    timer_label = tk.Label(
        info, text=f"{quiz_time_left}s", font=(UI, 18, "bold"),
        fg=color, bg=BG
    )
    timer_label.pack(side="right")
    timer_ui["label"] = timer_label

    dots = tk.Frame(content, bg=BG)
    dots.pack(fill="x", pady=(12, 0))
    for i in range(total):
        if i == quiz_index:
            kind = "primary"
        elif quiz_answers[i] is not None:
            kind = "dot_done"
        else:
            kind = "dot_locked"
        dot = FlatButton(
            dots, str(i + 1), lambda: None,
            kind=kind, font_size=9, padx=7, pady=4
        )
        dot.config(cursor="arrow")
        dot.hover_bg = dot.normal_bg
        dot.pack(side="left", padx=(0, 4))

    prompt, _, code = question_data["question"].partition("\n\n")

    prompt_label = tk.Label(
        content, text=prompt, font=(UI, 17, "bold"), fg=TEXT, bg=BG,
        anchor="w", justify="left", wraplength=780
    )
    prompt_label.pack(fill="x", pady=(24, 8))
    autowrap(content, prompt_label, 0)

    if code:
        tk.Label(
            content, text=code, font=(MONO, 12), fg=TEXT, bg=CODE_BG,
            anchor="w", justify="left", padx=16, pady=12
        ).pack(fill="x", pady=(0, 8))

    options = tk.Frame(content, bg=BG)
    options.pack(fill="x", pady=(8, 0))

    for n, option_text in enumerate(question_data["options"]):
        chosen = quiz_answers[quiz_index] == n
        card_bg = CARD_HOVER if chosen else CARD

        card = tk.Frame(
            options, bg=card_bg, cursor="hand2",
            highlightthickness=2 if chosen else 1,
            highlightbackground=ACCENT if chosen else BORDER
        )
        card.pack(fill="x", pady=5)

        letter = tk.Label(
            card, text=chr(65 + n), font=(UI, 11, "bold"), width=3,
            fg=ON_ACCENT if chosen else MUTED,
            bg=ACCENT if chosen else INPUT, cursor="hand2"
        )
        letter.pack(side="left", fill="y")

        text_label = tk.Label(
            card, text=option_text, font=(UI, 12), fg=TEXT, bg=card_bg,
            anchor="w", justify="left", padx=14, pady=12,
            wraplength=720, cursor="hand2"
        )
        text_label.pack(side="left", fill="x", expand=True)
        autowrap(content, text_label, 90)

        def enter(_, c=card, t=text_label, on=chosen):
            if not on:
                c.config(bg=CARD_HOVER)
                t.config(bg=CARD_HOVER)

        def leave(_, c=card, t=text_label, on=chosen):
            if not on:
                c.config(bg=CARD)
                t.config(bg=CARD)

        for part in (card, letter, text_label):
            part.bind("<Enter>", enter)
            part.bind("<Leave>", leave)
            part.bind("<Button-1>", lambda e, num=n: select_answer(num))


def finish_quiz():
    if quiz_answers[quiz_index] is None:
        messagebox.showwarning(
            "No Answer",
            "Please select an answer before submitting."
        )
        return

    stop_quiz_timer()
    show_quiz_result()


def confirm_exit_quiz():
    answer = messagebox.askyesno(
        "Leave quiz",
        "Are you sure you want to leave the quiz? Your current answers will be lost."
    )

    if answer:
        stop_quiz_timer()
        main_menu()


def given_name(full_name):
    if "," in full_name:
        rest = full_name.split(",", 1)[1].strip()
        if rest:
            return rest.split()[0]
    return full_name.split()[0]


def display_name(full_name):
    if "," in full_name:
        surname, given = [part.strip() for part in full_name.split(",", 1)]
        if surname and given:
            return f"{given} {surname}"
    return full_name.strip()


import io
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

CREAM = HexColor("#F2FAF5")
GOLD = HexColor("#1E9E72")
GOLD_LIGHT = HexColor("#8FE3C0")
GOLD_DARK = HexColor("#12624A")
BLACK = HexColor("#0B2B20")
GRAY = HexColor("#2B4A3D")


_NAME_FONT = None


def _name_font():
    global _NAME_FONT
    if _NAME_FONT:
        return _NAME_FONT
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates = [
        ("SegoeScript", os.path.join(windir, "Fonts", "segoesc.ttf")),
        ("BrushScript", os.path.join(windir, "Fonts", "BRUSHSCI.TTF")),
        ("Corsiva", os.path.join(windir, "Fonts", "MTCORSVA.TTF")),
        ("Corsiva", "/System/Library/Fonts/Supplemental/Apple Chancery.ttf"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                _NAME_FONT = name
                return name
            except Exception:
                pass
    _NAME_FONT = "Times-BoldItalic"
    return _NAME_FONT


def _swoosh(c, w, h, flip):
    c.saveState()
    if flip:
        c.translate(w, h)
        c.rotate(180)

    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(0, h)
    p.lineTo(w * 0.52, h)
    p.curveTo(w * 0.34, h - 20, w * 0.16, h - 62, 0, h - 215)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.setFillColor(GOLD_LIGHT)
    p = c.beginPath()
    p.moveTo(0, h)
    p.lineTo(w * 0.40, h)
    p.curveTo(w * 0.26, h - 14, w * 0.11, h - 52, 0, h - 170)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.setFillColor(BLACK)
    p = c.beginPath()
    p.moveTo(0, h)
    p.lineTo(w * 0.34, h)
    p.curveTo(w * 0.21, h - 10, w * 0.08, h - 40, 0, h - 130)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    for k in range(1, 6):
        d = k * 9
        c.bezier(0, h - 120 + d * 0.2, w * 0.07, h - 36 - d * 0.1,
                 w * 0.18, h - 8 - d * 0.1, w * 0.32 - d * 0.5, h - 2 - d * 0.25)

    c.setStrokeColor(GOLD_LIGHT)
    c.setFillColor(GOLD_LIGHT)
    c.setLineWidth(1.2)
    c.bezier(26, h - 70, 40, h - 110, 62, h - 138, 52, h - 185)
    for (x, y, a) in [(34, h - 95, 30), (42, h - 120, 20), (48, h - 150, 10),
                      (24, h - 86, 80), (36, h - 132, 70)]:
        c.saveState()
        c.translate(x, y)
        c.rotate(a)
        lp = c.beginPath()
        lp.moveTo(0, 0)
        lp.curveTo(8, 6, 16, 4, 20, 0)
        lp.curveTo(16, -4, 8, -6, 0, 0)
        c.drawPath(lp, stroke=0, fill=1)
        c.restoreState()
    c.restoreState()


def _corner_frame(c, x, y, sx, sy, size=70):
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.8)
    c.line(x, y, x + sx * size, y)
    c.line(x, y, x, y + sy * size)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(x + sx * 6, y + sy * 6, x + sx * (size - 10), y + sy * 6)
    c.line(x + sx * 6, y + sy * 6, x + sx * 6, y + sy * (size - 10))


def _seal(c, cx, cy):
    c.setFillColor(BLACK)
    for dx in (-17, 4):
        p = c.beginPath()
        p.moveTo(cx + dx, cy - 18)
        p.lineTo(cx + dx + 13, cy - 18)
        p.lineTo(cx + dx + 13, cy - 62)
        p.lineTo(cx + dx + 6.5, cy - 52)
        p.lineTo(cx + dx, cy - 62)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    import math
    c.setFillColor(BLACK)
    p = c.beginPath()
    n = 28
    for i in range(n * 2):
        r = 40 if i % 2 == 0 else 35
        a = math.pi * i / n
        pt = (cx + r * math.cos(a), cy + r * math.sin(a))
        p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    c.setFillColor(GOLD_DARK)
    c.circle(cx, cy, 31, stroke=0, fill=1)
    c.setFillColor(GOLD_LIGHT)
    c.circle(cx, cy, 26, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.circle(cx, cy, 20, stroke=0, fill=1)
    c.setFillColor(HexColor("#C9F5E1"))
    c.circle(cx - 5, cy + 6, 8, stroke=0, fill=1)


def _fit(c, text, font, size, max_w):
    while size > 14 and c.stringWidth(text, font, size) > max_w:
        size -= 1
    return size


def _wrap(c, text, font, size, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if c.stringWidth(trial, font, size) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _spaced(c, x, y, text, font, size, space, align="center"):
    width = c.stringWidth(text, font, size) + space * (len(text) - 1)
    if align == "center":
        x -= width / 2
    elif align == "right":
        x -= width
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.textOut(text)
    t.setCharSpace(0)
    c.drawText(t)


def _mixed(c, cx, y, parts, size):
    fonts = {False: "Times-Roman", True: "Times-Bold"}
    total = sum(c.stringWidth(t, fonts[b], size) for t, b in parts)
    x = cx - total / 2
    for t, b in parts:
        c.setFont(fonts[b], size)
        c.drawString(x, y, t)
        x += c.stringWidth(t, fonts[b], size)


def build_certificate_pdf(person_name, score, total, percentage,
                          date_text, cert_id, lessons):
    buf = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setTitle("Certificate of Completion")
    c.setAuthor("PyCharm Reviewer")

    DARK = HexColor("#0B2B20")
    GREEN = HexColor("#1E9E72")
    LIGHT = HexColor("#8FE3C0")
    MINT = HexColor("#F2FAF5")
    TEXTC = HexColor("#1E3A2F")
    DEEP = HexColor("#12624A")
    GRAYG = HexColor("#5B6F65")

    cx = w / 2
    m = 22
    c.setFillColor(DARK)
    c.roundRect(m, m, w - 2 * m, h - 2 * m, 10, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.rect(m + 12, m + 12, w - 2 * m - 24, h - 2 * m - 24, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.rect(m + 14, m + 14, w - 2 * m - 28, h - 2 * m - 28, stroke=0, fill=1)

    c.setFillColor(DARK)
    _spaced(c, cx, h - 120, "CERTIFICATE", "Times-Bold", 50, 7)
    c.setFillColor(GREEN)
    _spaced(c, cx, h - 156, "OF COMPLETION", "Times-Bold", 15, 5)

    c.setFillColor(DARK)
    c.setFont("Times-Bold", 13)
    c.drawCentredString(cx, h - 214, "This certificate is proudly presented to")

    size = _fit(c, person_name, "Times-BoldItalic", 44, w - 220)
    c.setFillColor(GREEN)
    c.setFont("Times-BoldItalic", size)
    c.drawCentredString(cx, h - 268, person_name)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1)
    c.line(cx - 170, h - 284, cx + 170, h - 284)

    c.setFillColor(TEXTC)
    _mixed(c, cx, h - 326,
           [("For successfully completing the ", False),
            ("PYCHARM REVIEWER", True), (" quiz,", False)], 14)
    _mixed(c, cx, h - 348,
           [(f"covering {lessons} lessons of Basic Python, with a score of ", False),
            (f"{score}/{total} ({percentage:.0f}%)", True), (".", False)], 14)

    honor = "WITH EXCELLENCE" if percentage >= 90 else "PASSED WITH MERIT"
    c.setFillColor(DEEP)
    _spaced(c, cx, h - 392, honor, "Helvetica-Bold", 11, 4)

    left, right = m + 62, w - m - 62
    c.setStrokeColor(LIGHT)
    c.setLineWidth(1)
    c.line(left, 118, right, 118)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, 92, date_text)
    c.drawRightString(right, 92, cert_id)
    c.setFillColor(GRAYG)
    _spaced(c, left, 76, "DATE ISSUED", "Helvetica", 8, 2, "left")
    _spaced(c, right, 76, "CERTIFICATE ID", "Helvetica", 8, 2, "right")

    c.showPage()
    c.save()
    return buf.getvalue()


def build_certificate_content(full_name, score, total, percentage):
    person = display_name(full_name)
    name = escape(person)
    first = escape(full_name.strip())
    date_text = datetime.now().strftime("%B %d, %Y")
    cert_id = "PYR-" + uuid.uuid4().hex[:8].upper()
    honor = "WITH EXCELLENCE" if percentage >= 90 else "PASSED WITH MERIT"
    lessons = len(topics)

    pdf_bytes = build_certificate_pdf(
        person, score, total, percentage, date_text, cert_id, lessons
    )

    plain_text = (
        f"CONGRATULATIONS, {full_name.strip().upper()}!\n\n"
        f"You passed the PYCHARM REVIEWER QUIZ with a score of "
        f"{score}/{total} ({percentage:.0f}%).\n\n"
        f"Your certificate is attached to this email as a PDF.\n\n"
        f"CERTIFICATE OF COMPLETION\n"
        f"Presented to: {person}\n"
        f"Score: {score}/{total} ({percentage:.1f}%) - {honor}\n"
        f"Date: {date_text}\n"
        f"Certificate ID: {cert_id}\n"
    )

    png_bytes = None
    fallback_block = f"""
  <tr><td>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           bgcolor="#0B2B20" style="background:#0B2B20;border-radius:6px;">
      <tr><td style="padding:8px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
               bgcolor="#F2FAF5" style="background:#F2FAF5;border:2px solid #1E9E72;">
          <tr><td align="center" style="padding:40px 34px 12px 34px;">
            <div style="font-family:Georgia,'Times New Roman',serif;font-size:42px;
                        font-weight:bold;letter-spacing:4px;color:#0B2B20;line-height:46px;">CERTIFICATE</div>
            <div style="font-family:Georgia,'Times New Roman',serif;font-size:17px;
                        letter-spacing:3px;color:#1E9E72;font-weight:bold;margin-top:6px;">OF COMPLETION</div>

            <div style="font-family:Georgia,'Times New Roman',serif;font-size:13px;
                        color:#0B2B20;font-weight:bold;margin-top:34px;">
              This certificate is proudly presented to
            </div>

            <div style="margin:18px 0 18px 0;">
              <span style="display:inline-block;font-family:Georgia,'Times New Roman',serif;
                           font-size:34px;font-style:italic;font-weight:bold;color:#1E9E72;
                           border-bottom:1px solid #1E9E72;padding:2px 20px 6px 20px;">{name}</span>
            </div>

            <div style="font-family:Georgia,'Times New Roman',serif;font-size:14px;
                        line-height:1.7;color:#1E3A2F;">
              For successfully completing the <b>PYCHARM REVIEWER</b> quiz,<br>
              covering {lessons} lessons of Basic Python, with a score of
              <b>{score}/{total} ({percentage:.0f}%)</b>.
            </div>

            <div style="font-size:12px;letter-spacing:4px;color:#12624A;font-weight:bold;margin-top:18px;">
              {honor}
            </div>
          </td></tr>

          <tr><td style="padding:22px 34px 26px 34px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="border-top:1px solid #8FE3C0;">
              <tr>
                <td align="left" style="padding-top:14px;font-size:13px;color:#0B2B20;">
                  <b>{date_text}</b><br>
                  <span style="font-size:10px;letter-spacing:2px;color:#12624A;">DATE ISSUED</span>
                </td>
                <td align="right" style="padding-top:14px;font-size:13px;color:#0B2B20;">
                  <b>{cert_id}</b><br>
                  <span style="font-size:10px;letter-spacing:2px;color:#12624A;">CERTIFICATE ID</span>
                </td>
              </tr>
            </table>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </td></tr>

"""
    cert_block = (
        '<tr><td align="center"><img src="cid:certimg" alt="Certificate" '
        'style="width:100%;max-width:560px;height:auto;display:block;'
        'border-radius:6px;"></td></tr>'
        if png_bytes else fallback_block
    )

    html_body = f"""
<div style="margin:0;padding:24px 12px;background:#EEF4F1;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="max-width:640px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;">

  <tr><td style="padding:0 0 18px 0;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           bgcolor="#FFFFFF" style="background:#FFFFFF;border-left:6px solid #2FD9A4;border-radius:10px;">
      <tr><td style="padding:24px 28px;">
        <div style="font-size:30px;line-height:34px;">&#127881;</div>
        <h1 style="margin:8px 0 10px 0;font-size:26px;color:#0F1F18;">Congratulations, {first}!</h1>
        <p style="margin:0 0 10px 0;font-size:15px;line-height:1.65;color:#33463D;">
          You passed the <b>PYCHARM REVIEWER</b> quiz with a score of
          <b>{score}/{total} ({percentage:.0f}%)</b>. All the time you spent reading
          the lessons and practicing the code really paid off.
        </p>
        <p style="margin:0;font-size:15px;line-height:1.65;color:#33463D;">
          Your certificate is below, and a <b>PDF copy is attached</b> to this email.
          Keep it, print it, or share it with pride. Keep learning and keep coding!
        </p>
      </td></tr>
    </table>
  </td></tr>

{cert_block}

  <tr><td align="center" style="padding:16px 8px 0 8px;font-size:12px;color:#7A8F85;">
    This is an automated message from PyCharm Reviewer.
  </td></tr>
</table>
</div>
"""
    return plain_text, html_body, pdf_bytes, cert_id, png_bytes


def send_certificate_email(receiver_email, full_name, score, total, percentage):
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:
        return False, (
            "The Gmail sender is not configured. Set EMAIL_SENDER and "
            "EMAIL_APP_PASSWORD in your computer's environment variables."
        )

    if len(EMAIL_APP_PASSWORD) != 16:
        return False, "The sender's Google App Password must be 16 characters."

    plain_text, html_body, pdf_bytes, cert_id, png_bytes = build_certificate_content(
        full_name, score, total, percentage
    )

    message = EmailMessage()
    message["Subject"] = "Congratulations! Your PYCHARM REVIEWER Certificate"
    message["From"] = EMAIL_SENDER
    message["To"] = receiver_email
    message.set_content(plain_text)
    message.add_alternative(html_body, subtype="html")
    if png_bytes:
        message.get_body(preferencelist=("html",)).add_related(
            png_bytes, maintype="image", subtype="png", cid="<certimg>"
        )

    safe_name = display_name(full_name).replace(" ", "_").replace(",", "")
    message.add_attachment(
        pdf_bytes, maintype="application", subtype="pdf",
        filename=f"Certificate_{safe_name}_{cert_id}.pdf"
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=20) as server:
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.send_message(message)
        return True, f"Certificate (with PDF) sent to {receiver_email}."
    except smtplib.SMTPAuthenticationError:
        return False, (
            "Gmail login failed. Check the sender Gmail and its 16-character "
            "Google App Password. 2-Step Verification must be enabled."
        )
    except (OSError, smtplib.SMTPException) as error:
        return False, f"Could not send the certificate: {error}"


def show_quiz_result():
    screen = new_screen()

    score = sum(
        1 for index, answer in enumerate(quiz_answers)
        if answer == quiz_questions[index]["answer"]
    )

    total = len(quiz_questions)
    percentage = (score / total) * 100
    passed = percentage >= PASSING_PERCENTAGE
    ring_color = ACCENT if passed else WARN

    footer = tk.Frame(screen, bg=SIDEBAR)
    footer.pack(side="bottom", fill="x")

    FlatButton(
        footer, "Retake quiz", start_quiz, kind="primary"
    ).pack(side="right", padx=24, pady=12)
    FlatButton(
        footer, "Back to lessons:", main_menu, kind="secondary"
    ).pack(side="right", pady=12)

    head = tk.Frame(screen, bg=BG)
    head.pack(fill="x", padx=40, pady=(24, 10))

    ring = tk.Canvas(
        head, width=140, height=140, bg=BG, highlightthickness=0
    )
    ring.pack(side="left")
    ring.create_oval(12, 12, 128, 128, outline=BORDER, width=10)
    if percentage > 0:
        ring.create_arc(
            12, 12, 128, 128, start=90,
            extent=-min(359.9, 360 * percentage / 100),
            style="arc", outline=ring_color, width=10
        )
    ring.create_text(
        70, 62, text=f"{score}/{total}", font=(UI, 22, "bold"), fill=TEXT
    )
    ring.create_text(
        70, 90, text=f"{percentage:.0f}%", font=(UI, 11), fill=MUTED
    )

    info = tk.Frame(head, bg=BG)
    info.pack(side="left", fill="x", expand=True, padx=(28, 0))

    tk.Label(
        info, text="Quiz complete", font=(UI, 24, "bold"),
        fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x")

    if percentage >= 90:
        remark = "Excellent! You have a strong understanding of Python."
    elif percentage >= 75:
        remark = "Good job! Keep reviewing the lessons."
    elif percentage >= 50:
        remark = "Nice try! Review the topics and practice more."
    else:
        remark = "Keep studying! You can improve with more practice."

    tk.Label(
        info, text=remark, font=(UI, 12), fg=MUTED, bg=BG,
        anchor="w", justify="left", wraplength=600
    ).pack(fill="x", pady=(2, 8))

    if passed:
        user = get_user(current_user)
        receiver_email = user["gmail"].strip()

        if not receiver_email:
            tk.Label(
                info,
                text="You passed, but your account has no Gmail address, so no certificate was sent.",
                font=(UI, 11, "bold"), fg=ACCENT, bg=BG,
                anchor="w", justify="left", wraplength=600
            ).pack(fill="x")
        else:
            status = tk.Label(
                info, text=f"Sending certificate to {receiver_email}...",
                font=(UI, 11, "bold"), fg=MUTED, bg=BG,
                anchor="w", justify="left", wraplength=600
            )
            status.pack(fill="x")

            full_name = user["full_name"]
            outcome = {}

            def worker():
                outcome["result"] = send_certificate_email(
                    receiver_email, full_name, score, total, percentage
                )

            def poll():
                if not status.winfo_exists():
                    return
                if "result" in outcome:
                    sent, result_message = outcome["result"]
                    status.config(
                        text=result_message,
                        fg=ACCENT if sent else DANGER
                    )
                else:
                    root.after(200, poll)

            threading.Thread(target=worker, daemon=True).start()
            poll()
    else:
        tk.Label(
            info,
            text=f"You need {PASSING_PERCENTAGE}% or higher to earn a certificate. Review the lessons and try again.",
            font=(UI, 11, "bold"), fg=WARN, bg=BG,
            anchor="w", justify="left", wraplength=600
        ).pack(fill="x")

    tk.Label(
        screen, text="Review your answers", font=(UI, 13, "bold"),
        fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x", padx=40, pady=(10, 6))

    review = ScrollFrame(screen)
    review.pack(fill="both", expand=True, padx=(40, 30), pady=(0, 10))

    for index, question_data in enumerate(quiz_questions):
        chosen = quiz_answers[index]
        correct = question_data["answer"]
        is_correct = chosen == correct
        status_color = ACCENT if is_correct else DANGER

        row = tk.Frame(review.inner, bg=CARD)
        row.pack(fill="x", pady=5, padx=(0, 10))

        tk.Frame(row, bg=status_color, width=5).pack(side="left", fill="y")

        body = tk.Frame(row, bg=CARD)
        body.pack(side="left", fill="x", expand=True, padx=16, pady=12)

        tk.Label(
            body,
            text=f"Question {index + 1}: {'Correct' if is_correct else 'Incorrect'}",
            font=(UI, 10, "bold"), fg=status_color, bg=CARD, anchor="w"
        ).pack(fill="x")

        if chosen == TIMED_OUT:
            your_answer = "No answer (time ran out)"
        else:
            your_answer = question_data["options"][chosen]

        lines = [
            (question_data["question"], (UI, 12, "bold"), TEXT),
            (f"Your answer: {your_answer}", (UI, 11), DANGER if chosen == TIMED_OUT else TEXT),
        ]
        if not is_correct:
            lines.append((
                f"Correct answer: {question_data['options'][correct]}",
                (UI, 11), ACCENT
            ))
        lines.append((question_data["explanation"], (UI, 10), MUTED))

        for text, font, color in lines:
            label = tk.Label(
                body, text=text, font=font, fg=color, bg=CARD,
                anchor="w", justify="left"
            )
            label.pack(fill="x", pady=(3, 0))
            review.wrap(label, 130)


def logout():
    global current_user

    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to logout?"
    )

    if answer:
        current_user = None

        messagebox.showinfo(
            "Logout",
            "You have successfully logged out."
        )

        login_screen()


init_db()
create_account_screen()
root.mainloop()