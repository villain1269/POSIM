# gui_windows.py
import tkinter as tk
from tkinter import ttk, messagebox
from functions import (
    get_products,
    add_inventory,
    update_inventory,
    get_inventory,
    add_product_with_recipe,
    get_recipe,
    deduct_inventory
)
from database import connect 

# -------------------- MAIN MENU --------------------
def open_main_menu(user):
    if not user:
        messagebox.showerror("Error", "Invalid user data")
        return

    role = user[3]  # role column
    menu_win = tk.Tk()
    menu_win.title("Bean & Brew POS")
    menu_win.geometry("450x400")

    tk.Label(menu_win, text="BEAN & BREW MAIN MENU",
             font=("Arial", 16, "bold"),
             fg="#6F4E37").pack(pady=20)

    if role in ['admin', 'cashier']:
        tk.Button(menu_win, text="New Sale", width=30,
                  command=lambda: open_pos(user[0])).pack(pady=5)

    if role == 'admin':
        tk.Button(menu_win, text="Menu Editor", width=30,
                  command=open_menu_editor).pack(pady=5)

    if role in ['admin', 'inventory_manager', 'cashier']:
        tk.Button(menu_win, text="Inventory Management", width=30,
                  command=open_inventory_editor).pack(pady=5)

    tk.Button(menu_win, text="Logout", fg="red", width=30,
              command=menu_win.destroy).pack(pady=20)

    menu_win.mainloop()


# -------------------- POS WINDOW --------------------
def open_pos(user_id):
    pos_win = tk.Toplevel()
    pos_win.title("POS - New Sale")
    pos_win.geometry("400x400")

    products = get_products()
    vars_qty = {}

    tk.Label(pos_win, text="Select Products:", font=("Arial",12,"bold")).pack(pady=10)

    for pid, name, price in products:
        frame = tk.Frame(pos_win)
        frame.pack(anchor='w')
        tk.Label(frame, text=f"{name} - ${price}").pack(side='left')
        qty_var = tk.IntVar(value=0)
        tk.Spinbox(frame, from_=0, to=100, width=5, textvariable=qty_var).pack(side='left', padx=5)
        vars_qty[pid] = qty_var

    def checkout():
        items_to_sell = []
        for pid, var in vars_qty.items():
            qty = var.get()
            if qty > 0:
                items_to_sell.append((pid, qty))
        if not items_to_sell:
            messagebox.showwarning("No items", "Please select at least one product")
            return
        try:
            # Deduct ingredients per quantity sold
            total = 0
            for pid, qty in items_to_sell:
                recipe = get_recipe(pid)
                for _ in range(qty):
                    deduct_inventory(pid)
                # calculate total
                product = next(p for p in products if p[0]==pid)
                total += product[2] * qty
            messagebox.showinfo("Sale Complete", f"Sale processed. Total: ${total:.2f}")
            pos_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(pos_win, text="Checkout", bg="#6F4E37", fg="white", command=checkout).pack(pady=10)
    tk.Button(pos_win, text="Back", command=pos_win.destroy).pack(pady=5)


