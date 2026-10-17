import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme, create_button

import os
from datetime import datetime


# ============================================================
# GLOBAL VARIABLES
# ============================================================

customer_combo = None
menu_combo = None
payment_combo = None
quantity_entry = None
price_entry = None
stock_entry = None
total_label = None
sales_table = None
count_label = None

last_sale_id = None


# ============================================================
# LOAD CUSTOMERS
# ============================================================

def load_customers(customer_combo):

    try:

        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT customer_id, customer_name
            FROM customers
            ORDER BY customer_name
        """)

        customers = cursor.fetchall()

        customer_combo["values"] = [
            f"{customer[0]} - {customer[1]}"
            for customer in customers
        ]

        cursor.close()
        db.close()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# LOAD MENU ITEMS
# ============================================================

def load_menu_items(menu_combo):

    try:

        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT item_id, item_name
            FROM menu_items
            ORDER BY item_name
        """)

        items = cursor.fetchall()

        menu_combo["values"] = [
            f"{item[0]} - {item[1]}"
            for item in items
        ]

        cursor.close()
        db.close()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# GET ITEM DETAILS
# ============================================================

def get_item_details(event=None):

    selected = menu_combo.get()

    if not selected:
        return

    try:

        item_id = int(
            selected.split(" - ")[0]
        )

        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                price,
                cost_price,
                available_quantity
            FROM menu_items
            WHERE item_id = %s
        """, (item_id,))

        item = cursor.fetchone()

        cursor.close()
        db.close()

        if item:

            price, cost, stock = item

            price_entry.config(
                state="normal"
            )

            price_entry.delete(
                0,
                tk.END
            )

            price_entry.insert(
                0,
                f"{price:.2f}"
            )

            price_entry.config(
                state="readonly"
            )

            stock_entry.config(
                state="normal"
            )

            stock_entry.delete(
                0,
                tk.END
            )

            stock_entry.insert(
                0,
                str(stock)
            )

            stock_entry.config(
                state="readonly"
            )

            calculate_total()

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )


# ============================================================
# CALCULATE TOTAL
# ============================================================

def calculate_total(event=None):

    try:

        price = float(
            price_entry.get()
        )

        quantity = int(
            quantity_entry.get()
        )

        if quantity < 1:

            total = 0

        else:

            total = price * quantity

        total_label.config(
            text=f"₹{total:.2f}"
        )

    except ValueError:

        total_label.config(
            text="₹0.00"
        )


# ============================================================
# CREATE SALE
# ============================================================

def create_sale():

    global last_sale_id

    selected_customer = customer_combo.get()
    selected_item = menu_combo.get()
    payment_mode = payment_combo.get()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not selected_item:

        messagebox.showwarning(
            "Missing Information",
            "Please select a menu item."
        )

        return

    if not payment_mode:

        messagebox.showwarning(
            "Missing Information",
            "Please select payment mode."
        )

        return

    try:

        quantity = int(
            quantity_entry.get()
        )

        if quantity <= 0:

            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be greater than 0."
            )

            return

    except ValueError:

        messagebox.showwarning(
            "Invalid Quantity",
            "Please enter a valid quantity."
        )

        return

    db = None
    cursor = None

    try:

        item_id = int(
            selected_item.split(" - ")[0]
        )

        customer_id = None

        if selected_customer:

            customer_id = int(
                selected_customer.split(" - ")[0]
            )

        db = connect_database()
        cursor = db.cursor()

        # ----------------------------------------------------
        # GET LATEST ITEM DETAILS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                price,
                cost_price,
                available_quantity
            FROM menu_items
            WHERE item_id = %s
        """, (item_id,))

        item = cursor.fetchone()

        if not item:

            messagebox.showerror(
                "Error",
                "Menu item not found."
            )

            return

        price, cost_price, available_quantity = item

        # ----------------------------------------------------
        # STOCK CHECK
        # ----------------------------------------------------

        if quantity > available_quantity:

            messagebox.showwarning(
                "Insufficient Stock",
                f"Only {available_quantity} units are available."
            )

            return

        # ----------------------------------------------------
        # CALCULATE
        # ----------------------------------------------------

        total_amount = price * quantity

        profit = (
            price - cost_price
        ) * quantity

        # ----------------------------------------------------
        # INSERT SALE
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO sales
            (
                customer_id,
                sale_date,
                sale_time,
                payment_mode,
                total_amount
            )
            VALUES
            (
                %s,
                CURDATE(),
                CURTIME(),
                %s,
                %s
            )
        """, (
            customer_id,
            payment_mode,
            total_amount
        ))

        sale_id = cursor.lastrowid

        # ----------------------------------------------------
        # INSERT SALE ITEM
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO sale_items
            (
                sale_id,
                item_id,
                quantity,
                price,
                profit
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            sale_id,
            item_id,
            quantity,
            price,
            profit
        ))

        # ----------------------------------------------------
        # REDUCE STOCK
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE menu_items
            SET available_quantity =
                available_quantity - %s
            WHERE item_id = %s
        """, (
            quantity,
            item_id
        ))

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.commit()

        last_sale_id = sale_id

        # ----------------------------------------------------
        # UPDATE PRINT BUTTON
        # ----------------------------------------------------

        if print_bill_button is not None:

            print_bill_button.config(
                state="normal"
            )

        messagebox.showinfo(
            "Sale Recorded",
            f"Sale #{sale_id} recorded successfully!\n\n"
            f"Total Amount: ₹{total_amount:.2f}\n"
            f"Profit: ₹{profit:.2f}\n\n"
            f"You can now click 'Print Last Bill'."
        )

        clear_sale_form()

        load_sales()

        # Reload menu stock
        load_menu_items(menu_combo)

        # Restore selected item if possible
        for value in menu_combo["values"]:

            if value.startswith(
                f"{item_id} - "
            ):

                menu_combo.set(value)

                get_item_details()

                break

    except Exception as error:

        if db:

            try:
                db.rollback()
            except:
                pass

        messagebox.showerror(
            "Database Error",
            str(error)
        )

    finally:

        if cursor:

            try:
                cursor.close()
            except:
                pass

        if db:

            try:
                db.close()
            except:
                pass


