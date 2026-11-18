"""
PYTHON QUEST - Learn. Practice. Master.
Console-based Python lessons and quiz reviewer.

Run with: python python_quest.py
Account data and latest quiz results are saved in python_quest_data.json
in the same folder as this program.
"""

import json
import os
import hashlib
import getpass
import sys
import textwrap

APP_TITLE = "PYTHON QUEST"
TAGLINE = "Learn. Practice. Master."
DATA_FILE = "python_quest_data.json"

topics = {'Introduction to Programming': ('CHAPTER 1: INTRODUCTION TO PROGRAMMING', 'Programming is the process of giving instructions to a computer. A program is a set of instructions that performs a specific task.\n\nAn algorithm is a step-by-step procedure for solving a problem. Python is a programming language used to create different types of programs.', 'print("Hello, Python!")\nprint("Welcome to programming.")', 'Hello, Python!\nWelcome to programming.'), 'Python Basic Syntax': ('CHAPTER 2: PYTHON BASIC SYNTAX', 'Syntax refers to the rules of writing Python code. Python uses indentation to organize statements. Python is also case-sensitive.', 'if 5 > 2:\n    print("Five is greater than two")', 'Five is greater than two'), 'Printing Output': ('PRINTING OUTPUT', 'The print() function displays text, numbers, and other information on the screen.', 'print("Hello, world!")\nprint("Age:", 17)\nprint(10 + 5)', 'Hello, world!\nAge: 17\n15'), 'Python Comments': ('PYTHON COMMENTS', 'Comments are notes written inside the code. Python ignores comments when executing a program. A single-line comment starts with #.', '# This is a comment\nname = "Alex"\n\nprint(name)', 'Alex'), 'Variables, Constants, and Data Types': ('VARIABLES, CONSTANTS, AND DATA TYPES', 'A variable stores a value. A constant is a value that should not change. In Python, uppercase names are commonly used for constants.', 'name = "Alex"\nage = 17\n\nPI = 3.14159\n\nprint(name)\nprint(age)\nprint(PI)', 'Alex\n17\n3.14159'), 'Basic Data Types in Python': ('BASIC DATA TYPES IN PYTHON', 'Python has different data types:\n\nint - whole numbers\nfloat - decimal numbers\nstr - text\nbool - True or False', 'number = 10\nprice = 25.50\nmessage = "Hello"\nis_ready = True\n\nprint(type(number))\nprint(type(price))\nprint(type(message))\nprint(type(is_ready))', "<class 'int'>\n<class 'float'>\n<class 'str'>\n<class 'bool'>"), 'Arithmetic Operators and Expressions': ('CHAPTER 3: ARITHMETIC OPERATORS AND EXPRESSIONS', 'Arithmetic operators perform mathematical operations.\n\n+ Addition\n- Subtraction\n* Multiplication\n/ Division\n// Floor Division\n% Modulus (remainder)\n** Exponentiation', 'a = 10\nb = 3\n\nprint(a + b)\nprint(a - b)\nprint(a * b)\nprint(a / b)\nprint(a // b)\nprint(a % b)\nprint(a ** b)', '13\n7\n30\n3.3333333333333335\n3\n1\n1000'), 'Basic Input and Output': ('CHAPTER 4: BASIC INPUT AND OUTPUT', 'The input() function accepts information from the user. The print() function displays information.\n\nThe input() function returns a string. Use int() or float() to convert input into a number.', 'name = input("Enter your name: ")\nage = int(input("Enter your age: "))\n\nprint("Hello,", name)\nprint("Next year:", age + 1)', 'Enter your name: Alex\nEnter your age: 17\nHello, Alex\nNext year: 18'), 'Conditional Statements': ('MIDTERM: CONDITIONAL STATEMENTS', 'Conditional statements allow a program to make decisions.\n\nif - checks a condition\nelif - checks another condition\nelse - runs when the conditions are False', 'score = int(input("Enter your score: "))\n\nif score >= 90:\n    print("Excellent")\n\nelif score >= 75:\n    print("Passed")\n\nelse:\n    print("Needs improvement")', 'Enter your score: 85\nPassed'), 'Logical Operators': ('MIDTERM: LOGICAL OPERATORS', 'Logical operators combine conditions.\n\nand - both conditions must be True\nor - at least one condition must be True\nnot - reverses the Boolean value', 'age = 17\nhas_id = True\n\nprint(age >= 18 and has_id)\nprint(age >= 18 or has_id)\nprint(not has_id)', 'False\nTrue\nFalse'), 'Iteration and Loops': ('FINALS: INTRODUCTION TO ITERATION AND LOOPS', 'A loop repeats a block of code.\n\nfor loop - repeats through a sequence or range\nwhile loop - repeats while a condition is True\n\nLoops help reduce repeated code.', 'for number in range(1, 4):\n    print(number)\n\ncount = 1\n\nwhile count <= 3:\n    print("Count:", count)\n    count += 1', '1\n2\n3\nCount: 1\nCount: 2\nCount: 3')}
quiz_questions = [
    {
        'question': 'What is an algorithm?',
        'options': ['A type of computer hardware', 'A step-by-step procedure for solving a problem', 'A Python error message', 'A program that only prints text'],
        'answer': 1,
        'explanation': 'An algorithm is a step-by-step procedure for solving a problem. A program is one way of carrying out an algorithm.',
    },
    {
        'question': 'What will this code display?\n\nprint("Age:", 17)',
        'options': ['Age:17', 'Age: 17', '"Age:", 17', 'Age 17'],
        'answer': 1,
        'explanation': 'print() separates multiple values with a space by default, and the quotation marks are not shown. The output is: Age: 17',
    },
    {
        'question': 'What does Python do with comments when a program runs?',
        'options': ['Executes them as code', 'Displays them on the screen', 'Ignores them', 'Converts them to variables'],
        'answer': 2,
        'explanation': 'Comments are notes for people reading the code. Python ignores them when executing a program.',
    },
    {
        'question': 'Which name follows the common Python convention for a constant?',
        'options': ['max_speed', 'maxSpeed', 'MAX_SPEED', 'Max-Speed'],
        'answer': 2,
        'explanation': 'By convention, constants are written in uppercase letters, with underscores separating words. Python does not enforce this; it is a naming habit.',
    },
    {
        'question': 'What data type does the input() function always return?',
        'options': ['int', 'float', 'bool', 'str'],
        'answer': 3,
        'explanation': 'input() always returns a string. Use int() or float() to convert the value into a number.',
    },
    {
        'question': 'What is the result of 17 % 5?',
        'options': ['3', '2', '3.4', '12'],
        'answer': 1,
        'explanation': 'The % operator returns the remainder. 17 divided by 5 is 3 with a remainder of 2.',
    },
    {
        'question': 'What is the result of 2 ** 4?',
        'options': ['8', '6', '16', '24'],
        'answer': 2,
        'explanation': 'The ** operator is exponentiation. 2 ** 4 means 2 x 2 x 2 x 2, which equals 16.',
    },
    {
        'question': 'Which keyword checks another condition when the first if condition is False?',
        'options': ['elif', 'else', 'while', 'for'],
        'answer': 0,
        'explanation': 'elif (short for "else if") checks a new condition only when the previous conditions were False. else has no condition at all.',
    },
    {
        'question': 'What is the output of this code?\n\nage = 17\nhas_id = True\nprint(age >= 18 or has_id)',
        'options': ['False', '17', 'Error', 'True'],
        'answer': 3,
        'explanation': 'age >= 18 is False, but has_id is True. The or operator only needs one True condition, so the result is True.',
    },
    {
        'question': 'How does Python organize blocks of statements, such as the code inside an if statement?',
        'options': ['Curly braces { }', 'Indentation', 'Semicolons ;', 'Parentheses ( )'],
        'answer': 1,
        'explanation': 'Python uses indentation (spaces at the start of a line) to show which statements belong together.',
    },
    {
        'question': 'What is the data type of "Hello"?',
        'options': ['str', 'int', 'float', 'bool'],
        'answer': 0,
        'explanation': 'Text enclosed in quotation marks is a string, whose data type is str.',
    },
    {
        'question': 'What is the output of this code?\n\nfor i in range(3):\n    print(i)',
        'options': ['1 2 3', '0 1 2', '0 1 2 3', '1 2'],
        'answer': 1,
        'explanation': 'range(3) starts at 0 by default and stops before 3, so it produces 0, 1, and 2.',
    },
    {
        'question': 'Python is case-sensitive. What does this mean for the variables score and Score?',
        'options': ['They are the same variable', 'They are two different variables', 'Python shows an error', 'Score replaces score'],
        'answer': 1,
        'explanation': 'Because Python is case-sensitive, uppercase and lowercase letters are different. score and Score are separate variables.',
    },
    {
        'question': 'Which code correctly converts the text "21" into a whole number?',
        'options': ['str("21")', 'float("21")', 'print("21")', 'int("21")'],
        'answer': 3,
        'explanation': 'int() converts a value into a whole number. float() would produce 21.0, and str() keeps it as text.',
    },
    {
        'question': 'What is the output of this code?\n\nprint(not (5 > 2))',
        'options': ['True', 'False', '5', 'Error'],
        'answer': 1,
        'explanation': '5 > 2 is True, and the not operator reverses it, so the result is False.',
    },
]


