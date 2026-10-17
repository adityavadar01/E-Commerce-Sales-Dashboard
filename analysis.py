import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_summary_data():
    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM sales
        """)
        total_sales = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(profit), 0)
            FROM sale_items
        """)
        total_profit = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM sales
        """)
        total_orders = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM sale_items
        """)
        total_items = cursor.fetchone()[0]

        cursor.close()
        db.close()

        return total_sales, total_profit, total_orders, total_items

    except Exception as error:
        messagebox.showerror("Database Error", str(error))
        return 0, 0, 0, 0


def load_best_selling_items():
    for row in best_table.get_children():
        best_table.delete(row)

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                m.item_name,
                SUM(si.quantity) AS total_quantity,
                SUM(si.quantity * si.price) AS revenue,
                SUM(si.profit) AS profit
            FROM sale_items si
            JOIN menu_items m
                ON si.item_id = m.item_id
            GROUP BY m.item_id, m.item_name
            ORDER BY total_quantity DESC
            LIMIT 10
        """)

        records = cursor.fetchall()

        for record in records:
            item_name, quantity, revenue, profit = record

            best_table.insert(
                "",
                tk.END,
                values=(
                    item_name,
                    quantity,
                    f"₹{revenue:.2f}",
                    f"₹{profit:.2f}"
                )
            )

        cursor.close()
        db.close()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def load_payment_analysis():
    for row in payment_table.get_children():
        payment_table.delete(row)

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                payment_mode,
                COUNT(*) AS orders,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM sales
            GROUP BY payment_mode
            ORDER BY revenue DESC
        """)

        records = cursor.fetchall()

        for record in records:
            payment, orders, revenue = record

            payment_table.insert(
                "",
                tk.END,
                values=(
                    payment,
                    orders,
                    f"₹{revenue:.2f}"
                )
            )

        cursor.close()
        db.close()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def load_daily_sales():
    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                sale_date,
                SUM(total_amount)
            FROM sales
            GROUP BY sale_date
            ORDER BY sale_date
        """)

        records = cursor.fetchall()

        cursor.close()
        db.close()

        dates = [str(record[0]) for record in records]
        sales = [float(record[1]) for record in records]

        return dates, sales

    except Exception as error:
        messagebox.showerror("Database Error", str(error))
        return [], []


def load_sales_chart():
    for widget in chart_frame.winfo_children():
        widget.destroy()

    dates, sales = load_daily_sales()

    figure = plt.Figure(
        figsize=(8, 4.2),
        dpi=100
    )

    ax = figure.add_subplot(111)

    if dates:
        ax.plot(
            dates,
            sales,
            marker="o",
            linewidth=2
        )

        ax.set_title(
            "Daily Sales Trend",
            fontsize=13,
            fontweight="bold"
        )

        ax.set_xlabel("Date")
        ax.set_ylabel("Sales (₹)")

        ax.grid(
            True,
            alpha=0.25
        )

        ax.tick_params(
            axis="x",
            rotation=35
        )

        figure.tight_layout()

    else:
        ax.text(
            0.5,
            0.5,
            "No sales data available",
            ha="center",
            va="center",
            fontsize=13
        )

        ax.set_axis_off()

    canvas = FigureCanvasTkAgg(
        figure,
        master=chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )


def refresh_analysis():
    total_sales, total_profit, total_orders, total_items = get_summary_data()

    sales_value.config(
        text=f"₹{total_sales:,.2f}"
    )

    profit_value.config(
        text=f"₹{total_profit:,.2f}"
    )

    orders_value.config(
        text=str(total_orders)
    )

    items_value.config(
        text=str(total_items)
    )

    load_best_selling_items()
    load_payment_analysis()
    load_sales_chart()


def open_analysis():
    global sales_value
    global profit_value
    global orders_value
    global items_value
    global best_table
    global payment_table
    global chart_frame

    window = tk.Toplevel()
    window.title("Sales Analysis - Ganesh Nashta Center")
    window.geometry("1250x800")
    window.minsize(1100, 700)

    apply_theme()

    # ================= HEADER =================

    header = tk.Frame(
        window,
        bg="#1F4E78",
        height=75
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)

    tk.Label(
        header,
        text="Sales Analysis",
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
        text="Analyze revenue, profit, orders and customer payment trends",
        font=("Segoe UI", 10),
        bg="#1F4E78",
        fg="#DCE6F1"
    ).pack(
        anchor="w",
        padx=27
    )

    # ================= KPI SECTION =================

    kpi_frame = tk.Frame(window)
    kpi_frame.pack(
        fill="x",
        padx=20,
        pady=18
    )

    # Total Sales
    sales_card = tk.Frame(
        kpi_frame,
        bg="white",
        bd=1,
        relief="solid"
    )

    sales_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    tk.Label(
        sales_card,
        text="TOTAL SALES",
        font=("Segoe UI", 10, "bold"),
        bg="white",
        fg="#5B6573"
    ).pack(
        pady=(14, 3)
    )

    sales_value = tk.Label(
        sales_card,
        text="₹0.00",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#1F4E78"
    )

    sales_value.pack(
        pady=(0, 14)
    )

    # Total Profit
    profit_card = tk.Frame(
        kpi_frame,
        bg="white",
        bd=1,
        relief="solid"
    )

    profit_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    tk.Label(
        profit_card,
        text="TOTAL PROFIT",
        font=("Segoe UI", 10, "bold"),
        bg="white",
        fg="#5B6573"
    ).pack(
        pady=(14, 3)
    )

    profit_value = tk.Label(
        profit_card,
        text="₹0.00",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#70AD47"
    )

    profit_value.pack(
        pady=(0, 14)
    )

    # Orders
    orders_card = tk.Frame(
        kpi_frame,
        bg="white",
        bd=1,
        relief="solid"
    )

    orders_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    tk.Label(
        orders_card,
        text="TOTAL ORDERS",
        font=("Segoe UI", 10, "bold"),
        bg="white",
        fg="#5B6573"
    ).pack(
        pady=(14, 3)
    )

    orders_value = tk.Label(
        orders_card,
        text="0",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#2E75B6"
    )

    orders_value.pack(
        pady=(0, 14)
    )

    # Items Sold
    items_card = tk.Frame(
        kpi_frame,
        bg="white",
        bd=1,
        relief="solid"
    )

    items_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    tk.Label(
        items_card,
        text="ITEMS SOLD",
        font=("Segoe UI", 10, "bold"),
        bg="white",
        fg="#5B6573"
    ).pack(
        pady=(14, 3)
    )

    items_value = tk.Label(
        items_card,
        text="0",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#1F4E78"
    )

    items_value.pack(
        pady=(0, 14)
    )

    # ================= MAIN CONTENT =================

    content_frame = tk.Frame(window)
    content_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 10)
    )

    # Left side
    left_frame = tk.Frame(content_frame)
    left_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    # Chart
    chart_card = tk.LabelFrame(
        left_frame,
        text="  Sales Trend  ",
        font=("Segoe UI", 11, "bold")
    )

    chart_card.pack(
        fill="both",
        expand=True
    )

    chart_frame = tk.Frame(chart_card)
    chart_frame.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    # Right side
    right_frame = tk.Frame(content_frame)
    right_frame.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(8, 0)
    )

    # ================= BEST SELLING =================

    best_card = tk.LabelFrame(
        right_frame,
        text="  Best Selling Items  ",
        font=("Segoe UI", 11, "bold")
    )

    best_card.pack(
        fill="both",
        expand=True,
        pady=(0, 8)
    )

    best_table = ttk.Treeview(
        best_card,
        columns=(
            "Item",
            "Quantity",
            "Revenue",
            "Profit"
        ),
        show="headings",
        height=7
    )

    best_widths = {
        "Item": 150,
        "Quantity": 80,
        "Revenue": 110,
        "Profit": 110
    }

    for column in best_widths:
        best_table.heading(
            column,
            text=column
        )

        best_table.column(
            column,
            width=best_widths[column],
            anchor="center"
        )

    best_table.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    # ================= PAYMENT ANALYSIS =================

    payment_card = tk.LabelFrame(
        right_frame,
        text="  Payment Mode Analysis  ",
        font=("Segoe UI", 11, "bold")
    )

    payment_card.pack(
        fill="both",
        expand=True,
        pady=(8, 0)
    )

    payment_table = ttk.Treeview(
        payment_card,
        columns=(
            "Payment",
            "Orders",
            "Revenue"
        ),
        show="headings",
        height=5
    )

    payment_widths = {
        "Payment": 150,
        "Orders": 90,
        "Revenue": 130
    }

    for column in payment_widths:
        payment_table.heading(
            column,
            text=column
        )

        payment_table.column(
            column,
            width=payment_widths[column],
            anchor="center"
        )

    payment_table.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    # ================= FOOTER =================

    footer = tk.Frame(window)
    footer.pack(
        fill="x",
        padx=25,
        pady=(0, 15)
    )

    tk.Button(
        footer,
        text="Refresh Analysis",
        command=refresh_analysis,
        font=("Segoe UI", 10, "bold"),
        bg="#1F4E78",
        fg="white",
        activebackground="#2E75B6",
        activeforeground="white",
        relief="flat",
        padx=15,
        pady=7,
        cursor="hand2"
    ).pack(
        side="right"
    )

    refresh_analysis()