# ============================================================
# CLEAR SALE FORM
# ============================================================

def clear_sale_form():

    customer_combo.set("")

    menu_combo.set("")

    payment_combo.set("")

    quantity_entry.delete(
        0,
        tk.END
    )

    quantity_entry.insert(
        0,
        "1"
    )

    price_entry.config(
        state="normal"
    )

    price_entry.delete(
        0,
        tk.END
    )

    price_entry.config(
        state="readonly"
    )

    stock_entry.config(
        state="normal"
    )

    stock_entry.delete(
        0,
        tk.END
    )

    stock_entry.config(
        state="readonly"
    )

    total_label.config(
        text="₹0.00"
    )


# ============================================================
# LOAD SALES
# ============================================================

def load_sales():

    for row in sales_table.get_children():

        sales_table.delete(row)

    try:

        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                s.sale_id,
                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ),
                s.sale_date,
                s.sale_time,
                s.payment_mode,
                s.total_amount

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            ORDER BY
                s.sale_id DESC
        """)

        sales = cursor.fetchall()

        for sale in sales:

            (
                sale_id,
                customer,
                date,
                time,
                payment,
                total
            ) = sale

            sales_table.insert(
                "",
                tk.END,
                values=(
                    sale_id,
                    customer,
                    date,
                    time,
                    payment,
                    f"₹{total:.2f}"
                )
            )

        cursor.close()
        db.close()

        count_label.config(
            text=f"Total Orders: {len(sales)}"
        )

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ============================================================
# GET LATEST SALE ID
# ============================================================

def get_latest_sale_id():

    try:

        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT MAX(sale_id)
            FROM sales
        """)

        result = cursor.fetchone()

        cursor.close()
        db.close()

        if result and result[0]:

            return result[0]

        return None

    except Exception:

        return None


# ============================================================
# GENERATE BILL
# ============================================================

