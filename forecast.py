import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta


def load_menu_items():
    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT item_id, item_name
            FROM menu_items
            ORDER BY item_name
        """)

        items = cursor.fetchall()

        item_combo["values"] = [
            f"{item[0]} - {item[1]}"
            for item in items
        ]

        cursor.close()
        db.close()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def get_sales_data(item_id):
    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                sale_date,
                SUM(quantity) AS total_quantity
            FROM sale_items si
            JOIN sales s
                ON si.sale_id = s.sale_id
            WHERE si.item_id = %s
            GROUP BY sale_date
            ORDER BY sale_date
        """, (item_id,))

        records = cursor.fetchall()

        cursor.close()
        db.close()

        return records

    except Exception as error:
        messagebox.showerror("Database Error", str(error))
        return []


def generate_forecast():
    selected = item_combo.get()

    if not selected:
        messagebox.showwarning(
            "Missing Information",
            "Please select a menu item."
        )
        return

    item_id = int(selected.split(" - ")[0])
    item_name = selected.split(" - ", 1)[1]

    records = get_sales_data(item_id)

    if len(records) < 3:
        messagebox.showwarning(
            "Insufficient Data",
            f"At least 3 days of sales data are required "
            f"to forecast {item_name}."
        )
        return

    try:
        # -----------------------------
        # Prepare training data
        # -----------------------------

        dates = [record[0] for record in records]
        quantities = [float(record[1]) for record in records]

        X = [[i] for i in range(len(quantities))]
        y = quantities

        # -----------------------------
        # Linear Regression
        # -----------------------------

        model = LinearRegression()
        model.fit(X, y)

        future_days = 7

        future_X = [
            [len(quantities) + i]
            for i in range(future_days)
        ]

        predictions = model.predict(future_X)

        # Demand cannot realistically be negative
        predictions = [
            max(0, round(float(prediction), 2))
            for prediction in predictions
        ]

        # -----------------------------
        # Clear previous results
        # -----------------------------

        for row in forecast_table.get_children():
            forecast_table.delete(row)

        # -----------------------------
        # Display forecast
        # -----------------------------

        last_date = dates[-1]

        for i in range(future_days):
            forecast_date = last_date + timedelta(days=i + 1)

            forecast_table.insert(
                "",
                tk.END,
                values=(
                    forecast_date,
                    item_name,
                    predictions[i],
                    "Linear Regression"
                )
            )

        # -----------------------------
        # Summary
        # -----------------------------

        average_forecast = sum(predictions) / len(predictions)

        summary_label.config(
            text=(
                f"7-Day Forecast: {sum(predictions):.0f} units  |  "
                f"Average Daily Demand: {average_forecast:.2f} units"
            )
        )

        method_label.config(
            text=(
                f"Forecast Method: Linear Regression  |  "
                f"Historical Days Used: {len(records)}"
            )
        )

        # -----------------------------
        # Update chart
        # -----------------------------

        create_forecast_chart(
            dates,
            quantities,
            last_date,
            predictions
        )

    except Exception as error:
        messagebox.showerror(
            "Forecast Error",
            str(error)
        )


