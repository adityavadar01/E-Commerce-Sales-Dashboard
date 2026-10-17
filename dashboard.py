import tkinter as tk
from tkinter import messagebox

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import connect_database

from menu import open_menu
from customers import open_customers
from sales import open_sales
from inventory import open_inventory
from waste import open_waste
from analysis import open_analysis
from forecast import open_forecast
from alerts import open_alerts
from reports import open_reports

from theme import (
    apply_theme,
    BG_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    TEXT_COLOR,
    SECONDARY_TEXT,
    BORDER_COLOR,
    TITLE_FONT,
    SUBTITLE_FONT,
    HEADING_FONT,
    create_button,
    create_kpi_card
)


# =========================================================
# DASHBOARD DATA
# =========================================================

def load_dashboard_data():

    db = None
    cursor = None

    try:

        db = connect_database()
        cursor = db.cursor()

        # =================================================
        # TOTAL SALES
        # =================================================

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM sales
        """)

        total_sales = cursor.fetchone()[0]

        # =================================================
        # TOTAL PROFIT
        # =================================================

        cursor.execute("""
            SELECT COALESCE(SUM(profit), 0)
            FROM sale_items
        """)

        total_profit = cursor.fetchone()[0]

        # =================================================
        # TOTAL ORDERS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM sales
        """)

        total_orders = cursor.fetchone()[0]

        # =================================================
        # TOTAL ITEMS SOLD
        # =================================================

        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM sale_items
        """)

        total_items = cursor.fetchone()[0]

        # =================================================
        # LOW STOCK ITEMS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM inventory
            WHERE quantity <= minimum_quantity
        """)

        low_stock = cursor.fetchone()[0]

        # =================================================
        # UPDATE KPI CARDS
        # =================================================

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
            text=str(total_items)
        )

        stock_value_label.config(
            text=str(low_stock)
        )

        # =================================================
        # SALES DATA
        #
        # Get the latest 7 dates that actually have sales.
        # This works better for demo/historical data.
        # =================================================

        cursor.execute("""
            SELECT
                sale_date,
                SUM(total_amount) AS daily_sales
            FROM sales
            GROUP BY sale_date
            ORDER BY sale_date DESC
            LIMIT 7
        """)

        records = cursor.fetchall()

        # Reverse so chart goes oldest -> newest
        records = list(reversed(records))

        # =================================================
        # CLOSE DATABASE
        # =================================================

        cursor.close()
        cursor = None

        db.close()
        db = None

        # =================================================
        # CLEAR OLD CHART
        # =================================================

        for widget in chart_frame.winfo_children():
            widget.destroy()

        # =================================================
        # NO SALES DATA
        # =================================================

        if not records:

            no_data_frame = tk.Frame(
                chart_frame,
                bg=CARD_COLOR
            )

            no_data_frame.pack(
                fill="both",
                expand=True
            )

            no_data_label = tk.Label(
                no_data_frame,
                text="No sales data available",
                font=(
                    "Segoe UI",
                    14,
                    "bold"
                ),
                bg=CARD_COLOR,
                fg=SECONDARY_TEXT
            )

            no_data_label.pack(
                pady=60
            )

            return

        # =================================================
        # CREATE DATAFRAME
        # =================================================

        df = pd.DataFrame(
            records,
            columns=[
                "date",
                "sales"
            ]
        )

        df["date"] = pd.to_datetime(
            df["date"]
        )

        df["sales"] = pd.to_numeric(
            df["sales"]
        )

        # =================================================
        # CREATE MATPLOTLIB FIGURE
        # =================================================

        figure = plt.Figure(
            figsize=(10, 2.5),
            dpi=100
        )

        figure.patch.set_facecolor(
            "#FFFFFF"
        )

        axis = figure.add_subplot(111)

        axis.set_facecolor(
            "#FFFFFF"
        )

        # =================================================
        # PLOT SALES
        # =================================================

        axis.plot(
            df["date"],
            df["sales"],
            marker="o",
            linewidth=2.5,
            markersize=6
        )

        # =================================================
        # CHART TITLE
        # =================================================

        axis.set_title(
            "Sales Performance - Latest 7 Sales Days",
            fontsize=12,
            fontweight="bold",
            pad=10
        )

        axis.set_xlabel(
            "Date",
            fontsize=9
        )

        axis.set_ylabel(
            "Sales (₹)",
            fontsize=9
        )

        axis.grid(
            True,
            alpha=0.25
        )

        # =================================================
        # FORMAT X AXIS
        # =================================================

        axis.tick_params(
            axis="x",
            labelrotation=30,
            labelsize=8
        )

        axis.tick_params(
            axis="y",
            labelsize=8
        )

        # =================================================
        # ADD VALUES ABOVE POINTS
        # =================================================

        for date, sales in zip(
            df["date"],
            df["sales"]
        ):

            axis.annotate(
                f"₹{sales:,.0f}",
                (
                    date,
                    sales
                ),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=8
            )

        figure.tight_layout()

        # =================================================
        # PUT CHART INTO TKINTER
        # =================================================

        canvas = FigureCanvasTkAgg(
            figure,
            master=chart_frame
        )

        canvas.draw()

        canvas_widget = canvas.get_tk_widget()

        canvas_widget.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

    except Exception as error:

        # Clear chart area
        for widget in chart_frame.winfo_children():
            widget.destroy()

        error_label = tk.Label(
            chart_frame,
            text=f"Unable to load dashboard data\n\n{error}",
            font=(
                "Segoe UI",
                10
            ),
            bg=CARD_COLOR,
            fg="#C62828",
            justify="center"
        )

        error_label.pack(
            pady=45
        )

        messagebox.showerror(
            "Dashboard Error",
            f"Unable to load dashboard data.\n\n{error}"
        )

    finally:

        try:

            if cursor:
                cursor.close()

        except:
            pass

        try:

            if db:
                db.close()

        except:
            pass