def generate_bill(sale_id):

    if not sale_id:

        messagebox.showwarning(
            "No Sale",
            "There is no sale available to print."
        )

        return None

    db = None
    cursor = None

    try:

        db = connect_database()
        cursor = db.cursor()

        # ----------------------------------------------------
        # SALE INFORMATION
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                s.sale_id,
                s.sale_date,
                s.sale_time,
                s.payment_mode,
                s.total_amount,
                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                )

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            WHERE s.sale_id = %s
        """, (sale_id,))

        sale = cursor.fetchone()

        if not sale:

            messagebox.showerror(
                "Bill Error",
                "Sale record not found."
            )

            return None

        (
            sale_id,
            sale_date,
            sale_time,
            payment_mode,
            total_amount,
            customer_name
        ) = sale

        # ----------------------------------------------------
        # SALE ITEMS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                m.item_name,
                si.quantity,
                si.price,
                si.quantity * si.price AS amount

            FROM sale_items si

            INNER JOIN menu_items m
                ON si.item_id = m.item_id

            WHERE si.sale_id = %s

            ORDER BY si.sale_item_id
        """, (sale_id,))

        items = cursor.fetchall()

        # ----------------------------------------------------
        # CREATE BILLS FOLDER
        # ----------------------------------------------------

        bills_folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "Bills"
        )

        os.makedirs(
            bills_folder,
            exist_ok=True
        )

        # ----------------------------------------------------
        # BILL FILE
        # ----------------------------------------------------

        bill_path = os.path.join(
            bills_folder,
            f"Bill_{sale_id}.txt"
        )

        # ----------------------------------------------------
        # BUILD BILL
        # ----------------------------------------------------

        lines = []

        lines.append(
            "========================================"
        )

        lines.append(
            "          GANESH NASHTA CENTER"
        )

        lines.append(
            "========================================"
        )

        lines.append(
            "                SALES BILL"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"Bill No.       : {sale_id}"
        )

        lines.append(
            f"Date           : {sale_date}"
        )

        lines.append(
            f"Time           : {sale_time}"
        )

        lines.append(
            f"Customer       : {customer_name}"
        )

        lines.append(
            f"Payment Mode   : {payment_mode}"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"{'Item':<22}{'Qty':>5}{'Amount':>11}"
        )

        lines.append(
            "----------------------------------------"
        )

        for item in items:

            item_name = str(item[0])
            quantity = item[1]
            price = float(item[2])
            amount = float(item[3])

            # Limit item name length
            if len(item_name) > 21:

                item_name = item_name[:21]

            lines.append(
                f"{item_name:<22}"
                f"{quantity:>5}"
                f"₹{amount:>9.2f}"
            )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"{'TOTAL':<27}"
            f"₹{float(total_amount):>9.2f}"
        )

        lines.append(
            "========================================"
        )

        lines.append(
            "          Thank You!"
        )

        lines.append(
            "       Visit Again Soon"
        )

        lines.append(
            "========================================"
        )

        # ----------------------------------------------------
        # WRITE FILE
        # ----------------------------------------------------

        with open(
            bill_path,
            "w",
            encoding="utf-8"
        ) as bill_file:

            bill_file.write(
                "\n".join(lines)
            )

        return bill_path

    except Exception as error:

        messagebox.showerror(
            "Bill Error",
            str(error)
        )

        return None

    finally:

        if cursor:

            try:
                cursor.close()
            except:
                pass

        if db:

            try:
                db.close()
            except:
                pass


# ============================================================
# PRINT BILL
# ============================================================

