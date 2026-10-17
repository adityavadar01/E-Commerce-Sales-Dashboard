import tkinter as tk
from tkinter import ttk, messagebox

from database import connect_database

from theme import (
    apply_theme,
    BG_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    TEXT_COLOR,
    SECONDARY_TEXT,
    SUCCESS_COLOR,
    WARNING_COLOR,
    DANGER_COLOR,
    BORDER_COLOR,
    TITLE_FONT,
    SUBTITLE_FONT,
    HEADING_FONT,
    NORMAL_FONT,
    create_button
)


# ============================================================
# LOAD MENU ITEMS
# ============================================================

def load_items():
    """Load all menu items from database."""

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT item_id,
                   item_name,
                   category,
                   price,
                   cost_price,
                   available_quantity
            FROM menu_items
            ORDER BY item_id
        """)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )
        return []


# ============================================================
# LOAD ITEM NAMES FOR DROPDOWN
# ============================================================

def load_item_names():
    """Load existing item names into Item Name dropdown."""

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT item_name
            FROM menu_items
            ORDER BY item_name
        """)

        names = [
            row[0]
            for row in cursor.fetchall()
        ]

        cursor.close()
        connection.close()

        return names

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )
        return []


def refresh_item_dropdown():
    """Refresh Item Name dropdown."""

    names = load_item_names()

    item_name_combo["values"] = names


# ============================================================
# LOAD TABLE
# ============================================================

def load_menu_table():
    """Load menu items into Treeview."""

    for item in table.get_children():
        table.delete(item)

    rows = load_items()

    for row in rows:

        table.insert(
            "",
            "end",
            values=(
                row[0],
                row[1],
                row[2],
                f"{float(row[3]):.2f}",
                f"{float(row[4]):.2f}",
                row[5]
            )
        )

    count_label.config(
        text=f"Total Menu Items: {len(rows)}"
    )

    refresh_item_dropdown()


# ============================================================
# AUTO-FILL EXISTING ITEM
# ============================================================

def fill_existing_item(event=None):
    """Auto-fill details when existing item is selected."""

    selected_name = item_name_var.get().strip()

    if not selected_name:
        return

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT item_id,
                   category,
                   price,
                   cost_price,
                   available_quantity
            FROM menu_items
            WHERE item_name = %s
        """, (selected_name,))

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row:

            selected_id_var.set(row[0])

            category_var.set(
                row[1] if row[1] else ""
            )

            price_var.set(row[2])

            cost_price_var.set(row[3])

            quantity_var.set(row[4])

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# CLEAR FORM
# ============================================================

def clear_fields():

    selected_id_var.set("")

    item_name_var.set("")

    category_var.set("")

    price_var.set("")

    cost_price_var.set("")

    quantity_var.set("")


# ============================================================
# ADD ITEM
# ============================================================

def add_item():

    item_name = item_name_var.get().strip()

    category = category_var.get().strip()

    price = price_var.get().strip()

    cost_price = cost_price_var.get().strip()

    quantity = quantity_var.get().strip()

    if (
        not item_name
        or not category
        or not price
        or not cost_price
        or not quantity
    ):

        messagebox.showwarning(
            "Missing Information",
            "Please fill all fields."
        )

        return

    try:

        price_value = float(price)

        cost_value = float(cost_price)

        quantity_value = int(quantity)

        if (
            price_value < 0
            or cost_value < 0
            or quantity_value < 0
        ):

            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Invalid Input",
            "Price and cost must be valid numbers and quantity must be a valid integer."
        )

        return

    try:

        connection = connect_database()
        cursor = connection.cursor()

        # Check duplicate item name

        cursor.execute("""
            SELECT item_id
            FROM menu_items
            WHERE item_name = %s
        """, (item_name,))

        existing = cursor.fetchone()

        if existing:

            cursor.close()
            connection.close()

            messagebox.showwarning(
                "Duplicate Item",
                "This menu item already exists.\n"
                "Select it from the dropdown and use Update."
            )

            return

        cursor.execute("""
            INSERT INTO menu_items
            (
                item_name,
                category,
                price,
                cost_price,
                available_quantity
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            item_name,
            category,
            price_value,
            cost_value,
            quantity_value
        ))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Menu item added successfully."
        )

        clear_fields()

        load_menu_table()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# UPDATE ITEM
# ============================================================

