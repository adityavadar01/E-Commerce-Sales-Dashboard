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


def load_customers():
    """Load all customers into the table."""
    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT customer_id,
                   customer_name,
                   phone,
                   city
            FROM customers
            ORDER BY customer_id
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


def load_customer_table():
    """Refresh customer table."""
    for item in customer_table.get_children():
        customer_table.delete(item)

    rows = load_customers()

    for row in rows:
        customer_table.insert(
            "",
            "end",
            values=row
        )

    count_label.config(
        text=f"Total Customers: {len(rows)}"
    )


def clear_fields():
    """Clear customer form."""
    selected_id_var.set("")
    customer_name_var.set("")
    phone_var.set("")
    city_var.set("")


def add_customer():
    """Add a new customer."""
    name = customer_name_var.get().strip()
    phone = phone_var.get().strip()
    city = city_var.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Information",
            "Please enter the customer name."
        )
        return

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO customers
            (customer_name, phone, city)
            VALUES (%s, %s, %s)
        """, (
            name,
            phone,
            city
        ))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Customer added successfully."
        )

        clear_fields()
        load_customer_table()

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )


def update_customer():
    """Update selected customer."""
    customer_id = selected_id_var.get().strip()

    if not customer_id:
        messagebox.showwarning(
            "Select Customer",
            "Please select a customer from the table first."
        )
        return

    name = customer_name_var.get().strip()
    phone = phone_var.get().strip()
    city = city_var.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Information",
            "Customer name cannot be empty."
        )
        return

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE customers
            SET customer_name = %s,
                phone = %s,
                city = %s
            WHERE customer_id = %s
        """, (
            name,
            phone,
            city,
            customer_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Customer updated successfully."
        )

        clear_fields()
        load_customer_table()

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )


def delete_customer():
    """Delete selected customer."""
    customer_id = selected_id_var.get().strip()

    if not customer_id:
        messagebox.showwarning(
            "Select Customer",
            "Please select a customer first."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this customer?"
    )

    if not confirm:
        return

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Customer deleted successfully."
        )

        clear_fields()
        load_customer_table()

    except Exception as error:
        messagebox.showerror(
            "Delete Error",
            "This customer may already be linked to a sale.\n\n"
            + str(error)
        )


def select_customer(event=None):
    """Load selected customer into form."""
    selected = customer_table.selection()

    if not selected:
        return

    values = customer_table.item(
        selected[0],
        "values"
    )

    if not values:
        return

    selected_id_var.set(values[0])
    customer_name_var.set(values[1])
    phone_var.set(values[2])
    city_var.set(values[3])


def open_customers():
    global customer_window
    global selected_id_var
    global customer_name_var
    global phone_var
    global city_var
    global customer_table
    global count_label

    customer_window = tk.Toplevel()
    customer_window.title("Customer Management")
    customer_window.geometry("1050x700")
    customer_window.minsize(950, 620)
    customer_window.configure(
        bg=BG_COLOR
    )

    # IMPORTANT:
    # apply_theme() takes no arguments.
    apply_theme()

    # Header
    header = tk.Frame(
        customer_window,
        bg=PRIMARY_COLOR,
        height=80
    )
    header.pack(
        fill="x"
    )
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Customer Management",
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
        text="Add, update and manage customer information",
        bg=PRIMARY_COLOR,
        fg="#DCE6F1",
        font=SUBTITLE_FONT
    ).pack(
        anchor="w",
        padx=25
    )

    # Main
    main = tk.Frame(
        customer_window,
        bg=BG_COLOR
    )
    main.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    # Form Card
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
        text="Customer Details",
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

    # Variables
    selected_id_var = tk.StringVar()
    customer_name_var = tk.StringVar()
    phone_var = tk.StringVar()
    city_var = tk.StringVar()

    # Customer Name
    tk.Label(
        form_card,
        text="Customer Name",
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

    ttk.Entry(
        form_card,
        textvariable=customer_name_var,
        width=25,
        font=NORMAL_FONT
    ).grid(
        row=2,
        column=0,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # Phone
    tk.Label(
        form_card,
        text="Phone",
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

    ttk.Entry(
        form_card,
        textvariable=phone_var,
        width=25,
        font=NORMAL_FONT
    ).grid(
        row=2,
        column=1,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    # City
    tk.Label(
        form_card,
        text="City",
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
        textvariable=city_var,
        width=25,
        font=NORMAL_FONT
    ).grid(
        row=2,
        column=2,
        sticky="ew",
        padx=20,
        pady=(0, 15)
    )

    for column in range(3):
        form_card.grid_columnconfigure(
            column,
            weight=1
        )

    # Buttons
    button_frame = tk.Frame(
        form_card,
        bg=CARD_COLOR
    )
    button_frame.grid(
        row=2,
        column=3,
        sticky="e",
        padx=20,
        pady=(0, 15)
    )

    create_button(
        button_frame,
        "Add Customer",
        add_customer,
        width=15,
        bg=SUCCESS_COLOR
    ).pack(
        pady=3
    )

    create_button(
        button_frame,
        "Update",
        update_customer,
        width=15,
        bg=SECONDARY_COLOR
    ).pack(
        pady=3
    )

    create_button(
        button_frame,
        "Delete",
        delete_customer,
        width=15,
        bg=DANGER_COLOR
    ).pack(
        pady=3
    )

    create_button(
        button_frame,
        "Clear",
        clear_fields,
        width=15,
        bg=WARNING_COLOR
    ).pack(
        pady=3
    )

    # Table Card
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
        text="Customer List",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).pack(
        side="left"
    )

    count_label = tk.Label(
        top_table,
        text="Total Customers: 0",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    )
    count_label.pack(
        side="right"
    )

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
        "Customer Name",
        "Phone",
        "City"
    )

    customer_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    customer_table.heading(
        "ID",
        text="ID"
    )

    customer_table.heading(
        "Customer Name",
        text="Customer Name"
    )

    customer_table.heading(
        "Phone",
        text="Phone"
    )

    customer_table.heading(
        "City",
        text="City"
    )

    customer_table.column(
        "ID",
        width=80,
        anchor="center"
    )

    customer_table.column(
        "Customer Name",
        width=300,
        anchor="center"
    )

    customer_table.column(
        "Phone",
        width=220,
        anchor="center"
    )

    customer_table.column(
        "City",
        width=250,
        anchor="center"
    )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=customer_table.yview
    )

    customer_table.configure(
        yscrollcommand=scrollbar.set
    )

    customer_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    customer_table.bind(
        "<<TreeviewSelect>>",
        select_customer
    )

    load_customer_table()