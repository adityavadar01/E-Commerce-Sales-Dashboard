import tkinter as tk
from tkinter import messagebox

from database import connect_database
from dashboard import open_dashboard

from theme import (
    apply_theme,
    BG_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    SECONDARY_TEXT,
    TITLE_FONT,
    SUBTITLE_FONT,
    NORMAL_FONT,
    BUTTON_FONT
)


def login():

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "" or password == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password."
        )

        return

    try:

        db = connect_database()
        cursor = db.cursor()

        query = """
        SELECT *
        FROM users
        WHERE username = %s
        AND password = %s
        """

        cursor.execute(
            query,
            (
                username,
                password
            )
        )

        result = cursor.fetchone()

        cursor.close()
        db.close()

        if result:

            messagebox.showinfo(
                "Login Successful",
                "Welcome to Ganesh Nashta Center!"
            )

            root.destroy()

            open_dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


def show_password():

    if password_entry.cget("show") == "*":

        password_entry.config(
            show=""
        )

        show_password_button.config(
            text="Hide"
        )

    else:

        password_entry.config(
            show="*"
        )

        show_password_button.config(
            text="Show"
        )


# =================================================
# MAIN WINDOW
# =================================================

root = tk.Tk()

apply_theme()

root.title(
    "Ganesh Nashta Center - Login"
)

root.geometry(
    "500x600"
)

root.configure(
    bg=BG_COLOR
)

root.resizable(
    False,
    False
)


# =================================================
# TOP AREA
# =================================================

top_frame = tk.Frame(
    root,
    bg=PRIMARY_COLOR,
    height=150
)

top_frame.pack(
    fill="x"
)

top_frame.pack_propagate(
    False
)


title = tk.Label(
    top_frame,
    text="GANESH NASHTA CENTER",
    font=TITLE_FONT,
    bg=PRIMARY_COLOR,
    fg="white"
)

title.pack(
    pady=(35, 5)
)


subtitle = tk.Label(
    top_frame,
    text="Sales & Business Intelligence",
    font=SUBTITLE_FONT,
    bg=PRIMARY_COLOR,
    fg="#DCEAF7"
)

subtitle.pack()


# =================================================
# LOGIN CARD
# =================================================

login_card = tk.Frame(
    root,
    bg=CARD_COLOR,
    width=390,
    height=350,
    highlightbackground="#D9DEE5",
    highlightthickness=1
)

login_card.pack(
    pady=35
)

login_card.pack_propagate(
    False
)


login_title = tk.Label(
    login_card,
    text="Administrator Login",
    font=(
        "Segoe UI",
        18,
        "bold"
    ),
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

login_title.pack(
    pady=(25, 20)
)


# =================================================
# USERNAME
# =================================================

username_label = tk.Label(
    login_card,
    text="Username",
    font=BUTTON_FONT,
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

username_label.pack(
    anchor="w",
    padx=45
)


username_entry = tk.Entry(
    login_card,
    width=32,
    font=NORMAL_FONT,
    relief="solid",
    bd=1
)

username_entry.pack(
    pady=(6, 15),
    ipady=7
)


# =================================================
# PASSWORD
# =================================================

password_label = tk.Label(
    login_card,
    text="Password",
    font=BUTTON_FONT,
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

password_label.pack(
    anchor="w",
    padx=45
)


password_frame = tk.Frame(
    login_card,
    bg=CARD_COLOR
)

password_frame.pack(
    pady=(6, 20)
)


password_entry = tk.Entry(
    password_frame,
    width=25,
    font=NORMAL_FONT,
    show="*",
    relief="solid",
    bd=1
)

password_entry.pack(
    side="left",
    ipady=7
)


show_password_button = tk.Button(
    password_frame,
    text="Show",
    font=(
        "Segoe UI",
        8,
        "bold"
    ),
    bg="#E8EDF2",
    fg=TEXT_COLOR,
    relief="flat",
    bd=0,
    cursor="hand2",
    command=show_password
)

show_password_button.pack(
    side="left",
    padx=5,
    ipady=5
)


# =================================================
# LOGIN BUTTON
# =================================================

login_button = tk.Button(
    login_card,
    text="LOGIN",
    width=24,
    height=2,
    font=BUTTON_FONT,
    bg=PRIMARY_COLOR,
    fg="white",
    activebackground=SECONDARY_COLOR,
    activeforeground="white",
    relief="flat",
    bd=0,
    cursor="hand2",
    command=login
)

login_button.pack(
    pady=5
)


# =================================================
# FOOTER
# =================================================

footer = tk.Label(
    root,
    text="Business Intelligence & Sales Management System",
    font=(
        "Segoe UI",
        9
    ),
    bg=BG_COLOR,
    fg=SECONDARY_TEXT
)

footer.pack(
    pady=5
)


username_entry.focus()

root.bind(
    "<Return>",
    lambda event: login()
)

root.mainloop()