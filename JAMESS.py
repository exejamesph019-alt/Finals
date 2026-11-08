
import tkinter as tk
from tkinter import messagebox

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


root = tk.Tk()
root.title("PYCHARM REVIEWER - Python Programming Lessons")
root.geometry("1000x700")
root.minsize(850, 600)
root.configure(bg="#1e1e2e")


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def create_header(parent, title, subtitle=None):
    tk.Label(
        parent,
        text=title,
        font=("Arial", 23, "bold"),
        fg="white",
        bg="#1e1e2e"
    ).pack(pady=(20, 5))

    if subtitle:
        tk.Label(
            parent,
            text=subtitle,
            font=("Arial", 11),
            fg="#bac2de",
            bg="#1e1e2e"
        ).pack(pady=(0, 15))


def create_account_screen():
    clear_screen()

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(expand=True)

    create_header(frame, "CREATE ACCOUNT", "Register to access PYCHARM REVIEWER")

    entries = {}

    fields = [
        ("Full Name", "full_name", False),
        ("Username", "username", False),
        ("Password", "password", True),
        ("Confirm Password", "confirm", True),
        ("Gmail (Optional)", "gmail", False)
    ]

    for label, key, hidden in fields:
        tk.Label(
            frame,
            text=label,
            font=("Arial", 11),
            fg="white",
            bg="#1e1e2e"
        ).pack(anchor="w")

        entry = tk.Entry(
            frame,
            font=("Arial", 12),
            width=32,
            show="*" if hidden else ""
        )
        entry.pack(pady=(4, 10))
        entries[key] = entry

    def register():
        full_name = entries["full_name"].get().strip()
        username = entries["username"].get().strip().lower()
        password = entries["password"].get()
        confirm = entries["confirm"].get()
        gmail = entries["gmail"].get().strip()

        if not full_name or not username or not password or not confirm:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all required fields."
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

    tk.Button(
        frame,
        text="CREATE ACCOUNT",
        font=("Arial", 11, "bold"),
        bg="#89b4fa",
        fg="#1e1e2e",
        width=27,
        height=2,
        command=register
    ).pack(pady=12)

    tk.Button(
        frame,
        text="Already have an account? Login",
        font=("Arial", 10),
        bg="#1e1e2e",
        fg="white",
        bd=0,
        command=login_screen
    ).pack()


def login_screen():
    clear_screen()

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(expand=True)

    create_header(frame, "LOGIN", "Enter your account details")

    tk.Label(
        frame,
        text="Username",
        fg="white",
        bg="#1e1e2e"
    ).pack()

    username_entry = tk.Entry(frame, font=("Arial", 12), width=32)
    username_entry.pack(pady=(4, 12))

    tk.Label(
        frame,
        text="Password",
        fg="white",
        bg="#1e1e2e"
    ).pack()

    password_entry = tk.Entry(
        frame,
        font=("Arial", 12),
        width=32,
        show="*"
    )
    password_entry.pack(pady=(4, 12))

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
            messagebox.showinfo("Welcome", "Login successful!")
            main_menu()
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect password."
            )

    tk.Button(
        frame,
        text="LOGIN",
        font=("Arial", 11, "bold"),
        bg="#a6e3a1",
        fg="#1e1e2e",
        width=27,
        height=2,
        command=login
    ).pack(pady=12)

    tk.Button(
        frame,
        text="Create a new account",
        font=("Arial", 10),
        bg="#1e1e2e",
        fg="white",
        bd=0,
        command=create_account_screen
    ).pack()


