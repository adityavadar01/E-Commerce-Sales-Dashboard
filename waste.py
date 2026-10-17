import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme, create_button


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
            f"{item[0]} - {item[1]}" for item in items
        ]

        cursor.close()
        db.close()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def calculate_waste(event=None):
    try:
        prepared = int(prepared_entry.get())
        sold = int(sold_entry.get())

        if prepared < 0 or sold < 0:
            raise ValueError

        if sold > prepared:
            waste_label.config(text="Invalid")
            return

        wasted = prepared - sold
        waste_label.config(text=str(wasted))

    except ValueError:
        waste_label.config(text="0")


def add_waste():
    selected_item = item_combo.get()
    prepared = prepared_entry.get().strip()
    sold = sold_entry.get().strip()
    reason = reason_entry.get().strip()

    if not selected_item:
        messagebox.showwarning(
            "Missing Information",
            "Please select a menu item."
        )
        return

    if not prepared or not sold:
        messagebox.showwarning(
            "Missing Information",
            "Please enter prepared and sold quantities."
        )
        return

    try:
        prepared = int(prepared)
        sold = int(sold)

        if prepared < 0 or sold < 0:
            raise ValueError

        if sold > prepared:
            messagebox.showwarning(
                "Invalid Quantity",
                "Sold quantity cannot be greater than prepared quantity."
            )
            return

        wasted = prepared - sold
        item_id = int(selected_item.split(" - ")[0])

    except ValueError:
        messagebox.showwarning(
            "Invalid Quantity",
            "Please enter valid non-negative whole numbers."
        )
        return

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO waste
            (
                item_id,
                waste_date,
                prepared_quantity,
                sold_quantity,
                wasted_quantity,
                reason
            )
            VALUES
            (%s, CURDATE(), %s, %s, %s, %s)
        """, (
            item_id,
            prepared,
            sold,
            wasted,
            reason
        ))

        db.commit()

        cursor.close()
        db.close()

        messagebox.showinfo(
            "Success",
            f"Waste record added successfully.\n\n"
            f"Wasted Quantity: {wasted}"
        )

        clear_fields()
        load_waste()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def delete_waste():
    selected = waste_table.focus()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a waste record to delete."
        )
        return

    values = waste_table.item(selected, "values")

    if not values:
        return

    waste_id = values[0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this waste record?"
    )

    if not confirm:
        return

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            DELETE FROM waste
            WHERE waste_id = %s
        """, (waste_id,))

        db.commit()

        cursor.close()
        db.close()

        messagebox.showinfo(
            "Deleted",
            "Waste record deleted successfully."
        )

        load_waste()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def load_waste():
    for row in waste_table.get_children():
        waste_table.delete(row)

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                w.waste_id,
                m.item_name,
                w.waste_date,
                w.prepared_quantity,
                w.sold_quantity,
                w.wasted_quantity,
                COALESCE(w.reason, '')
            FROM waste w
            JOIN menu_items m
                ON w.item_id = m.item_id
            ORDER BY w.waste_id DESC
        """)

        records = cursor.fetchall()

        total_wasted = 0

        for record in records:
            (
                waste_id,
                item_name,
                waste_date,
                prepared,
                sold,
                wasted,
                reason
            ) = record

            total_wasted += wasted

            waste_table.insert(
                "",
                tk.END,
                values=(
                    waste_id,
                    item_name,
                    waste_date,
                    prepared,
                    sold,
                    wasted,
                    reason
                )
            )

        cursor.close()
        db.close()

        count_label.config(
            text=f"Total Records: {len(records)}"
        )

        total_waste_label.config(
            text=f"Total Wasted: {total_wasted}"
        )

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def clear_fields():
    item_combo.set("")
    prepared_entry.delete(0, tk.END)
    sold_entry.delete(0, tk.END)
    reason_entry.delete(0, tk.END)
    waste_label.config(text="0")

    for item in waste_table.selection():
        waste_table.selection_remove(item)


def open_waste():
    global item_combo
    global prepared_entry
    global sold_entry
    global reason_entry
    global waste_label
    global waste_table
    global count_label
    global total_waste_label

    window = tk.Toplevel()
    window.title("Food Waste Management - Ganesh Nashta Center")
    window.geometry("1200x720")
    window.minsize(1050, 650)

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
        text="Food Waste Management",
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
        text="Track prepared, sold and wasted food",
        font=("Segoe UI", 10),
        bg="#1F4E78",
        fg="#DCE6F1"
    ).pack(
        anchor="w",
        padx=27
    )

    # ================= FORM =================

    form_card = tk.LabelFrame(
        window,
        text="  Record Food Waste  ",
        font=("Segoe UI", 11, "bold"),
        padx=15,
        pady=12
    )
    form_card.pack(
        fill="x",
        padx=20,
        pady=18
    )

    # Menu Item
    tk.Label(
        form_card,
        text="Menu Item",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=7
    )

    item_combo = ttk.Combobox(
        form_card,
        state="readonly",
        width=27
    )
    item_combo.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 10)
    )

    # Prepared
    tk.Label(
        form_card,
        text="Prepared Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=10,
        pady=7
    )

    prepared_entry = ttk.Entry(
        form_card,
        width=20
    )
    prepared_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 10)
    )
    prepared_entry.bind("<KeyRelease>", calculate_waste)

    # Sold
    tk.Label(
        form_card,
        text="Sold Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=2,
        sticky="w",
        padx=10,
        pady=7
    )

    sold_entry = ttk.Entry(
        form_card,
        width=20
    )
    sold_entry.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 10)
    )
    sold_entry.bind("<KeyRelease>", calculate_waste)

    # Wasted
    tk.Label(
        form_card,
        text="Wasted Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=3,
        sticky="w",
        padx=10,
        pady=7
    )

    waste_label = tk.Label(
        form_card,
        text="0",
        font=("Segoe UI", 18, "bold"),
        fg="#C00000"
    )
    waste_label.grid(
        row=1,
        column=3,
        sticky="w",
        padx=10,
        pady=(0, 10)
    )

    # Reason
    tk.Label(
        form_card,
        text="Reason",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=2,
        column=0,
        sticky="w",
        padx=10,
        pady=7
    )

    reason_entry = ttk.Entry(
        form_card,
        width=40
    )
    reason_entry.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="w",
        padx=10,
        pady=(0, 10)
    )

    # Buttons
    button_frame = tk.Frame(form_card)
    button_frame.grid(
        row=3,
        column=2,
        columnspan=2,
        pady=(0, 10)
    )

    create_button(
        button_frame,
        "Add Waste Record",
        add_waste,
        width=17,
        bg="#1F4E78"
    ).pack(
        side="left",
        padx=5
    )

    create_button(
        button_frame,
        "Delete",
        delete_waste,
        width=12,
        bg="#C00000"
    ).pack(
        side="left",
        padx=5
    )

    create_button(
        button_frame,
        "Clear",
        clear_fields,
        width=10,
        bg="#6B7280"
    ).pack(
        side="left",
        padx=5
    )

    # ================= SUMMARY =================

    summary_frame = tk.Frame(window)
    summary_frame.pack(
        fill="x",
        padx=25,
        pady=(0, 10)
    )

    count_label = tk.Label(
        summary_frame,
        text="Total Records: 0",
        font=("Segoe UI", 11, "bold"),
        fg="#1F2937"
    )
    count_label.pack(side="left")

    total_waste_label = tk.Label(
        summary_frame,
        text="Total Wasted: 0",
        font=("Segoe UI", 11, "bold"),
        fg="#C00000"
    )
    total_waste_label.pack(side="right")

    # ================= TABLE =================

    table_frame = tk.Frame(window)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 20)
    )

    columns = (
        "ID",
        "Menu Item",
        "Date",
        "Prepared",
        "Sold",
        "Wasted",
        "Reason"
    )

    waste_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    widths = {
        "ID": 60,
        "Menu Item": 190,
        "Date": 120,
        "Prepared": 110,
        "Sold": 100,
        "Wasted": 100,
        "Reason": 300
    }

    for column in columns:
        waste_table.heading(
            column,
            text=column
        )

        waste_table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=waste_table.yview
    )

    scrollbar_x = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=waste_table.xview
    )

    waste_table.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    waste_table.pack(
        side="top",
        fill="both",
        expand=True
    )

    scrollbar_y.pack(
        side="right",
        fill="y"
    )

    scrollbar_x.pack(
        side="bottom",
        fill="x"
    )

    # Load data
    load_menu_items()
    load_waste()