def update_item():

    item_id = selected_id_var.get().strip()

    if not item_id:

        messagebox.showwarning(
            "Select Item",
            "Please select an existing item from the dropdown or table."
        )

        return

    item_name = item_name_var.get().strip()

    category = category_var.get().strip()

    price = price_var.get().strip()

    cost_price = cost_price_var.get().strip()

    quantity = quantity_var.get().strip()

    if (
        not item_name
        or not category
        or not price
        or not cost_price
        or not quantity
    ):

        messagebox.showwarning(
            "Missing Information",
            "Please fill all fields."
        )

        return

    try:

        price_value = float(price)

        cost_value = float(cost_price)

        quantity_value = int(quantity)

        if (
            price_value < 0
            or cost_value < 0
            or quantity_value < 0
        ):

            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Invalid Input",
            "Price and cost must be valid numbers and quantity must be a valid integer."
        )

        return

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE menu_items
            SET item_name = %s,
                category = %s,
                price = %s,
                cost_price = %s,
                available_quantity = %s
            WHERE item_id = %s
        """, (
            item_name,
            category,
            price_value,
            cost_value,
            quantity_value,
            item_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Menu item updated successfully."
        )

        clear_fields()

        load_menu_table()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# DELETE ITEM
# ============================================================

def delete_item():

    item_id = selected_id_var.get().strip()

    if not item_id:

        messagebox.showwarning(
            "Select Item",
            "Please select an item first."
        )

        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this menu item?"
    )

    if not confirm:
        return

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM menu_items
            WHERE item_id = %s
        """, (item_id,))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Menu item deleted successfully."
        )

        clear_fields()

        load_menu_table()

    except Exception as error:

        messagebox.showerror(
            "Delete Error",
            "This item may already be used in sales "
            "or food-waste records.\n\n"
            + str(error)
        )


# ============================================================
# SELECT TABLE ITEM
# ============================================================

def select_table_item(event=None):

    selected = table.selection()

    if not selected:
        return

    values = table.item(
        selected[0],
        "values"
    )

    if not values:
        return

    selected_id_var.set(values[0])

    item_name_var.set(values[1])

    category_var.set(values[2])

    price_var.set(values[3])

    cost_price_var.set(values[4])

    quantity_var.set(values[5])


# ============================================================
# OPEN MENU WINDOW
# ============================================================

