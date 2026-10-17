import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme


def get_alerts():
    alerts = []

    try:
        db = connect_database()
        cursor = db.cursor()

        # ================= LOW STOCK =================

        cursor.execute("""
            SELECT
                ingredient_name,
                quantity,
                unit,
                minimum_quantity
            FROM inventory
            WHERE quantity <= minimum_quantity
            ORDER BY quantity ASC
        """)

        low_stock_items = cursor.fetchall()

        for item in low_stock_items:
            ingredient, quantity, unit, minimum = item

            alerts.append({
                "type": "Low Stock",
                "title": f"Low stock: {ingredient}",
                "message": (
                    f"Only {quantity:g} {unit} available. "
                    f"Minimum required: {minimum:g} {unit}."
                )
            })

        # ================= HIGH FOOD WASTE =================

        cursor.execute("""
            SELECT
                m.item_name,
                SUM(w.wasted_quantity) AS total_waste
            FROM waste w
            JOIN menu_items m
                ON w.item_id = m.item_id
            GROUP BY m.item_id, m.item_name
            HAVING SUM(w.wasted_quantity) > 5
            ORDER BY total_waste DESC
        """)

        waste_items = cursor.fetchall()

        for item in waste_items:
            item_name, total_waste = item

            alerts.append({
                "type": "Food Waste",
                "title": f"High waste: {item_name}",
                "message": (
                    f"{total_waste} units have been wasted. "
                    f"Consider reducing preparation quantity."
                )
            })

        # ================= HIGH DEMAND ITEMS =================

        cursor.execute("""
            SELECT
                m.item_name,
                SUM(si.quantity) AS total_quantity
            FROM sale_items si
            JOIN menu_items m
                ON si.item_id = m.item_id
            GROUP BY m.item_id, m.item_name
            ORDER BY total_quantity DESC
            LIMIT 3
        """)

        top_items = cursor.fetchall()

        for item in top_items:
            item_name, quantity = item

            alerts.append({
                "type": "High Demand",
                "title": f"Popular item: {item_name}",
                "message": (
                    f"{quantity} units sold. "
                    f"Maintain sufficient stock for this item."
                )
            })

        cursor.close()
        db.close()

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )

    return alerts


def refresh_alerts():
    for widget in alerts_container.winfo_children():
        widget.destroy()

    alerts = get_alerts()

    alert_count_label.config(
        text=f"{len(alerts)} alert(s)"
    )

    if not alerts:
        empty_frame = tk.Frame(
            alerts_container,
            bg="white"
        )

        empty_frame.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            empty_frame,
            text="✓",
            font=("Segoe UI", 36, "bold"),
            bg="white",
            fg="#70AD47"
        ).pack(
            pady=(100, 5)
        )

        tk.Label(
            empty_frame,
            text="No alerts at the moment",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#1F2937"
        ).pack()

        tk.Label(
            empty_frame,
            text="Inventory, waste and sales indicators are within normal limits.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#5B6573"
        ).pack(
            pady=5
        )

        return

    for alert in alerts:
        create_alert_card(alert)


def create_alert_card(alert):
    alert_type = alert["type"]

    if alert_type == "Low Stock":
        accent = "#C00000"
        icon = "!"
    elif alert_type == "Food Waste":
        accent = "#E67E22"
        icon = "W"
    else:
        accent = "#2E75B6"
        icon = "↑"

    card = tk.Frame(
        alerts_container,
        bg="white",
        bd=1,
        relief="solid"
    )

    card.pack(
        fill="x",
        padx=15,
        pady=7
    )

    # Accent bar
    accent_bar = tk.Frame(
        card,
        bg=accent,
        width=6
    )

    accent_bar.pack(
        side="left",
        fill="y"
    )

    # Icon
    icon_frame = tk.Frame(
        card,
        bg="white",
        width=55
    )

    icon_frame.pack(
        side="left",
        fill="y",
        padx=(10, 0)
    )

    icon_frame.pack_propagate(False)

    tk.Label(
        icon_frame,
        text=icon,
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg=accent
    ).pack(
        expand=True
    )

    # Text
    text_frame = tk.Frame(
        card,
        bg="white"
    )

    text_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=10,
        pady=12
    )

    tk.Label(
        text_frame,
        text=alert["title"],
        font=("Segoe UI", 11, "bold"),
        bg="white",
        fg="#1F2937",
        anchor="w"
    ).pack(
        fill="x"
    )

    tk.Label(
        text_frame,
        text=alert["message"],
        font=("Segoe UI", 10),
        bg="white",
        fg="#5B6573",
        anchor="w",
        justify="left",
        wraplength=700
    ).pack(
        fill="x",
        pady=(3, 0)
    )

    # Type badge
    tk.Label(
        card,
        text=alert_type,
        font=("Segoe UI", 9, "bold"),
        bg=accent,
        fg="white",
        padx=10,
        pady=4
    ).pack(
        side="right",
        padx=15
    )


def open_alerts():
    global alerts_container
    global alert_count_label

    window = tk.Toplevel()
    window.title(
        "Alerts & Recommendations - Ganesh Nashta Center"
    )
    window.geometry("950x700")
    window.minsize(800, 600)

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
        text="Alerts & Recommendations",
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
        text="Business insights requiring attention",
        font=("Segoe UI", 10),
        bg="#1F4E78",
        fg="#DCE6F1"
    ).pack(
        anchor="w",
        padx=27
    )

    # ================= SUMMARY =================

    summary = tk.Frame(window)
    summary.pack(
        fill="x",
        padx=25,
        pady=15
    )

    tk.Label(
        summary,
        text="Current Alerts",
        font=("Segoe UI", 15, "bold"),
        fg="#1F2937"
    ).pack(
        side="left"
    )

    alert_count_label = tk.Label(
        summary,
        text="0 alert(s)",
        font=("Segoe UI", 10, "bold"),
        fg="#C00000"
    )

    alert_count_label.pack(
        side="right"
    )

    # ================= ALERT CONTAINER =================

    outer_frame = tk.Frame(window)
    outer_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 15)
    )

    canvas = tk.Canvas(
        outer_frame,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        outer_frame,
        orient="vertical",
        command=canvas.yview
    )

    alerts_container = tk.Frame(
        canvas,
        bg="#F4F6F8"
    )

    alerts_container.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=alerts_container,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # Keep inner frame width equal to canvas width
    def resize_alerts(event):
        canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_alerts
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
        text="Refresh Alerts",
        command=refresh_alerts,
        font=("Segoe UI", 10, "bold"),
        bg="#1F4E78",
        fg="white",
        activebackground="#2E75B6",
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=8,
        cursor="hand2"
    ).pack(
        side="right"
    )

    refresh_alerts()