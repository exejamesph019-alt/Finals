import tkinter as tk
from tkinter import messagebox
import os
import ssl
import smtplib
import threading
from email.message import EmailMessage
from html import escape

# Set these as environment variables on your computer. Never write the
# password directly in the code.
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "exejamesph019@gmail.com").strip()
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "ofik ympa pbmx hqys").replace(" ", "").strip()
PASSING_PERCENTAGE = 75
MIN_PASSWORD_LENGTH = 8

user_full_names = []
user_usernames = []
user_passwords = []
user_gmails = []

current_user = None

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

# ---------------------------------------------------------------------------
# Design tokens: deep emerald surfaces, one mint accent, Segoe UI + Consolas
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------
class FlatButton(tk.Label):
    """A flat, hoverable button built on a Label so colors work on every OS."""

    def __init__(self, parent, text, command, kind="primary",
                 font_size=10, weight="bold", padx=18, pady=9, **kw):
        styles = {
            "primary": (ACCENT, ON_ACCENT, ACCENT_HOVER),
            "secondary": (CARD, TEXT, CARD_HOVER),
            "danger": ("#3A1E22", DANGER, "#4A252A"),
            "ghost": (parent.cget("bg"), MUTED, CARD),
            "nav": (SIDEBAR, MUTED, CARD),
            "nav_active": (CARD, ACCENT, CARD),
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
    """A vertically scrolling container. Add widgets to `.inner`."""

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
        """Keep a label's wrap width in step with the window width."""
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
    """Split layout shared by the create account and login screens."""
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
    ).pack(anchor="w", padx=40, pady=(60, 12))

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


# ---------------------------------------------------------------------------
# Account screens
# ---------------------------------------------------------------------------
def create_account_screen():
    form = auth_shell("Create your account", "Sign Up to Access My Lessons")

    full_name_entry = make_field(form, "Full Name ( Surname, Given Name ):")
    username_entry = make_field(form, "Username:")
    password_entry = make_field(
        form, "Password (at least 8 letters or numbers):", hidden=True
    )
    confirm_entry = make_field(form, "Confirm password:", hidden=True)
    gmail_entry = make_field(form, "Gmail (optional, used to send your certificate):")

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

        if username in user_usernames:
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

        user_full_names.append(full_name)
        user_usernames.append(username)
        user_passwords.append(password)
        user_gmails.append(gmail)

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

        if username not in user_usernames:
            messagebox.showerror(
                "Login Failed",
                "Username does not exist."
            )
            return

        index = user_usernames.index(username)

        if user_passwords[index] == password:
            current_user = username
            main_menu()
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


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
def topic_card(parent, number, name, command):
    card = tk.Frame(
        parent, bg=CARD, cursor="hand2",
        highlightthickness=1, highlightbackground=BORDER
    )
    badge = tk.Label(
        card, text=str(number), font=(UI, 16, "bold"),
        fg=ACCENT, bg=CARD, width=3, cursor="hand2"
    )
    badge.pack(side="left", padx=(8, 0), pady=14)

    title = tk.Label(
        card, text=name, font=(UI, 11, "bold"), fg=TEXT, bg=CARD,
        anchor="w", justify="left", wraplength=300, cursor="hand2"
    )
    title.pack(side="left", fill="x", expand=True, padx=(4, 12))

    parts = (card, badge, title)

    def enter(_):
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

    index = user_usernames.index(current_user)
    full_name = user_full_names[index]

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
        greeting, text=f"Hi, {full_name.split()[0]}",
        font=(UI, 22, "bold"), fg=TEXT, bg=BG, anchor="w"
    ).pack(fill="x")
    tk.Label(
        greeting, text="Choose a lesson. ( click to discuss )",
        font=(UI, 11), fg=MUTED, bg=BG, anchor="w"
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
            lambda name=topic_name: show_topic(name)
        )
        card.grid(row=i // 2, column=i % 2, sticky="ew", padx=5, pady=5)


# ---------------------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------------------
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


def render_lesson(scroll, number, name):
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


def show_topic(topic_name):
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
        FlatButton(
            sidebar, f"{i + 1}.  {name}",
            lambda n=name: show_topic(n),
            kind="nav_active" if active else "nav",
            weight="bold" if active else "normal",
            padx=14, pady=7, anchor="w", justify="left", wraplength=225
        ).pack(fill="x", padx=10, pady=1)

    main = tk.Frame(screen, bg=BG)
    main.pack(side="left", fill="both", expand=True)

    footer = tk.Frame(main, bg=SIDEBAR)
    footer.pack(side="bottom", fill="x")

    scroll = ScrollFrame(main)
    scroll.pack(fill="both", expand=True)
    render_lesson(scroll, idx + 1, topic_name)

    if idx > 0:
        FlatButton(
            footer, "Previous lesson",
            lambda: show_topic(names[idx - 1]), kind="secondary"
        ).pack(side="left", padx=24, pady=12)

    if idx < len(names) - 1:
        FlatButton(
            footer, "Next lesson",
            lambda: show_topic(names[idx + 1]), kind="primary"
        ).pack(side="right", padx=24, pady=12)
    else:
        FlatButton(
            footer, "Take the quiz", start_quiz, kind="primary"
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

    for i, name in enumerate(topics):
        if i > 0:
            tk.Frame(scroll.inner, bg=BORDER, height=1).pack(
                fill="x", padx=36, pady=(8, 0)
            )
        render_lesson(scroll, i + 1, name)


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------
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
    """Show the quiz guide. The quiz begins when the person presses Start."""
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

    # The bar under the title shrinks as the time for this question runs out.
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


def send_certificate_email(receiver_email, full_name, score, total, percentage):
    """Send a completion certificate to the Gmail entered during registration."""
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:
        return False, (
            "The Gmail sender is not configured. Set EMAIL_SENDER and "
            "EMAIL_APP_PASSWORD in your computer's environment variables."
        )

    if len(EMAIL_APP_PASSWORD) != 16:
        return False, "The sender's Google App Password must be 16 characters."

    safe_name = escape(full_name)
    subject = "Your PYCHARM REVIEWER Certificate"
    plain_text = (
        f"CERTIFICATE OF COMPLETION\n\n"
        f"This certifies that {full_name} completed the PYCHARM REVIEWER quiz.\n"
        f"Score: {score}/{total} ({percentage:.1f}%).\n"
        f"Congratulations!"
    )
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
                padding:30px;border:6px double {ACCENT};text-align:center;">
      <h1 style="color:{ACCENT};">CERTIFICATE OF COMPLETION</h1>
      <p>This certificate is proudly presented to</p>
      <h2>{safe_name}</h2>
      <p>for successfully completing the <b>PYCHARM REVIEWER</b> quiz.</p>
      <h3>Score: {score}/{total} ({percentage:.1f}%)</h3>
      <p>Congratulations on your achievement!</p>
    </div>
    """

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = receiver_email
    message.set_content(plain_text)
    message.add_alternative(html_body, subtype="html")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=20) as server:
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.send_message(message)
        return True, f"Certificate sent to {receiver_email}."
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
        user_index = user_usernames.index(current_user)
        receiver_email = user_gmails[user_index].strip()

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

            full_name = user_full_names[user_index]
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


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
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


create_account_screen()
root.mainloop()