def open_menu():

    global menu_window

    global item_name_var
    global category_var
    global price_var
    global cost_price_var
    global quantity_var

    global selected_id_var

    global item_name_combo

    global table

    global count_label

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    menu_window = tk.Toplevel()

    menu_window.title(
        "Menu Management"
    )

    menu_window.geometry(
        "1150x720"
    )

    menu_window.minsize(
        1050,
        650
    )

    menu_window.configure(
        bg=BG_COLOR
    )

    # IMPORTANT:
    # theme.py defines apply_theme() without arguments.
    apply_theme()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        menu_window,
        bg=PRIMARY_COLOR,
        height=80
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(
        False
    )

    tk.Label(
        header,
        text="Menu Management",
        bg=PRIMARY_COLOR,
        fg="white",
        font=TITLE_FONT
    ).pack(
        anchor="w",
        padx=25,
        pady=(15, 0)
    )

    tk.Label(
        header,
        text="Manage food items, prices, cost and available quantity",
        bg=PRIMARY_COLOR,
        fg="#DCE6F1",
        font=SUBTITLE_FONT
    ).pack(
        anchor="w",
        padx=25
    )

    # --------------------------------------------------------
    # MAIN CONTAINER
    # --------------------------------------------------------

    main = tk.Frame(
        menu_window,
        bg=BG_COLOR
    )

    main.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    # --------------------------------------------------------
    # FORM CARD
    # --------------------------------------------------------

    form_card = tk.Frame(
        main,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    form_card.pack(
        fill="x",
        pady=(0, 15)
    )

    tk.Label(
        form_card,
        text="Menu Item Details",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).grid(
        row=0,
        column=0,
        columnspan=4,
        sticky="w",
        padx=20,
        pady=(18, 15)
    )

    # --------------------------------------------------------
    # VARIABLES
    # --------------------------------------------------------

    selected_id_var = tk.StringVar()

    item_name_var = tk.StringVar()

    category_var = tk.StringVar()

    price_var = tk.StringVar()

    cost_price_var = tk.StringVar()

    quantity_var = tk.StringVar()

    # --------------------------------------------------------
    # ITEM NAME
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Item Name",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=0,
        sticky="w",
        padx=20,
        pady=5
    )

    item_name_combo = ttk.Combobox(
        form_card,
        textvariable=item_name_var,
        width=28,
        font=NORMAL_FONT
    )

    item_name_combo.grid(
        row=2,
        column=0,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    item_name_combo.bind(
        "<<ComboboxSelected>>",
        fill_existing_item
    )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Category",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=1,
        sticky="w",
        padx=20,
        pady=5
    )

    category_combo = ttk.Combobox(
        form_card,
        textvariable=category_var,
        state="readonly",
        values=[
            "Breakfast",
            "Snacks",
            "Beverage",
            "Lunch",
            "Dinner",
            "Other"
        ],
        width=22,
        font=NORMAL_FONT
    )

    category_combo.grid(
        row=2,
        column=1,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # SELLING PRICE
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Selling Price",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=2,
        sticky="w",
        padx=20,
        pady=5
    )

    ttk.Entry(
        form_card,
        textvariable=price_var,
        width=20,
        font=NORMAL_FONT
    ).grid(
        row=2,
        column=2,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # COST PRICE
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Cost Price",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=3,
        sticky="w",
        padx=20,
        pady=5
    )

    ttk.Entry(
        form_card,
        textvariable=cost_price_var,
        width=20,
        font=NORMAL_FONT
    ).grid(
        row=2,
        column=3,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # AVAILABLE QUANTITY
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Available Quantity",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=3,
        column=0,
        sticky="w",
        padx=20,
        pady=5
    )

    ttk.Entry(
        form_card,
        textvariable=quantity_var,
        width=20,
        font=NORMAL_FONT
    ).grid(
        row=4,
        column=0,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # COLUMN CONFIGURATION
    # --------------------------------------------------------

    for column in range(4):

        form_card.grid_columnconfigure(
            column,
            weight=1
        )

    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    button_frame = tk.Frame(
        form_card,
        bg=CARD_COLOR
    )

    button_frame.grid(
        row=4,
        column=1,
        columnspan=3,
        sticky="e",
        padx=20,
        pady=(0, 15)
    )

    create_button(
        button_frame,
        "Add Item",
        add_item,
        width=13,
        bg=SUCCESS_COLOR
    ).pack(
        side="left",
        padx=5
    )

    create_button(
        button_frame,
        "Update",
        update_item,
        width=13,
        bg=SECONDARY_COLOR
    ).pack(
        side="left",
        padx=5
    )

    create_button(
        button_frame,
        "Delete",
        delete_item,
        width=13,
        bg=DANGER_COLOR
    ).pack(
        side="left",
        padx=5
    )

    create_button(
        button_frame,
        "Clear",
        clear_fields,
        width=13,
        bg=WARNING_COLOR
    ).pack(
        side="left",
        padx=5
    )

    # --------------------------------------------------------
    # TABLE CARD
    # --------------------------------------------------------

    table_card = tk.Frame(
        main,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    table_card.pack(
        fill="both",
        expand=True
    )

    # --------------------------------------------------------
    # TABLE HEADER
    # --------------------------------------------------------

    top_table = tk.Frame(
        table_card,
        bg=CARD_COLOR
    )

    top_table.pack(
        fill="x",
        padx=20,
        pady=(15, 10)
    )

    tk.Label(
        top_table,
        text="Menu Items",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).pack(
        side="left"
    )

    count_label = tk.Label(
        top_table,
        text="Total Menu Items: 0",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    )

    count_label.pack(
        side="right"
    )

    # --------------------------------------------------------
    # TABLE FRAME
    # --------------------------------------------------------

    table_frame = tk.Frame(
        table_card,
        bg=CARD_COLOR
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    columns = (
        "ID",
        "Item Name",
        "Category",
        "Selling Price",
        "Cost Price",
        "Available Quantity"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    widths = {
        "ID": 60,
        "Item Name": 220,
        "Category": 150,
        "Selling Price": 130,
        "Cost Price": 130,
        "Available Quantity": 170
    }

    for column in columns:

        table.heading(
            column,
            text=column
        )

        table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    # --------------------------------------------------------
    # SCROLLBAR
    # --------------------------------------------------------

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # --------------------------------------------------------
    # TABLE SELECTION
    # --------------------------------------------------------

    table.bind(
        "<<TreeviewSelect>>",
        select_table_item
    )

    # --------------------------------------------------------
    # INITIAL DATA
    # --------------------------------------------------------

    load_menu_table()