def pause():
    input("\nPress ENTER to continue...")


def line(char="=", width=72):
    print(char * width)


def header(title, subtitle=None):
    print("\n")
    line()
    print(title.center(72))
    if subtitle:
        print(subtitle.center(72))
    line()


def read_choice(prompt, valid_choices):
    """Read a menu choice (not case-sensitive) until it is valid."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please enter one of:", ", ".join(sorted(valid_choices)))


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "quiz_results": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        data.setdefault("users", {})
        data.setdefault("quiz_results", {})
        return data
    except (json.JSONDecodeError, OSError):
        print("Warning: The saved account file could not be read.")
        print("A new data file will be created when you register.")
        return {"users": {}, "quiz_results": {}}


def save_data():
    temporary_file = DATA_FILE + ".tmp"
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(temporary_file, DATA_FILE)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ask_password(prompt):
    """Read a password and show * for each character typed.
    Falls back to normal typing where a console cannot mask input
    (Android apps, IDLE, or when input is piped)."""
    on_android = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
    if on_android or not sys.stdin.isatty():
        return input(prompt)

    chars = []
    try:
        if os.name == "nt":
            import msvcrt
            sys.stdout.write(prompt)
            sys.stdout.flush()
            while True:
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    sys.stdout.write("\n")
                    return "".join(chars)
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch in ("\x00", "\xe0"):      # arrow / function keys
                    msvcrt.getwch()
                    continue
                if ch in ("\b", "\x7f"):
                    if chars:
                        chars.pop()
                        sys.stdout.write("\b \b")
                else:
                    chars.append(ch)
                    sys.stdout.write("*")
                sys.stdout.flush()
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            sys.stdout.write(prompt)
            sys.stdout.flush()
            try:
                tty.setcbreak(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n"):
                        sys.stdout.write("\n")
                        return "".join(chars)
                    if ch == "\x03":
                        raise KeyboardInterrupt
                    if ch == "\x04":
                        raise EOFError
                    if ch in ("\b", "\x7f"):
                        if chars:
                            chars.pop()
                            sys.stdout.write("\b \b")
                    else:
                        chars.append(ch)
                        sys.stdout.write("*")
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        return input(prompt)


def is_command(text, command):
    return text.strip().lower() == command


# ---------------------------------------------------------------------------
# REGISTRATION
# ---------------------------------------------------------------------------

def ask_field(step, values):
    """Ask one registration question.
    Returns (status, value): status is 'ok', 'error', 'back' or 'cancel'."""
    if step == 0:
        raw = input("Full name: ")
    elif step == 1:
        raw = input("Create username: ")
    elif step == 2:
        raw = ask_password("Create password: ")
    else:
        raw = input("Gmail (optional, press ENTER to skip): ")

    if is_command(raw, "/cancel"):
        return "cancel", None
    if is_command(raw, "/back"):
        return "back", None

    if step == 0:
        raw = raw.strip()
        if not raw:
            print("Full name is required.")
            return "error", None
        return "ok", raw

    if step == 1:
        username = raw.strip().lower()
        if not username:
            print("Username is required.")
            return "error", None
        if " " in username:
            print("Username cannot contain spaces.")
            return "error", None
        if username in data["users"]:
            print("That username already exists. Please choose another.")
            return "error", None
        return "ok", username

    if step == 2:
        if not raw:
            print("Password is required.")
            return "error", None
        confirm = ask_password("Confirm password: ")
        if is_command(confirm, "/cancel"):
            return "cancel", None
        if raw != confirm:
            print("Passwords do not match. Please enter the password again.")
            return "error", None
        return "ok", raw

    raw = raw.strip()
    if raw and ("@" not in raw or "." not in raw.split("@")[-1]):
        print("Please enter a valid email address, or press ENTER to skip.")
        return "error", None
    return "ok", raw


def register():
    header("CREATE AN ACCOUNT", "Register to begin your Python learning journey")
    print("Tips: type /back to return to the previous question.")
    print("      type /cancel to stop and return to the main menu.")
    print("      You can also fix any detail on the review screen.\n")

    keys = ["full_name", "username", "password", "gmail"]
    labels = ["Full name", "Username", "Password", "Gmail"]
    values = {key: "" for key in keys}

    # First pass: ask every question in order.
    step = 0
    while step < 4:
        status, value = ask_field(step, values)
        if status == "cancel":
            print("\nRegistration cancelled.")
            return
        if status == "back":
            if step == 0:
                print("You are already at the first question.")
            else:
                step -= 1
        elif status == "ok":
            values[keys[step]] = value
            step += 1

    # Review screen: fix any detail without starting over.
    while True:
        print()
        line("-")
        print("PLEASE REVIEW YOUR DETAILS")
        line("-")
        print("[1] Full name : {}".format(values["full_name"]))
        print("[2] Username  : {}".format(values["username"]))
        print("[3] Password  : {}".format("*" * len(values["password"])))
        print("[4] Gmail     : {}".format(values["gmail"] or "(none)"))
        line("-")
        print("Type 1-4 to change that detail")
        print("[S] Save account    [C] Cancel")
        choice = read_choice("\nChoose an option: ", {"1", "2", "3", "4", "s", "c"})

        if choice == "s":
            data["users"][values["username"]] = {
                "full_name": values["full_name"],
                "password_hash": hash_password(values["password"]),
                "gmail": values["gmail"],
            }
            save_data()
            print("\nAccount created successfully! You can now log in.")
            return
        if choice == "c":
            print("\nRegistration cancelled.")
            return

        step = int(choice) - 1
        print("\nChange {} (type /cancel to keep the old value):".format(labels[step].lower()))
        while True:
            status, value = ask_field(step, values)
            if status == "ok":
                values[keys[step]] = value
                break
            if status in ("cancel", "back"):
                print("Kept the old value.")
                break


def login():
    header("LOGIN", "Enter your account details")
    print("Tip: type /cancel to return to the main menu.\n")
    username = input("Username: ").strip().lower()
    if is_command(username, "/cancel"):
        return None
    password = ask_password("Password: ")
    if is_command(password, "/cancel"):
        return None

    user = data["users"].get(username)
    if user and user["password_hash"] == hash_password(password):
        print("\nLogin successful. Welcome, {}!".format(user["full_name"]))
        return username

    print("\nLogin failed: Incorrect username or password.")
    return None


# ---------------------------------------------------------------------------
# LESSONS
# ---------------------------------------------------------------------------

def show_lesson(topic_name, position=None, total=None):
    """Show one lesson. Returns 'prev', 'next', 'list' or 'menu'."""
    title, discussion, code, output = topics[topic_name]
    subtitle = topic_name
    if position is not None:
        subtitle = "Lesson {} of {}  -  {}".format(position, total, topic_name)
    header(title, subtitle)
    print("\nLESSON DISCUSSION\n")
    print(textwrap.fill(discussion, width=72, replace_whitespace=False))
    print("\nPYTHON CODE EXAMPLE\n")
    print(code)
    print("\nSAMPLE OUTPUT\n")
    print(output)
    line("-")
    print("[ENTER] or [N] Next lesson     [P] Previous lesson")
    print("[L] Lesson list                [M] Main menu")

    mapping = {"": "next", "n": "next", "2": "next",
               "p": "prev", "1": "prev",
               "l": "list", "3": "list",
               "m": "menu", "4": "menu"}
    while True:
        choice = input("\nChoose an option: ").strip().lower()
        if choice in mapping:
            return mapping[choice]
        print("Invalid choice. Press ENTER for next, or type P, L, or M.")


def lesson_viewer():
    topic_names = list(topics.keys())
    while True:
        header("PYTHON LESSONS", "Choose a topic to study")
        for index, name in enumerate(topic_names, start=1):
            print("[{}] {}".format(index, name))
        print("[0] Back to main menu")

        choice = input("\nEnter topic number: ").strip()
        if choice == "0" or choice.lower() in {"m", "b"}:
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(topic_names):
            print("Invalid topic number.")
            continue

        index = int(choice) - 1
        while True:
            action = show_lesson(topic_names[index], index + 1, len(topic_names))
            if action == "prev":
                index = (index - 1) % len(topic_names)
            elif action == "next":
                index = (index + 1) % len(topic_names)
            elif action == "list":
                break
            else:
                return


def discuss_all_topics():
    """Go through every lesson in order, with next / previous navigation."""
    topic_names = list(topics.keys())
    index = 0
    while True:
        action = show_lesson(topic_names[index], index + 1, len(topic_names))
        if action == "prev":
            if index > 0:
                index -= 1
            else:
                print("You are already at the first lesson.")
        elif action == "next":
            if index < len(topic_names) - 1:
                index += 1
            else:
                print("\nYou have reached the end of all {} lessons.".format(len(topic_names)))
                return
        else:
            return


# ---------------------------------------------------------------------------
# QUIZ
# ---------------------------------------------------------------------------

def calculate_score(answers):
    return sum(
        1 for index, answer in enumerate(answers)
        if answer == quiz_questions[index]["answer"]
    )


def ask_question_number(prompt):
    """Return a zero-based question index, or None if the input is invalid."""
    value = input(prompt).strip()
    if value.isdigit() and 1 <= int(value) <= len(quiz_questions):
        return int(value) - 1
    print("Please enter a number from 1 to {}.".format(len(quiz_questions)))
    return None


def run_quiz():
    """Let the person answer the quiz. Returns the answers, or None if they leave."""
    total = len(quiz_questions)
    answers = [None] * total
    index = 0

    while True:
        question_data = quiz_questions[index]
        header("PYTHON QUEST QUIZ", "Question {} of {}".format(index + 1, total))
        print(textwrap.fill(question_data["question"], width=72, replace_whitespace=False))
        print()
        for option_index, option in enumerate(question_data["options"], start=1):
            print("{}. {}".format(option_index, option))

        if answers[index] is not None:
            print("\nYour answer: {}  (type 1-4 to change it)".format(answers[index] + 1))

        print("\n[1-4] Answer   [N] Next   [P] Previous   [J] Jump to question")
        print("[S] Submit     [M] Main menu")
        choice = input("Your choice: ").strip().lower()

        if choice in {"1", "2", "3", "4"}:
            answers[index] = int(choice) - 1
            if index < total - 1:
                index += 1
            else:
                print("Answer saved. This is the last question - type S to submit.")

        elif choice == "n":
            if index < total - 1:
                index += 1
            else:
                print("You are already at the last question. Type S to submit.")

        elif choice == "p":
            if index > 0:
                index -= 1
            else:
                print("You are already at the first question.")

        elif choice == "j":
            target = ask_question_number("Go to question number (1-{}): ".format(total))
            if target is not None:
                index = target

        elif choice == "s":
            unanswered = [i + 1 for i, answer in enumerate(answers) if answer is None]
            if unanswered:
                print("\nUnanswered question(s): {}".format(", ".join(map(str, unanswered))))
                go = input("Go to question {} now? (y/n): ".format(unanswered[0])).strip().lower()
                if go == "y":
                    index = unanswered[0] - 1
                continue

            print("\nYOUR ANSWERS")
            line("-")
            for number, answer in enumerate(answers, start=1):
                print("Q{:<2} -> {}".format(number, answer + 1))
            line("-")
            reply = input("Submit now? Type Y to submit, or a question number to change it: ").strip().lower()
            if reply == "y":
                return answers
            if reply.isdigit() and 1 <= int(reply) <= total:
                index = int(reply) - 1
            elif reply:
                print("Not submitted. Returning to the quiz.")

        elif choice == "m":
            if any(answer is not None for answer in answers):
                confirm = input("Leave the quiz? Your answers will be lost (y/n): ").strip().lower()
                if confirm != "y":
                    continue
            return None

        else:
            print("Invalid input. Enter 1-4, N, P, J, S, or M.")


def show_quiz_result(username, answers):
    """Show the result. Returns True if the person wants to retake the quiz."""
    score = calculate_score(answers)
    total = len(quiz_questions)
    percentage = (score / total) * 100

    if percentage >= 90:
        remark = "Excellent! You have a strong understanding of Python."
    elif percentage >= 75:
        remark = "Good job! Keep reviewing the lessons."
    elif percentage >= 50:
        remark = "Nice try! Review the topics and practice more."
    else:
        remark = "Keep studying! You can improve with more practice."

    data["quiz_results"][username] = {
        "score": score,
        "total": total,
        "percentage": round(percentage, 1),
        "remark": remark,
    }
    save_data()

    header("QUIZ COMPLETED!")
    print("Your Score : {} / {}".format(score, total))
    print("Percentage : {:.1f}%".format(percentage))
    print("Remark     : {}".format(remark))
    print("\nANSWER REVIEW")
    line("-")

    for index, question in enumerate(quiz_questions):
        correct = question["answer"]
        selected = answers[index]
        status = "CORRECT" if selected == correct else "INCORRECT"
        print("\nQuestion {}: {}".format(index + 1, question["question"]))
        print("Your answer   : {}".format(question["options"][selected]))
        print("Correct answer: {}".format(question["options"][correct]))
        print("Result        : {}".format(status))
        print("Explanation   : {}".format(question["explanation"]))
        line("-")

    print("\n[R] Retake quiz")
    print("[M] Return to main menu")
    return read_choice("Choose an option: ", {"r", "m"}) == "r"


def take_quiz(username):
    while True:
        answers = run_quiz()
        if answers is None:
            return
        if not show_quiz_result(username, answers):
            return


def view_quiz_result(username):
    header("LATEST QUIZ RESULT")
    result = data["quiz_results"].get(username)
    if not result:
        print("You have not completed a quiz yet.")
    else:
        print("Your Score : {} / {}".format(result["score"], result["total"]))
        print("Percentage : {:.1f}%".format(result["percentage"]))
        print("Remark     : {}".format(result["remark"]))
    pause()


# ---------------------------------------------------------------------------
# MENUS
# ---------------------------------------------------------------------------

def main_menu(username):
    full_name = data["users"][username]["full_name"]
    while True:
        header(APP_TITLE, "Welcome, {}".format(full_name))
        print("[1] View a Lesson")
        print("[2] Discuss All Topics")
        print("[3] Take a Quiz")
        print("[4] View Latest Quiz Result")
        print("[5] Logout")
        choice = read_choice("\nEnter your choice: ", {"1", "2", "3", "4", "5"})

        if choice == "1":
            lesson_viewer()
        elif choice == "2":
            discuss_all_topics()
        elif choice == "3":
            take_quiz(username)
        elif choice == "4":
            view_quiz_result(username)
        else:
            print("You have been logged out.")
            return


def main():
    while True:
        header(APP_TITLE, TAGLINE)
        print("Welcome to your Python learning journey!")
        print("Learn the concepts. Practice the examples. Test your knowledge.")
        print("\n[1] Register")
        print("[2] Login")
        print("[3] Exit")
        choice = read_choice("\nEnter your choice: ", {"1", "2", "3"})

        if choice == "1":
            register()
        elif choice == "2":
            username = login()
            if username:
                main_menu(username)
        else:
            print("\nThank you for using PYTHON QUEST!")
            print("Learn. Practice. Master.")
            break


if __name__ == "__main__":
    data = load_data()
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed. Thank you for using PYTHON QUEST!")