def main_menu():
    clear_screen()

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(fill="both", expand=True)

    index = user_usernames.index(current_user)
    full_name = user_full_names[index]

    create_header(frame, "PYCHARM REVIEWER", f"Welcome, {full_name}!")

    tk.Label(
        frame,
        text="SELECT A PYTHON TOPIC",
        font=("Arial", 15, "bold"),
        fg="#89b4fa",
        bg="#1e1e2e"
    ).pack(pady=10)

    content = tk.Frame(frame, bg="#1e1e2e")
    content.pack(fill="both", expand=True, padx=35, pady=5)

    for i, topic_name in enumerate(topics):
        tk.Button(
            content,
            text=topic_name,
            font=("Arial", 10, "bold"),
            bg="#313244",
            fg="white",
            width=38,
            height=2,
            command=lambda name=topic_name: show_topic(name)
        ).grid(row=i // 2, column=i % 2, padx=8, pady=6, sticky="ew")

    content.grid_columnconfigure(0, weight=1)
    content.grid_columnconfigure(1, weight=1)

    tk.Button(
        frame,
        text="DISCUSS ALL TOPICS",
        font=("Arial", 10, "bold"),
        bg="#0f766e",
        fg="white",
        width=25,
        height=2,
        command=show_all_topics
    ).pack(pady=8)

    tk.Button(
        frame,
        text="TAKE A QUIZ",
        font=("Arial", 10, "bold"),
        bg="#cba6f7",
        fg="#1e1e2e",
        width=25,
        height=2,
        command=start_quiz
    ).pack(pady=8)

    tk.Button(
        frame,
        text="LOGOUT",
        font=("Arial", 10, "bold"),
        bg="#f38ba8",
        fg="#1e1e2e",
        width=20,
        height=2,
        command=logout
    ).pack(pady=(4, 15))


def show_topic(topic_name):
    clear_screen()

    title, discussion, code, output = topics[topic_name]

    header = tk.Frame(root, bg="#1e1e2e")
    header.pack(fill="x")

    tk.Label(
        header,
        text=title,
        font=("Arial", 18, "bold"),
        fg="#89b4fa",
        bg="#1e1e2e",
        wraplength=900
    ).pack(pady=18)

    content = tk.Frame(root, bg="#1e1e2e")
    content.pack(fill="both", expand=True, padx=25, pady=8)

    text_frame = tk.Frame(content)
    text_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    text_area = tk.Text(
        text_frame,
        font=("Consolas", 11),
        wrap="word",
        yscrollcommand=scrollbar.set,
        padx=15,
        pady=15,
        bg="#11111b",
        fg="#cdd6f4"
    )
    text_area.pack(fill="both", expand=True)
    scrollbar.config(command=text_area.yview)

    text_area.insert("end", "DISCUSSION:\n")
    text_area.insert("end", discussion + "\n\n")
    text_area.insert("end", "PYTHON CODE:\n")
    text_area.insert("end", code + "\n\n")
    text_area.insert("end", "SAMPLE OUTPUT:\n")
    text_area.insert("end", output + "\n")
    text_area.config(state="disabled")

    tk.Button(
        content,
        text="BACK TO MAIN MENU",
        font=("Arial", 10, "bold"),
        bg="#89b4fa",
        fg="#1e1e2e",
        command=main_menu
    ).pack(pady=12)


def show_all_topics():
    clear_screen()

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(fill="both", expand=True, padx=20, pady=15)

    create_header(frame, "ALL PYTHON TOPICS", "Complete reviewer")

    text_frame = tk.Frame(frame)
    text_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    text_area = tk.Text(
        text_frame,
        font=("Consolas", 10),
        wrap="word",
        yscrollcommand=scrollbar.set,
        padx=15,
        pady=15,
        bg="#11111b",
        fg="#cdd6f4"
    )
    text_area.pack(fill="both", expand=True)
    scrollbar.config(command=text_area.yview)

    for topic_name, data in topics.items():
        title, discussion, code, output = data

        text_area.insert("end", "=" * 60 + "\n")
        text_area.insert("end", title.upper() + "\n")
        text_area.insert("end", "=" * 60 + "\n\n")
        text_area.insert("end", "DISCUSSION:\n")
        text_area.insert("end", discussion + "\n\n")
        text_area.insert("end", "PYTHON CODE:\n")
        text_area.insert("end", code + "\n\n")
        text_area.insert("end", "SAMPLE OUTPUT:\n")
        text_area.insert("end", output + "\n\n\n")

    text_area.config(state="disabled")

    tk.Button(
        frame,
        text="BACK TO MAIN MENU",
        font=("Arial", 10, "bold"),
        bg="#89b4fa",
        fg="#1e1e2e",
        command=main_menu
    ).pack(pady=10)


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
        "options": ["input()", "print()", "type()", "int()"],
        "answer": 1,
        "explanation": "The print() function displays text, numbers, and other information."
    },
    {
        "question": "Which symbol starts a single-line comment in Python?",
        "options": ["//", "#", "@", "&"],
        "answer": 1,
        "explanation": "The # symbol is used to start a single-line comment in Python."
    },
    {
        "question": "What is the data type of 25.5?",
        "options": ["int", "str", "float", "bool"],
        "answer": 2,
        "explanation": "A float is a number that can contain a decimal point."
    },
    {
        "question": "What is the result of 10 // 3?",
        "options": ["3.33", "1", "4", "3"],
        "answer": 3,
        "explanation": "The // operator performs floor division, so 10 // 3 equals 3."
    },
    {
        "question": "Which function accepts information from the user?",
        "options": ["print()", "input()", "type()", "str()"],
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
        "options": ["and", "print", "input", "range"],
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
        "options": ["if", "elif", "while", "print"],
        "answer": 2,
        "explanation": "A while loop continues running as long as its condition is True."
    },
    {
        "question": "What is the output of this code?\n\nfor number in range(1, 4):\n    print(number)",
        "options": ["1 2 3", "1 2 3 4", "0 1 2 3", "3 2 1"],
        "answer": 0,
        "explanation": "range(1, 4) generates 1, 2, and 3. The ending value 4 is not included."
    },
    {
        "question": "Which of the following is a valid variable name in Python?",
        "options": ["2name", "user_name", "user-name", "class"],
        "answer": 1,
        "explanation": "Variable names can contain letters, numbers, and underscores, but cannot start with a number or use reserved keywords."
    },
    {
        "question": "What data type is the value True?",
        "options": ["str", "int", "bool", "float"],
        "answer": 2,
        "explanation": "True and False are Boolean values. Their data type is bool."
    },
    {
        "question": "What is the result of 8 + 4 * 2?",
        "options": ["24", "16", "20", "12"],
        "answer": 1,
        "explanation": "Multiplication comes first: 4 * 2 = 8, then 8 + 8 = 16."
    },
    {
        "question": "Which statement assigns the value 10 to a variable named score?",
        "options": ["score == 10", "10 = score", "score = 10", "score : 10"],
        "answer": 2,
        "explanation": "The = operator assigns a value to a variable."
    }
]