# -------------------- MENU EDITOR --------------------
def open_menu_editor():
    menu_win = tk.Toplevel()
    menu_win.title("Menu Editor")
    menu_win.geometry("500x500")

    tk.Label(menu_win, text="Add New Product", font=("Arial",12,"bold")).pack(pady=5)
    tk.Label(menu_win, text="Name:").pack()
    ent_name = tk.Entry(menu_win)
    ent_name.pack(pady=2)
    tk.Label(menu_win, text="Price:").pack()
    ent_price = tk.Entry(menu_win)
    ent_price.pack(pady=2)

    tk.Label(menu_win, text="Select Ingredients:").pack(pady=5)
    inventory = get_inventory()
    ing_vars = []
    ing_minmax = []

    canvas = tk.Canvas(menu_win)
    frame = tk.Frame(canvas)
    scrollbar = tk.Scrollbar(menu_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(fill='both', expand=True)
    canvas.create_window((0,0), window=frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", on_frame_configure)

    for ing in inventory:
        ing_id = ing[0]
        var = tk.IntVar()
        tk.Checkbutton(frame, text=f"{ing[1]} ({ing[4]} {ing[3]})", variable=var).pack(anchor='w')
        min_entry = tk.Entry(frame, width=5)
        min_entry.pack(anchor='w')
        max_entry = tk.Entry(frame, width=5)
        max_entry.pack(anchor='w')
        ing_vars.append(var)
        ing_minmax.append((min_entry, max_entry, ing_id))

    def save_product():
        name = ent_name.get()
        try:
            price = float(ent_price.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Price must be a number")
            return
        ingredients = []
        for var, (min_e, max_e, ing_id) in zip(ing_vars, ing_minmax):
            if var.get() == 1:
                try:
                    min_qty = float(min_e.get())
                    max_qty = float(max_e.get())
                except ValueError:
                    messagebox.showerror("Invalid input", "Min/Max quantity must be numbers")
                    return
                ingredients.append({"ingredient_id": ing_id, "min_qty": min_qty, "max_qty": max_qty})
        add_product_with_recipe(name, price, ingredients)
        messagebox.showinfo("Added", f"{name} added successfully!")
        menu_win.destroy()
        open_menu_editor()

    tk.Button(menu_win, text="Save Product", command=save_product).pack(pady=10)
    tk.Button(menu_win, text="Back", command=menu_win.destroy).pack(pady=5)


# -------------------- INVENTORY EDITOR --------------------
def open_inventory_editor():
    inv_win = tk.Toplevel()
    inv_win.title("Inventory Management")
    inv_win.geometry("600x500")

    cols = ("ID", "Name", "Category", "Unit", "Quantity")
    tree = ttk.Treeview(inv_win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, padx=10, fill="both", expand=True)

    categories = ["Beans", "Powder", "Syrup", "Milk", "General"]
    units = ["g", "ml", "pcs"]

    def load_inventory():
        for row in tree.get_children():
            tree.delete(row)
        for item in get_inventory():
            tree.insert("", "end", values=item)
    load_inventory()

    frm = tk.Frame(inv_win)
    frm.pack(pady=10)
    tk.Label(frm, text="Name:").grid(row=0, column=0, padx=5)
    ent_name = tk.Entry(frm)
    ent_name.grid(row=0, column=1, padx=5)
    tk.Label(frm, text="Category:").grid(row=1, column=0, padx=5)
    cat_var = tk.StringVar(value=categories[0])
    tk.OptionMenu(frm, cat_var, *categories).grid(row=1, column=1, padx=5)
    tk.Label(frm, text="Unit:").grid(row=2, column=0, padx=5)
    unit_var = tk.StringVar(value=units[0])
    tk.OptionMenu(frm, unit_var, *units).grid(row=2, column=1, padx=5)
    tk.Label(frm, text="Quantity:").grid(row=3, column=0, padx=5)
    ent_qty = tk.Entry(frm)
    ent_qty.grid(row=3, column=1, padx=5)

    def add_or_update_item():
        name = ent_name.get()
        category = cat_var.get()
        unit = unit_var.get()
        try:
            qty = float(ent_qty.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a number")
            return
        selected = tree.focus()
        if selected:
            item_id = tree.item(selected)['values'][0]
            update_inventory(item_id, qty)
            messagebox.showinfo("Updated", f"{name} updated!")
        else:
            add_inventory(name, category, unit, qty)
            messagebox.showinfo("Added", f"{name} added!")
        load_inventory()
        clear_fields()

    def delete_item():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to delete.")
            return
        item_id = tree.item(selected)["values"][0]
        confirm = messagebox.askyesno("Delete?", "Delete selected item?")
        if confirm:
            db = connect()
            cursor = db.cursor()
            cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id,))
            db.commit()
            db.close()
            load_inventory()

    def clear_fields():
        ent_name.delete(0, tk.END)
        ent_qty.delete(0, tk.END)
        cat_var.set(categories[0])
        unit_var.set(units[0])
        tree.selection_remove(tree.focus())

    def on_item_select(event):
        selected = tree.focus()
        if not selected:
            return
        item = tree.item(selected)["values"]
        ent_name.delete(0, tk.END)
        ent_name.insert(0, item[1])
        cat_var.set(item[2])
        unit_var.set(item[3])
        ent_qty.delete(0, tk.END)
        ent_qty.insert(0, item[4])

    tree.bind("<<TreeviewSelect>>", on_item_select)

    btn_frame = tk.Frame(inv_win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add/Update Item", command=add_or_update_item).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Delete Item", command=delete_item).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Clear Fields", command=clear_fields).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Back", command=inv_win.destroy).grid(row=1, column=1, pady=10)