import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_database
from theme import apply_theme, create_button


def load_inventory():
    for row in inventory_table.get_children():
        inventory_table.delete(row)

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                inventory_id,
                ingredient_name,
                quantity,
                unit,
                minimum_quantity
            FROM inventory
            ORDER BY ingredient_name
        """)

        records = cursor.fetchall()

        for record in records:
            inventory_id, ingredient, quantity, unit, minimum = record

            try:
                quantity = float(quantity)
                minimum = float(minimum)
            except (ValueError, TypeError):
                pass

            inventory_table.insert(
                "",
                tk.END,
                values=(
                    inventory_id,
                    ingredient,
                    quantity,
                    unit,
                    minimum
                )
            )

        cursor.close()
        db.close()

        update_inventory_count(len(records))
        update_low_stock_count(records)

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def update_inventory_count(count):
    count_label.config(text=f"Total Ingredients: {count}")


def update_low_stock_count(records):
    low_stock = 0

    for record in records:
        quantity = float(record[2])
        minimum = float(record[4])

        if quantity <= minimum:
            low_stock += 1

    low_stock_label.config(
        text=f"Low Stock Items: {low_stock}"
    )


def select_inventory(event=None):
    selected = inventory_table.focus()

    if not selected:
        return

    values = inventory_table.item(selected, "values")

    if not values:
        return

    ingredient_name_entry.delete(0, tk.END)
    ingredient_name_entry.insert(0, values[1])

    quantity_entry.delete(0, tk.END)
    quantity_entry.insert(0, values[2])

    unit_combo.set(values[3])

    minimum_quantity_entry.delete(0, tk.END)
    minimum_quantity_entry.insert(0, values[4])


def add_inventory():
    ingredient = ingredient_name_entry.get().strip()
    quantity = quantity_entry.get().strip()
    unit = unit_combo.get().strip()
    minimum = minimum_quantity_entry.get().strip()

    if not ingredient or not quantity or not unit or not minimum:
        messagebox.showwarning(
            "Missing Information",
            "Please fill all fields."
        )
        return

    try:
        quantity = float(quantity)
        minimum = float(minimum)

        if quantity < 0 or minimum < 0:
            messagebox.showwarning(
                "Invalid Value",
                "Quantity values cannot be negative."
            )
            return

    except ValueError:
        messagebox.showwarning(
            "Invalid Value",
            "Quantity and minimum quantity must be numeric."
        )
        return

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO inventory
            (ingredient_name, quantity, unit, minimum_quantity)
            VALUES (%s, %s, %s, %s)
        """, (
            ingredient,
            quantity,
            unit,
            minimum
        ))

        db.commit()

        cursor.close()
        db.close()

        messagebox.showinfo(
            "Success",
            "Ingredient added successfully."
        )

        clear_fields()
        load_inventory()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def update_inventory():
    selected = inventory_table.focus()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select an inventory item to update."
        )
        return

    values = inventory_table.item(selected, "values")

    if not values:
        return

    inventory_id = values[0]

    ingredient = ingredient_name_entry.get().strip()
    quantity = quantity_entry.get().strip()
    unit = unit_combo.get().strip()
    minimum = minimum_quantity_entry.get().strip()

    if not ingredient or not quantity or not unit or not minimum:
        messagebox.showwarning(
            "Missing Information",
            "Please fill all fields."
        )
        return

    try:
        quantity = float(quantity)
        minimum = float(minimum)

        if quantity < 0 or minimum < 0:
            messagebox.showwarning(
                "Invalid Value",
                "Quantity values cannot be negative."
            )
            return

    except ValueError:
        messagebox.showwarning(
            "Invalid Value",
            "Quantity and minimum quantity must be numeric."
        )
        return

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE inventory
            SET
                ingredient_name = %s,
                quantity = %s,
                unit = %s,
                minimum_quantity = %s
            WHERE inventory_id = %s
        """, (
            ingredient,
            quantity,
            unit,
            minimum,
            inventory_id
        ))

        db.commit()

        cursor.close()
        db.close()

        messagebox.showinfo(
            "Success",
            "Inventory item updated successfully."
        )

        clear_fields()
        load_inventory()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def delete_inventory():
    selected = inventory_table.focus()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select an inventory item to delete."
        )
        return

    values = inventory_table.item(selected, "values")

    if not values:
        return

    inventory_id = values[0]
    ingredient = values[1]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete '{ingredient}'?"
    )

    if not confirm:
        return

    try:
        db = connect_database()
        cursor = db.cursor()

        cursor.execute("""
            DELETE FROM inventory
            WHERE inventory_id = %s
        """, (inventory_id,))

        db.commit()

        cursor.close()
        db.close()

        messagebox.showinfo(
            "Deleted",
            "Inventory item deleted successfully."
        )

        clear_fields()
        load_inventory()

    except Exception as error:
        messagebox.showerror("Database Error", str(error))


def clear_fields():
    ingredient_name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    unit_combo.set("")
    minimum_quantity_entry.delete(0, tk.END)

    for item in inventory_table.selection():
        inventory_table.selection_remove(item)


def open_inventory():
    global ingredient_name_entry
    global quantity_entry
    global unit_combo
    global minimum_quantity_entry
    global inventory_table
    global count_label
    global low_stock_label

    window = tk.Toplevel()
    window.title("Inventory Management - Ganesh Nashta Center")
    window.geometry("1100x700")
    window.minsize(950, 620)

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
        text="Inventory Management",
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
        text="Manage ingredients and monitor stock levels",
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
        text="  Inventory Details  ",
        font=("Segoe UI", 11, "bold"),
        padx=15,
        pady=12
    )
    form_card.pack(
        fill="x",
        padx=20,
        pady=18
    )

    # Ingredient
    tk.Label(
        form_card,
        text="Ingredient Name",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=7
    )

    ingredient_name_entry = ttk.Entry(
        form_card,
        width=27
    )
    ingredient_name_entry.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 10)
    )

    # Quantity
    tk.Label(
        form_card,
        text="Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=10,
        pady=7
    )

    quantity_entry = ttk.Entry(
        form_card,
        width=20
    )
    quantity_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 10)
    )

    # Unit
    tk.Label(
        form_card,
        text="Unit",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=2,
        sticky="w",
        padx=10,
        pady=7
    )

    unit_combo = ttk.Combobox(
        form_card,
        values=[
            "kg",
            "gram",
            "litre",
            "ml",
            "pieces",
            "packets"
        ],
        state="readonly",
        width=18
    )
    unit_combo.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 10)
    )

    # Minimum Quantity
    tk.Label(
        form_card,
        text="Minimum Quantity",
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=0,
        column=3,
        sticky="w",
        padx=10,
        pady=7
    )

    minimum_quantity_entry = ttk.Entry(
        form_card,
        width=20
    )
    minimum_quantity_entry.grid(
        row=1,
        column=3,
        padx=10,
        pady=(0, 10)
    )

    # Buttons
    button_frame = tk.Frame(form_card)
    button_frame.grid(
        row=2,
        column=0,
        columnspan=4,
        pady=10
    )

    create_button(
        button_frame,
        "Add Ingredient",
        add_inventory,
        width=16,
        bg="#1F4E78"
    ).pack(side="left", padx=5)

    create_button(
        button_frame,
        "Update",
        update_inventory,
        width=12,
        bg="#2E75B6"
    ).pack(side="left", padx=5)

    create_button(
        button_frame,
        "Delete",
        delete_inventory,
        width=12,
        bg="#C00000"
    ).pack(side="left", padx=5)

    create_button(
        button_frame,
        "Clear",
        clear_fields,
        width=10,
        bg="#6B7280"
    ).pack(side="left", padx=5)

    # ================= SUMMARY =================

    summary_frame = tk.Frame(window)
    summary_frame.pack(
        fill="x",
        padx=25,
        pady=(0, 10)
    )

    count_label = tk.Label(
        summary_frame,
        text="Total Ingredients: 0",
        font=("Segoe UI", 11, "bold"),
        fg="#1F2937"
    )
    count_label.pack(side="left")

    low_stock_label = tk.Label(
        summary_frame,
        text="Low Stock Items: 0",
        font=("Segoe UI", 11, "bold"),
        fg="#C00000"
    )
    low_stock_label.pack(side="right")

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
        "Ingredient",
        "Quantity",
        "Unit",
        "Minimum Quantity"
    )

    inventory_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    widths = {
        "ID": 70,
        "Ingredient": 300,
        "Quantity": 150,
        "Unit": 150,
        "Minimum Quantity": 200
    }

    for column in columns:
        inventory_table.heading(
            column,
            text=column
        )

        inventory_table.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=inventory_table.yview
    )

    inventory_table.configure(
        yscrollcommand=scrollbar.set
    )

    inventory_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    inventory_table.bind(
        "<<TreeviewSelect>>",
        select_inventory
    )

    load_inventory()