quiz_answers = [None] * len(quiz_questions)
quiz_index = 0


def start_quiz():
    global quiz_answers, quiz_index

    quiz_answers = [None] * len(quiz_questions)
    quiz_index = 0

    show_quiz_question()


def show_quiz_question():
    clear_screen()

    question_data = quiz_questions[quiz_index]

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(fill="both", expand=True, padx=35, pady=20)

    tk.Label(
        frame,
        text="PYTHON KNOWLEDGE QUIZ",
        font=("Arial", 22, "bold"),
        fg="white",
        bg="#1e1e2e"
    ).pack(pady=(5, 8))

    tk.Label(
        frame,
        text=f"Question {quiz_index + 1} of {len(quiz_questions)}",
        font=("Arial", 11, "bold"),
        fg="#89b4fa",
        bg="#1e1e2e"
    ).pack(pady=5)

    progress = tk.Label(
        frame,
        text=f"Answered: {sum(answer is not None for answer in quiz_answers)} / {len(quiz_questions)}",
        font=("Arial", 10),
        fg="#bac2de",
        bg="#1e1e2e"
    )
    progress.pack(pady=(0, 15))

    tk.Label(
        frame,
        text=question_data["question"],
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#1e1e2e",
        justify="left",
        wraplength=850
    ).pack(anchor="w", pady=15)

    selected = tk.IntVar(
        value=-1 if quiz_answers[quiz_index] is None
        else quiz_answers[quiz_index]
    )

    option_frame = tk.Frame(frame, bg="#1e1e2e")
    option_frame.pack(fill="x", pady=10)

    for option_number, option_text in enumerate(question_data["options"]):
        tk.Radiobutton(
            option_frame,
            text=f"{chr(65 + option_number)}. {option_text}",
            variable=selected,
            value=option_number,
            font=("Arial", 12),
            fg="white",
            bg="#1e1e2e",
            activebackground="#1e1e2e",
            activeforeground="white",
            selectcolor="#313244",
            anchor="w",
            justify="left",
            wraplength=800
        ).pack(fill="x", anchor="w", pady=8)

    navigation = tk.Frame(frame, bg="#1e1e2e")
    navigation.pack(side="bottom", fill="x", pady=15)

    if quiz_index > 0:
        tk.Button(
            navigation,
            text="PREVIOUS",
            font=("Arial", 10, "bold"),
            bg="#45475a",
            fg="white",
            width=15,
            command=lambda: move_quiz(-1, selected)
        ).pack(side="left", padx=5)

    if quiz_index < len(quiz_questions) - 1:
        tk.Button(
            navigation,
            text="NEXT",
            font=("Arial", 10, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            width=15,
            command=lambda: move_quiz(1, selected)
        ).pack(side="right", padx=5)
    else:
        tk.Button(
            navigation,
            text="SUBMIT QUIZ",
            font=("Arial", 10, "bold"),
            bg="#a6e3a1",
            fg="#1e1e2e",
            width=18,
            command=lambda: finish_quiz(selected)
        ).pack(side="right", padx=5)

    tk.Button(
        frame,
        text="BACK TO MAIN MENU",
        font=("Arial", 9),
        bg="#1e1e2e",
        fg="#bac2de",
        bd=0,
        command=confirm_exit_quiz
    ).pack(side="bottom", pady=5)


def move_quiz(direction, selected):
    global quiz_index

    if selected.get() == -1:
        messagebox.showwarning(
            "No Answer",
            "Please select an answer before continuing."
        )
        return

    quiz_answers[quiz_index] = selected.get()
    quiz_index += direction

    show_quiz_question()


def finish_quiz(selected):
    if selected.get() == -1:
        messagebox.showwarning(
            "No Answer",
            "Please select an answer before submitting."
        )
        return

    quiz_answers[quiz_index] = selected.get()

    unanswered = [
        i + 1
        for i, answer in enumerate(quiz_answers)
        if answer is None
    ]

    if unanswered:
        messagebox.showwarning(
            "Incomplete Quiz",
            "Please answer all questions before submitting."
        )
        return

    show_quiz_result()


def confirm_exit_quiz():
    answer = messagebox.askyesno(
        "Exit Quiz",
        "Are you sure you want to leave the quiz? Your current answers will be lost."
    )

    if answer:
        main_menu()


def show_quiz_result():
    clear_screen()

    score = sum(
        1 for index, answer in enumerate(quiz_answers)
        if answer == quiz_questions[index]["answer"]
    )

    total = len(quiz_questions)
    percentage = (score / total) * 100

    frame = tk.Frame(root, bg="#1e1e2e")
    frame.pack(fill="both", expand=True, padx=25, pady=20)

    tk.Label(
        frame,
        text="QUIZ COMPLETED!",
        font=("Arial", 24, "bold"),
        fg="#a6e3a1",
        bg="#1e1e2e"
    ).pack(pady=15)

    tk.Label(
        frame,
        text=f"Your Score: {score} / {total}",
        font=("Arial", 22, "bold"),
        fg="white",
        bg="#1e1e2e"
    ).pack(pady=5)

    tk.Label(
        frame,
        text=f"Percentage: {percentage:.1f}%",
        font=("Arial", 15),
        fg="#89b4fa",
        bg="#1e1e2e"
    ).pack(pady=5)

    if percentage >= 90:
        remark = "Excellent! You have a strong understanding of Python."
    elif percentage >= 75:
        remark = "Good job! Keep reviewing the lessons."
    elif percentage >= 50:
        remark = "Nice try! Review the topics and practice more."
    else:
        remark = "Keep studying! You can improve with more practice."

    tk.Label(
        frame,
        text=remark,
        font=("Arial", 11),
        fg="#bac2de",
        bg="#1e1e2e",
        wraplength=850
    ).pack(pady=10)

    review_frame = tk.Frame(frame, bg="#1e1e2e")
    review_frame.pack(fill="both", expand=True, pady=10)

    review_scroll = tk.Scrollbar(review_frame)
    review_scroll.pack(side="right", fill="y")

    review_text = tk.Text(
        review_frame,
        font=("Arial", 10),
        wrap="word",
        yscrollcommand=review_scroll.set,
        padx=12,
        pady=10,
        bg="#11111b",
        fg="#cdd6f4"
    )
    review_text.pack(fill="both", expand=True)
    review_scroll.config(command=review_text.yview)

    for index, question_data in enumerate(quiz_questions):
        chosen = quiz_answers[index]
        correct = question_data["answer"]

        status = "CORRECT" if chosen == correct else "INCORRECT"

        review_text.insert(
            "end",
            f"Question {index + 1}: {status}\n"
        )
        review_text.insert(
            "end",
            question_data["question"] + "\n"
        )
        review_text.insert(
            "end",
            f"Your answer: {question_data['options'][chosen]}\n"
        )
        review_text.insert(
            "end",
            f"Correct answer: {question_data['options'][correct]}\n"
        )
        review_text.insert(
            "end",
            f"Explanation: {question_data['explanation']}\n\n"
        )

    review_text.config(state="disabled")

    buttons = tk.Frame(frame, bg="#1e1e2e")
    buttons.pack(pady=10)

    tk.Button(
        buttons,
        text="RETAKE QUIZ",
        font=("Arial", 10, "bold"),
        bg="#89b4fa",
        fg="#1e1e2e",
        width=16,
        command=start_quiz
    ).pack(side="left", padx=8)

    tk.Button(
        buttons,
        text="BACK TO MAIN MENU",
        font=("Arial", 10, "bold"),
        bg="#45475a",
        fg="white",
        width=20,
        command=main_menu
    ).pack(side="left", padx=8)


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