def print_bill():

    global last_sale_id

    # If no sale was created during this session,
    # use the latest sale from the database.

    if not last_sale_id:

        last_sale_id = get_latest_sale_id()

    if not last_sale_id:

        messagebox.showwarning(
            "No Bill Available",
            "No sale has been recorded yet."
        )

        return

    bill_path = generate_bill(
        last_sale_id
    )

    if not bill_path:

        return

    try:

        # ----------------------------------------------------
        # SEND BILL TO DEFAULT WINDOWS PRINTER
        # ----------------------------------------------------

        os.startfile(
            bill_path,
            "print"
        )

        messagebox.showinfo(
            "Bill Printed",
            f"Bill #{last_sale_id} has been sent "
            f"to the default printer.\n\n"
            f"Bill saved at:\n{bill_path}"
        )

    except Exception as error:

        # If automatic printing isn't available,
        # open the bill instead.

        try:

            os.startfile(
                bill_path
            )

            messagebox.showwarning(
                "Printing Not Available",
                "The bill was generated successfully, "
                "but Windows could not send it directly "
                "to the printer.\n\n"
                "The bill has been opened so you can "
                "print it manually."
            )

        except Exception as open_error:

            messagebox.showerror(
                "Print Error",
                str(error)
                + "\n\n"
                + str(open_error)
            )


# ============================================================
# VIEW BILL
# ============================================================

def view_bill():

    global last_sale_id

    if not last_sale_id:

        last_sale_id = get_latest_sale_id()

    if not last_sale_id:

        messagebox.showwarning(
            "No Bill Available",
            "No sale has been recorded yet."
        )

        return

    bill_path = generate_bill(
        last_sale_id
    )

    if not bill_path:

        return

    try:

        os.startfile(
            bill_path
        )

    except Exception as error:

        messagebox.showerror(
            "Bill Error",
            str(error)
        )


# ============================================================
# OPEN SALES WINDOW
# ============================================================