# =========================================================
# OPEN DASHBOARD
# =========================================================

def open_dashboard():

    global sales_value_label
    global profit_value_label
    global orders_value_label
    global items_value_label
    global stock_value_label
    global chart_frame

    # =====================================================
    # MAIN WINDOW
    # =====================================================

    dashboard = tk.Tk()

    apply_theme()

    dashboard.title(
        "Ganesh Nashta Center - Dashboard"
    )

    # Smaller height so everything fits on screen
    dashboard.geometry(
        "1200x780"
    )

    dashboard.minsize(
        1100,
        720
    )

    dashboard.configure(
        bg=BG_COLOR
    )

    # =====================================================
    # HEADER
    # =====================================================

    header = tk.Frame(
        dashboard,
        bg=PRIMARY_COLOR,
        height=95
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(
        False
    )

    title = tk.Label(
        header,
        text="Ganesh Nashta Center",
        font=TITLE_FONT,
        bg=PRIMARY_COLOR,
        fg="white"
    )

    title.pack(
        pady=(14, 0)
    )

    subtitle = tk.Label(
        header,
        text="Sales & Business Intelligence Dashboard",
        font=SUBTITLE_FONT,
        bg=PRIMARY_COLOR,
        fg="#DCEAF7"
    )

    subtitle.pack(
        pady=(0, 8)
    )

    # =====================================================
    # KPI SECTION
    # =====================================================

    kpi_frame = tk.Frame(
        dashboard,
        bg=BG_COLOR
    )

    kpi_frame.pack(
        pady=10
    )

    # =====================================================
    # TOTAL SALES
    # =====================================================

    sales_card, sales_value_label = create_kpi_card(
        kpi_frame,
        "TOTAL SALES",
        "₹0.00",
        width=185,
        height=85
    )

    sales_card.grid(
        row=0,
        column=0,
        padx=6
    )

    # =====================================================
    # TOTAL PROFIT
    # =====================================================

    profit_card, profit_value_label = create_kpi_card(
        kpi_frame,
        "TOTAL PROFIT",
        "₹0.00",
        width=185,
        height=85
    )

    profit_card.grid(
        row=0,
        column=1,
        padx=6
    )

    # =====================================================
    # TOTAL ORDERS
    # =====================================================

    orders_card, orders_value_label = create_kpi_card(
        kpi_frame,
        "TOTAL ORDERS",
        "0",
        width=185,
        height=85
    )

    orders_card.grid(
        row=0,
        column=2,
        padx=6
    )

    # =====================================================
    # ITEMS SOLD
    # =====================================================

    items_card, items_value_label = create_kpi_card(
        kpi_frame,
        "ITEMS SOLD",
        "0",
        width=185,
        height=85
    )

    items_card.grid(
        row=0,
        column=3,
        padx=6
    )

    # =====================================================
    # LOW STOCK
    # =====================================================

    stock_card, stock_value_label = create_kpi_card(
        kpi_frame,
        "LOW STOCK ITEMS",
        "0",
        width=185,
        height=85
    )

    stock_card.grid(
        row=0,
        column=4,
        padx=6
    )

    # =====================================================
    # CHART TITLE
    # =====================================================

    chart_title = tk.Label(
        dashboard,
        text="Sales Performance",
        font=HEADING_FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )

    chart_title.pack(
        pady=(2, 3)
    )

    # =====================================================
    # CHART FRAME
    # =====================================================

    chart_frame = tk.Frame(
        dashboard,
        height=245,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1
    )

    chart_frame.pack(
        fill="x",
        padx=35,
        pady=3
    )

    chart_frame.pack_propagate(
        False
    )

    # =====================================================
    # MODULE BUTTONS
    # =====================================================

    button_frame = tk.Frame(
        dashboard,
        bg=BG_COLOR
    )

    button_frame.pack(
        pady=7
    )

    # =====================================================
    # ROW 1
    # =====================================================

    menu_button = create_button(
        button_frame,
        "Menu Items",
        open_menu,
        width=19
    )

    menu_button.grid(
        row=0,
        column=0,
        padx=4,
        pady=3
    )

    customer_button = create_button(
        button_frame,
        "Customers",
        open_customers,
        width=19
    )

    customer_button.grid(
        row=0,
        column=1,
        padx=4,
        pady=3
    )

    sales_button = create_button(
        button_frame,
        "Sales",
        open_sales,
        width=19
    )

    sales_button.grid(
        row=0,
        column=2,
        padx=4,
        pady=3
    )

    inventory_button = create_button(
        button_frame,
        "Inventory",
        open_inventory,
        width=19
    )

    inventory_button.grid(
        row=0,
        column=3,
        padx=4,
        pady=3
    )

    # =====================================================
    # ROW 2
    # =====================================================

    waste_button = create_button(
        button_frame,
        "Food Waste",
        open_waste,
        width=19
    )

    waste_button.grid(
        row=1,
        column=0,
        padx=4,
        pady=3
    )

    analysis_button = create_button(
        button_frame,
        "Sales Analysis",
        open_analysis,
        width=19
    )

    analysis_button.grid(
        row=1,
        column=1,
        padx=4,
        pady=3
    )

    forecast_button = create_button(
        button_frame,
        "Demand Forecast",
        open_forecast,
        width=19
    )

    forecast_button.grid(
        row=1,
        column=2,
        padx=4,
        pady=3
    )

    alerts_button = create_button(
        button_frame,
        "Alerts & Recommendations",
        open_alerts,
        width=19,
        bg="#E67E22"
    )

    alerts_button.grid(
        row=1,
        column=3,
        padx=4,
        pady=3
    )

    # =====================================================
    # ROW 3 - REPORTS
    # =====================================================

    reports_button = create_button(
        button_frame,
        "Reports",
        open_reports,
        width=19,
        bg=ACCENT_COLOR
    )

    reports_button.grid(
        row=2,
        column=0,
        columnspan=4,
        pady=4
    )

    # =====================================================
    # CONTROL BUTTONS
    # =====================================================

    control_frame = tk.Frame(
        dashboard,
        bg=BG_COLOR
    )

    control_frame.pack(
        pady=2
    )

    refresh_button = create_button(
        control_frame,
        "Refresh Dashboard",
        load_dashboard_data,
        width=20,
        bg=SECONDARY_COLOR
    )

    refresh_button.grid(
        row=0,
        column=0,
        padx=5
    )

    logout_button = create_button(
        control_frame,
        "Logout",
        dashboard.destroy,
        width=15,
        bg="#555555"
    )

    logout_button.grid(
        row=0,
        column=1,
        padx=5
    )

    # =====================================================
    # FOOTER
    # =====================================================

    footer = tk.Label(
        dashboard,
        text="Ganesh Nashta Center • Business Intelligence System",
        font=(
            "Segoe UI",
            8
        ),
        bg=BG_COLOR,
        fg=SECONDARY_TEXT
    )

    footer.pack(
        pady=3
    )

    # =====================================================
    # LOAD DATA
    # =====================================================

    load_dashboard_data()

    # =====================================================
    # START DASHBOARD
    # =====================================================

    dashboard.mainloop()