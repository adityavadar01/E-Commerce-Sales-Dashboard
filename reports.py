import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

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
    BORDER_COLOR,
    TITLE_FONT,
    SUBTITLE_FONT,
    HEADING_FONT,
    NORMAL_FONT,
    create_button
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

reports_window = None

start_date_var = None
end_date_var = None

sales_value_label = None
profit_value_label = None
orders_value_label = None
items_value_label = None

sales_table = None
top_items_table = None
payment_table = None

sales_count_label = None


# ============================================================
# DATE FILTER
# ============================================================

def get_date_filter():

    start_date = start_date_var.get().strip()
    end_date = end_date_var.get().strip()

    condition = ""
    params = []

    if start_date:

        try:
            datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )
        except ValueError:
            raise ValueError(
                "Start date must be in YYYY-MM-DD format."
            )

        condition += " AND s.sale_date >= %s "
        params.append(start_date)

    if end_date:

        try:
            datetime.strptime(
                end_date,
                "%Y-%m-%d"
            )
        except ValueError:
            raise ValueError(
                "End date must be in YYYY-MM-DD format."
            )

        condition += " AND s.sale_date <= %s "
        params.append(end_date)

    if start_date and end_date:

        if start_date > end_date:
            raise ValueError(
                "Start date cannot be greater than end date."
            )

    return condition, params


# ============================================================
# LOAD SUMMARY
# ============================================================

def load_summary():

    condition, params = get_date_filter()

    connection = connect_database()
    cursor = connection.cursor()

    try:

        # Total Sales
        query_sales = f"""
            SELECT COALESCE(SUM(s.total_amount), 0)
            FROM sales s
            WHERE 1=1
            {condition}
        """

        cursor.execute(
            query_sales,
            tuple(params)
        )

        result = cursor.fetchone()
        total_sales = result[0] if result else 0

        # Total Orders
        query_orders = f"""
            SELECT COUNT(*)
            FROM sales s
            WHERE 1=1
            {condition}
        """

        cursor.execute(
            query_orders,
            tuple(params)
        )

        result = cursor.fetchone()
        total_orders = result[0] if result else 0

        # Total Profit + Items Sold
        query_items = f"""
            SELECT
                COALESCE(SUM(si.profit), 0),
                COALESCE(SUM(si.quantity), 0)
            FROM sale_items si
            INNER JOIN sales s
                ON si.sale_id = s.sale_id
            WHERE 1=1
            {condition}
        """

        cursor.execute(
            query_items,
            tuple(params)
        )

        result = cursor.fetchone()

        if result:
            total_profit = result[0]
            items_sold = result[1]
        else:
            total_profit = 0
            items_sold = 0

        # Update dashboard values
        sales_value_label.config(
            text=f"₹{float(total_sales):,.2f}"
        )

        profit_value_label.config(
            text=f"₹{float(total_profit):,.2f}"
        )

        orders_value_label.config(
            text=str(total_orders)
        )

        items_value_label.config(
            text=str(items_sold)
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# LOAD SALES REPORT
# ============================================================

def load_sales_report():

    condition, params = get_date_filter()

    connection = connect_database()
    cursor = connection.cursor()

    try:

        query = f"""
            SELECT
                s.sale_id,
                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ),
                s.sale_date,
                s.sale_time,
                s.payment_mode,
                s.total_amount,
                COALESCE(SUM(si.quantity), 0),
                COALESCE(SUM(si.profit), 0)

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.customer_id

            LEFT JOIN sale_items si
                ON s.sale_id = si.sale_id

            WHERE 1=1
            {condition}

            GROUP BY
                s.sale_id,
                c.customer_name,
                s.sale_date,
                s.sale_time,
                s.payment_mode,
                s.total_amount

            ORDER BY
                s.sale_date DESC,
                s.sale_time DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        # Clear table
        for item in sales_table.get_children():
            sales_table.delete(item)

        # Add rows
        for row in rows:

            sales_table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    f"₹{float(row[5]):,.2f}",
                    row[6],
                    f"₹{float(row[7]):,.2f}"
                )
            )

        sales_count_label.config(
            text=f"Records: {len(rows)}"
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# LOAD TOP SELLING ITEMS
# ============================================================

def load_top_items():

    condition, params = get_date_filter()

    connection = connect_database()
    cursor = connection.cursor()

    try:

        query = f"""
            SELECT
                m.item_name,
                COALESCE(SUM(si.quantity), 0),
                COALESCE(
                    SUM(si.quantity * si.price),
                    0
                ),
                COALESCE(SUM(si.profit), 0)

            FROM sale_items si

            INNER JOIN sales s
                ON si.sale_id = s.sale_id

            INNER JOIN menu_items m
                ON si.item_id = m.item_id

            WHERE 1=1
            {condition}

            GROUP BY
                m.item_id,
                m.item_name

            ORDER BY
                SUM(si.quantity) DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        for item in top_items_table.get_children():
            top_items_table.delete(item)

        for row in rows:

            top_items_table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    f"₹{float(row[2]):,.2f}",
                    f"₹{float(row[3]):,.2f}"
                )
            )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# LOAD PAYMENT ANALYSIS