def open_sales():

    global customer_combo
    global menu_combo
    global payment_combo
    global quantity_entry
    global price_entry
    global stock_entry
    global total_label
    global sales_table
    global count_label
    global print_bill_button
    global last_sale_id

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    window = tk.Toplevel()

    window.title(
        "Sales Management - Ganesh Nashta Center"
    )

    window.geometry(
        "1150x720"
    )

    window.minsize(
        1000,
        650
    )

    apply_theme()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        window,
        bg="#1F4E78",
        height=75
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(
        False
    )

    tk.Label(
        header,
        text="Sales Management",
        font=("Segoe UI", 22, "bold"),
        bg="#1F4E78",
        fg="white"
    ).pack(
        anchor="w",
        padx=25,
        pady=(15, 0)
    )

    tk.Label(
        header,
        text="Record sales, generate and print bills",
        font=("Segoe UI", 10),
        bg="#1F4E78",
        fg="#DCE6F1"
    ).pack(
        anchor="w",
        padx=27
    )

    # --------------------------------------------------------
    # SALE FORM
    # --------------------------------------------------------

    form_card = tk.LabelFrame(
        window,
        text="  Create New Sale  ",
        font=("Segoe UI", 11, "bold"),
        padx=15,
        pady=12
    )

    form_card.pack(
        fill="x",
        padx=20,
        pady=18
    )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Customer",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=7
    )

    customer_combo = ttk.Combobox(
        form_card,
        state="readonly",
        width=27
    )

    customer_combo.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 10)
    )

    # --------------------------------------------------------
    # MENU ITEM
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Menu Item",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=10,
        pady=7
    )

    menu_combo = ttk.Combobox(
        form_card,
        state="readonly",
        width=27
    )

    menu_combo.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 10)
    )

    menu_combo.bind(
        "<<ComboboxSelected>>",
        get_item_details
    )

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Selling Price",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=2,
        sticky="w",
        padx=10,
        pady=7
    )

    price_entry = ttk.Entry(
        form_card,
        width=18,
        state="readonly"
    )

    price_entry.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 10)
    )

    # --------------------------------------------------------
    # STOCK
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Available Stock",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=3,
        sticky="w",
        padx=10,
        pady=7
    )

    stock_entry = ttk.Entry(
        form_card,
        width=18,
        state="readonly"
    )

    stock_entry.grid(
        row=1,
        column=3,
        padx=10,
        pady=(0, 10)
    )

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=2,
        column=0,
        sticky="w",
        padx=10,
        pady=7
    )

    quantity_entry = ttk.Entry(
        form_card,
        width=18
    )

    quantity_entry.insert(
        0,
        "1"
    )

    quantity_entry.grid(
        row=3,
        column=0,
        padx=10,
        pady=(0, 10)
    )

    quantity_entry.bind(
        "<KeyRelease>",
        calculate_total
    )

    # --------------------------------------------------------
    # PAYMENT MODE
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Payment Mode",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=2,
        column=1,
        sticky="w",
        padx=10,
        pady=7
    )

    payment_combo = ttk.Combobox(
        form_card,
        values=[
            "Cash",
            "UPI",
            "Card"
        ],
        state="readonly",
        width=25
    )

    payment_combo.grid(
        row=3,
        column=1,
        padx=10,
        pady=(0, 10)
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    tk.Label(
        form_card,
        text="Total Amount",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=2,
        column=2,
        sticky="w",
        padx=10,
        pady=7
    )

    total_label = tk.Label(
        form_card,
        text="₹0.00",
        font=("Segoe UI", 18, "bold"),
        fg="#1F4E78"
    )

    total_label.grid(
        row=3,
        column=2,
        sticky="w",
        padx=10,
        pady=(0, 10)
    )

    # --------------------------------------------------------
    # BUTTON FRAME
    # --------------------------------------------------------

    button_frame = tk.Frame(
        form_card
    )

    button_frame.grid(
        row=3,
        column=3,
        padx=10,
        pady=(0, 10)
    )

    # Record Sale

    create_button(
        button_frame,
        "Record Sale",
        create_sale,
        width=14,
        bg="#1F4E78"
    ).pack(
        side="left",
        padx=3
    )

    # Clear

    create_button(
        button_frame,
        "Clear",
        clear_sale_form,
        width=9,
        bg="#6B7280"
    ).pack(
        side="left",
        padx=3
    )

    # Print Bill

    print_bill_button = create_button(
        button_frame,
        "Print Last Bill",
        print_bill,
        width=15,
        bg="#2E75B6"
    )

    print_bill_button.pack(
        side="left",
        padx=3
    )

    # View Bill

    create_button(
        button_frame,
        "View Bill",
        view_bill,
        width=11,
        bg="#70AD47"
    ).pack(
        side="left",
        padx=3
    )

    # --------------------------------------------------------
    # SALES TABLE HEADER
    # --------------------------------------------------------

    table_header = tk.Frame(
        window
    )

    table_header.pack(
        fill="x",
        padx=25,
        pady=(0, 8)
    )

    tk.Label(
        table_header,
        text="Recent Sales",
        font=("Segoe UI", 15, "bold"),
        fg="#1F2937"
    ).pack(
        side="left"
    )

    count_label = tk.Label(
        table_header,
        text="Total Orders: 0",
        font=("Segoe UI", 10, "bold"),
        fg="#5B6573"
    )

    count_label.pack(
        side="right"
    )

    # --------------------------------------------------------
    # SALES TABLE
    # --------------------------------------------------------

    table_frame = tk.Frame(
        window
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 20)
    )

    columns = (
        "ID",
        "Customer",
        "Date",
        "Time",
        "Payment Mode",
        "Total"
    )

    sales_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    widths = {
        "ID": 70,
        "Customer": 220,
        "Date": 130,
        "Time": 120,
        "Payment Mode": 150,
        "Total": 140
    }

    for column in columns:

        sales_table.heading(
            column,
            text=column
        )

        sales_table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=sales_table.yview
    )

    sales_table.configure(
        yscrollcommand=scrollbar.set
    )

    sales_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # --------------------------------------------------------
    # INITIAL DATA
    # --------------------------------------------------------

    load_customers(
        customer_combo
    )

    load_menu_items(
        menu_combo
    )

    load_sales()

    # --------------------------------------------------------
    # GET LATEST SALE
    # --------------------------------------------------------

    last_sale_id = get_latest_sale_id()

    if last_sale_id:

        print_bill_button.config(
            state="normal"
        )

    else:

        print_bill_button.config(
            state="disabled"
        )