def create_forecast_chart(
    historical_dates,
    historical_values,
    last_date,
    predictions
):
    for widget in chart_frame.winfo_children():
        widget.destroy()

    figure = plt.Figure(
        figsize=(8, 4.2),
        dpi=100
    )

    ax = figure.add_subplot(111)

    # Historical dates
    history_x = list(range(len(historical_values)))

    # Future dates
    future_x = [
        len(historical_values) + i
        for i in range(len(predictions))
    ]

    ax.plot(
        history_x,
        historical_values,
        marker="o",
        linewidth=2,
        label="Historical Demand"
    )

    ax.plot(
        future_x,
        predictions,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Forecast Demand"
    )

    # X-axis labels
    all_dates = historical_dates + [
        last_date + timedelta(days=i + 1)
        for i in range(len(predictions))
    ]

    display_labels = [
        str(date)
        for date in all_dates
    ]

    ax.set_xticks(
        range(len(display_labels))
    )

    ax.set_xticklabels(
        display_labels,
        rotation=40,
        ha="right"
    )

    ax.set_title(
        "Demand Forecast",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Quantity")

    ax.grid(
        True,
        alpha=0.25
    )

    ax.legend()

    figure.tight_layout()

    canvas = FigureCanvasTkAgg(
        figure,
        master=chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )


def clear_forecast():
    item_combo.set("")

    for row in forecast_table.get_children():
        forecast_table.delete(row)

    summary_label.config(
        text="7-Day Forecast: --"
    )

    method_label.config(
        text="Forecast Method: --"
    )

    for widget in chart_frame.winfo_children():
        widget.destroy()


def open_forecast():
    global item_combo
    global forecast_table
    global summary_label
    global method_label
    global chart_frame

    window = tk.Toplevel()
    window.title(
        "Demand Forecast - Ganesh Nashta Center"
    )
    window.geometry("1250x800")
    window.minsize(1100, 700)

    apply_theme()

    # ================= HEADER =================

    header = tk.Frame(
        window,
        bg="#1F4E78",
        height=75
    )

    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Demand Forecast",
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
        text="Predict future demand using historical sales data",
        font=("Segoe UI", 10),
        bg="#1F4E78",
        fg="#DCE6F1"
    ).pack(
        anchor="w",
        padx=27
    )

    # ================= CONTROL CARD =================

    control_card = tk.LabelFrame(
        window,
        text="  Forecast Settings  ",
        font=("Segoe UI", 11, "bold"),
        padx=15,
        pady=15
    )

    control_card.pack(
        fill="x",
        padx=20,
        pady=18
    )

    tk.Label(
        control_card,
        text="Select Menu Item",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=5
    )

    item_combo = ttk.Combobox(
        control_card,
        state="readonly",
        width=32
    )

    item_combo.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 5)
    )

    generate_button = tk.Button(
        control_card,
        text="Generate Forecast",
        command=generate_forecast,
        font=("Segoe UI", 10, "bold"),
        bg="#1F4E78",
        fg="white",
        activebackground="#2E75B6",
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=8,
        cursor="hand2"
    )

    generate_button.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 5)
    )

    clear_button = tk.Button(
        control_card,
        text="Clear",
        command=clear_forecast,
        font=("Segoe UI", 10, "bold"),
        bg="#6B7280",
        fg="white",
        activebackground="#4B5563",
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=8,
        cursor="hand2"
    )

    clear_button.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 5)
    )

    # ================= SUMMARY =================

    summary_frame = tk.Frame(window)
    summary_frame.pack(
        fill="x",
        padx=25,
        pady=(0, 10)
    )

    summary_label = tk.Label(
        summary_frame,
        text="7-Day Forecast: --",
        font=("Segoe UI", 12, "bold"),
        fg="#1F4E78"
    )

    summary_label.pack(
        side="left"
    )

    method_label = tk.Label(
        summary_frame,
        text="Forecast Method: --",
        font=("Segoe UI", 10),
        fg="#5B6573"
    )

    method_label.pack(
        side="right"
    )

    # ================= MAIN CONTENT =================

    content_frame = tk.Frame(window)
    content_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 15)
    )

    # Chart
    chart_card = tk.LabelFrame(
        content_frame,
        text="  Demand Trend & Forecast  ",
        font=("Segoe UI", 11, "bold")
    )

    chart_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    chart_frame = tk.Frame(chart_card)
    chart_frame.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    # Forecast Table
    table_card = tk.LabelFrame(
        content_frame,
        text="  7-Day Forecast  ",
        font=("Segoe UI", 11, "bold")
    )

    table_card.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(8, 0)
    )

    table_container = tk.Frame(table_card)
    table_container.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    columns = (
        "Date",
        "Item",
        "Predicted Demand",
        "Method"
    )

    forecast_table = ttk.Treeview(
        table_container,
        columns=columns,
        show="headings"
    )

    widths = {
        "Date": 100,
        "Item": 150,
        "Predicted Demand": 150,
        "Method": 150
    }

    for column in columns:
        forecast_table.heading(
            column,
            text=column
        )

        forecast_table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        table_container,
        orient="vertical",
        command=forecast_table.yview
    )

    forecast_table.configure(
        yscrollcommand=scrollbar.set
    )

    forecast_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    load_menu_items()