# ============================================================

def load_payment_analysis():

    condition, params = get_date_filter()

    connection = connect_database()
    cursor = connection.cursor()

    try:

        query = f"""
            SELECT
                s.payment_mode,
                COUNT(*),
                COALESCE(SUM(s.total_amount), 0)

            FROM sales s

            WHERE 1=1
            {condition}

            GROUP BY
                s.payment_mode

            ORDER BY
                SUM(s.total_amount) DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        for item in payment_table.get_children():
            payment_table.delete(item)

        for row in rows:

            payment_table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    f"₹{float(row[2]):,.2f}"
                )
            )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report():

    try:

        load_summary()
        load_sales_report()
        load_top_items()
        load_payment_analysis()

        # IMPORTANT:
        # No success popup here.
        # The report simply loads.

    except ValueError as error:

        messagebox.showerror(
            "Invalid Date",
            str(error)
        )

    except Exception as error:

        messagebox.showerror(
            "Report Error",
            "Unable to generate report.\n\n"
            + str(error)
        )


# ============================================================
# CLEAR FILTERS
# ============================================================

def clear_filters():

    start_date_var.set("")
    end_date_var.set("")

    generate_report()


# ============================================================
# EXPORT CSV
# ============================================================

def export_csv():

    try:

        rows = []

        for item in sales_table.get_children():

            values = sales_table.item(
                item,
                "values"
            )

            rows.append(values)

        if not rows:

            messagebox.showwarning(
                "No Data",
                "There is no sales data to export."
            )

            return

        file_path = filedialog.asksaveasfilename(
            title="Save Sales Report",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Sale ID",
                "Customer",
                "Date",
                "Time",
                "Payment Mode",
                "Total Amount",
                "Items Sold",
                "Profit"
            ])

            writer.writerows(rows)

        messagebox.showinfo(
            "Export Successful",
            "Sales report exported successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ============================================================
# OPEN REPORTS
# ============================================================

def open_reports():

    global reports_window
    global start_date_var
    global end_date_var

    global sales_value_label
    global profit_value_label
    global orders_value_label
    global items_value_label

    global sales_table
    global top_items_table
    global payment_table

    global sales_count_label

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    reports_window = tk.Toplevel()

    reports_window.title(
        "Reports"
    )

    reports_window.geometry(
        "1250x800"
    )

    reports_window.minsize(
        1100,
        700
    )

    reports_window.configure(
        bg=BG_COLOR
    )

    apply_theme()

    # --------------------------------------------------------
    # VARIABLES
    # --------------------------------------------------------

    start_date_var = tk.StringVar(
        master=reports_window,
        value=""
    )

    end_date_var = tk.StringVar(
        master=reports_window,
        value=""
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        reports_window,
        bg=PRIMARY_COLOR,
        height=80
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)

    tk.Label(
        header,
        text="Business Reports",
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
        text="Generate and analyze sales performance reports",
        bg=PRIMARY_COLOR,
        fg="#DCE6F1",
        font=SUBTITLE_FONT
    ).pack(
        anchor="w",
        padx=25
    )

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

    main = tk.Frame(
        reports_window,
        bg=BG_COLOR
    )

    main.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    # --------------------------------------------------------
    # FILTER CARD
    # --------------------------------------------------------

    filter_card = tk.Frame(
        main,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    filter_card.pack(
        fill="x",
        pady=(0, 15)
    )

    tk.Label(
        filter_card,
        text="Report Filters",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).grid(
        row=0,
        column=0,
        columnspan=8,
        padx=20,
        pady=(15, 5),
        sticky="w"
    )

    # Start Date

    tk.Label(
        filter_card,
        text="Start Date",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=0,
        padx=(20, 5),
        pady=(5, 15)
    )

    ttk.Entry(
        filter_card,
        textvariable=start_date_var,
        width=18,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=1,
        padx=5,
        pady=(5, 15)
    )

    # End Date

    tk.Label(
        filter_card,
        text="End Date",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=2,
        padx=(15, 5),
        pady=(5, 15)
    )

    ttk.Entry(
        filter_card,
        textvariable=end_date_var,
        width=18,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=3,
        padx=5,
        pady=(5, 15)
    )

    tk.Label(
        filter_card,
        text="YYYY-MM-DD",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    ).grid(
        row=1,
        column=4,
        padx=10,
        pady=(5, 15)
    )

    # Generate

    create_button(
        filter_card,
        "Generate Report",
        generate_report,
        width=17,
        bg=PRIMARY_COLOR
    ).grid(
        row=1,
        column=5,
        padx=5,
        pady=(5, 15)
    )

    # Clear

    create_button(
        filter_card,
        "Clear Filters",
        clear_filters,
        width=14,
        bg=WARNING_COLOR
    ).grid(
        row=1,
        column=6,
        padx=5,
        pady=(5, 15)
    )

    # Export

    create_button(
        filter_card,
        "Export CSV",
        export_csv,
        width=14,
        bg=ACCENT_COLOR
    ).grid(
        row=1,
        column=7,
        padx=(5, 20),
        pady=(5, 15)
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    kpi_frame = tk.Frame(
        main,
        bg=BG_COLOR
    )

    kpi_frame.pack(
        fill="x",
        pady=(0, 15)
    )

    # Total Sales

    sales_card = tk.Frame(
        kpi_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    sales_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    tk.Label(
        sales_card,
        text="Total Sales",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    ).pack(
        pady=(15, 5)
    )

    sales_value_label = tk.Label(
        sales_card,
        text="₹0.00",
        bg=CARD_COLOR,
        fg=PRIMARY_COLOR,
        font=("Segoe UI", 20, "bold")
    )

    sales_value_label.pack(
        pady=(0, 15)
    )

    # Total Profit

    profit_card = tk.Frame(
        kpi_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    profit_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=8
    )

    tk.Label(
        profit_card,
        text="Total Profit",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    ).pack(
        pady=(15, 5)
    )

    profit_value_label = tk.Label(
        profit_card,
        text="₹0.00",
        bg=CARD_COLOR,
        fg=SUCCESS_COLOR,
        font=("Segoe UI", 20, "bold")
    )

    profit_value_label.pack(
        pady=(0, 15)
    )

    # Total Orders

    orders_card = tk.Frame(
        kpi_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    orders_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=8
    )

    tk.Label(
        orders_card,
        text="Total Orders",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    ).pack(
        pady=(15, 5)
    )

    orders_value_label = tk.Label(
        orders_card,
        text="0",
        bg=CARD_COLOR,
        fg=SECONDARY_COLOR,
        font=("Segoe UI", 20, "bold")
    )

    orders_value_label.pack(
        pady=(0, 15)
    )

    # Items Sold

    items_card = tk.Frame(
        kpi_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    items_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )

    tk.Label(
        items_card,
        text="Items Sold",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    ).pack(
        pady=(15, 5)
    )

    items_value_label = tk.Label(
        items_card,
        text="0",
        bg=CARD_COLOR,
        fg=ACCENT_COLOR,
        font=("Segoe UI", 20, "bold")
    )

    items_value_label.pack(
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # SALES TABLE
    # --------------------------------------------------------

    sales_card_frame = tk.Frame(
        main,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    sales_card_frame.pack(
        fill="both",
        expand=True,
        pady=(0, 15)
    )

    sales_header = tk.Frame(
        sales_card_frame,
        bg=CARD_COLOR
    )

    sales_header.pack(
        fill="x",
        padx=15,
        pady=(10, 5)
    )

    tk.Label(
        sales_header,
        text="Detailed Sales Report",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).pack(
        side="left"
    )

    sales_count_label = tk.Label(
        sales_header,
        text="Records: 0",
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT,
        font=NORMAL_FONT
    )

    sales_count_label.pack(
        side="right"
    )

    sales_table_frame = tk.Frame(
        sales_card_frame,
        bg=CARD_COLOR
    )

    sales_table_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )

    sales_columns = (
        "Sale ID",
        "Customer",
        "Date",
        "Time",
        "Payment",
        "Total",
        "Items",
        "Profit"
    )

    sales_table = ttk.Treeview(
        sales_table_frame,
        columns=sales_columns,
        show="headings"
    )

    sales_widths = {
        "Sale ID": 70,
        "Customer": 180,
        "Date": 100,
        "Time": 90,
        "Payment": 100,
        "Total": 110,
        "Items": 80,
        "Profit": 110
    }

    for column in sales_columns:

        sales_table.heading(
            column,
            text=column
        )

        sales_table.column(
            column,
            width=sales_widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        sales_table_frame,
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
    # LOWER FRAME
    # --------------------------------------------------------

    lower_frame = tk.Frame(
        main,
        bg=BG_COLOR
    )

    lower_frame.pack(
        fill="both",
        expand=True
    )

    # --------------------------------------------------------
    # TOP SELLING ITEMS
    # --------------------------------------------------------

    top_items_card = tk.Frame(
        lower_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    top_items_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    tk.Label(
        top_items_card,
        text="Top Selling Items",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).pack(
        anchor="w",
        padx=15,
        pady=(12, 8)
    )

    top_items_table = ttk.Treeview(
        top_items_card,
        columns=(
            "Item",
            "Quantity",
            "Revenue",
            "Profit"
        ),
        show="headings"
    )

    top_items_table.heading(
        "Item",
        text="Item"
    )

    top_items_table.heading(
        "Quantity",
        text="Quantity"
    )

    top_items_table.heading(
        "Revenue",
        text="Revenue"
    )

    top_items_table.heading(
        "Profit",
        text="Profit"
    )

    top_items_table.column(
        "Item",
        width=160
    )

    top_items_table.column(
        "Quantity",
        width=80,
        anchor="center"
    )

    top_items_table.column(
        "Revenue",
        width=110,
        anchor="center"
    )

    top_items_table.column(
        "Profit",
        width=110,
        anchor="center"
    )

    top_items_table.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # PAYMENT ANALYSIS
    # --------------------------------------------------------

    payment_card = tk.Frame(
        lower_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    payment_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )

    tk.Label(
        payment_card,
        text="Payment Mode Analysis",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=HEADING_FONT
    ).pack(
        anchor="w",
        padx=15,
        pady=(12, 8)
    )

    payment_table = ttk.Treeview(
        payment_card,
        columns=(
            "Payment Mode",
            "Orders",
            "Sales"
        ),
        show="headings"
    )

    payment_table.heading(
        "Payment Mode",
        text="Payment Mode"
    )

    payment_table.heading(
        "Orders",
        text="Orders"
    )

    payment_table.heading(
        "Sales",
        text="Sales"
    )

    payment_table.column(
        "Payment Mode",
        width=150
    )

    payment_table.column(
        "Orders",
        width=100,
        anchor="center"
    )

    payment_table.column(
        "Sales",
        width=130,
        anchor="center"
    )

    payment_table.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # LOAD DATA SILENTLY
    # --------------------------------------------------------

    generate_report()


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

open_report = open_reports