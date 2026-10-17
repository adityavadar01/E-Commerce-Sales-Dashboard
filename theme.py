import tkinter as tk
from tkinter import ttk


# =================================================
# APPLICATION COLORS
# =================================================

BG_COLOR = "#F4F6F8"
CARD_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1F4E78"
SECONDARY_COLOR = "#2E75B6"
ACCENT_COLOR = "#70AD47"

TEXT_COLOR = "#1F2937"
SECONDARY_TEXT = "#5B6573"

SUCCESS_COLOR = "#2E7D32"
WARNING_COLOR = "#F57C00"
DANGER_COLOR = "#C62828"

BORDER_COLOR = "#D9DEE5"


# =================================================
# FONTS
# =================================================

TITLE_FONT = (
    "Segoe UI",
    26,
    "bold"
)

SUBTITLE_FONT = (
    "Segoe UI",
    14
)

HEADING_FONT = (
    "Segoe UI",
    16,
    "bold"
)

NORMAL_FONT = (
    "Segoe UI",
    10
)

BUTTON_FONT = (
    "Segoe UI",
    10,
    "bold"
)

KPI_TITLE_FONT = (
    "Segoe UI",
    10,
    "bold"
)

KPI_VALUE_FONT = (
    "Segoe UI",
    18,
    "bold"
)


# =================================================
# APPLY GLOBAL TKINTER THEME
# =================================================

def apply_theme():

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except:
        pass

    # -------------------------------------------------
    # Treeview
    # -------------------------------------------------

    style.configure(
        "Treeview",
        background=CARD_COLOR,
        foreground=TEXT_COLOR,
        rowheight=32,
        fieldbackground=CARD_COLOR,
        font=NORMAL_FONT,
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=PRIMARY_COLOR,
        foreground="white",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        padding=8
    )

    style.map(
        "Treeview",
        background=[
            ("selected", SECONDARY_COLOR)
        ],
        foreground=[
            ("selected", "white")
        ]
    )

    # -------------------------------------------------
    # Combobox
    # -------------------------------------------------

    style.configure(
        "TCombobox",
        font=NORMAL_FONT,
        padding=6
    )

    # -------------------------------------------------
    # Entry
    # -------------------------------------------------

    style.configure(
        "TEntry",
        font=NORMAL_FONT,
        padding=7
    )


# =================================================
# COMMON BUTTON
# =================================================

def create_button(
    parent,
    text,
    command,
    width=18,
    bg=PRIMARY_COLOR
):

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        height=2,
        font=BUTTON_FONT,
        bg=bg,
        fg="white",
        activebackground=SECONDARY_COLOR,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2"
    )

    return button


# =================================================
# KPI CARD
# =================================================

def create_kpi_card(
    parent,
    title,
    value,
    width=190,
    height=95
):

    card = tk.Frame(
        parent,
        width=width,
        height=height,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    card.pack_propagate(False)

    title_label = tk.Label(
        card,
        text=title,
        font=KPI_TITLE_FONT,
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT
    )

    title_label.pack(
        pady=(12, 3)
    )

    value_label = tk.Label(
        card,
        text=value,
        font=KPI_VALUE_FONT,
        bg=CARD_COLOR,
        fg=PRIMARY_COLOR
    )

    value_label.pack()

    return card, value_label