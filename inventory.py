import tkinter as tk
from tkinter import ttk
from database import get_inventory

class InventoryWindow:

    def __init__(self,root):

        self.win = tk.Toplevel(root)

        self.win.title("Inventory")

        cols = ("ID","Name","Quantity","Unit")

        tree = ttk.Treeview(self.win,
                            columns=cols,
                            show="headings")

        for c in cols:
            tree.heading(c,text=c)

        items = get_inventory()

        for i in items:
            tree.insert("",tk.END,values=i)

        tree.pack(fill="both",expand=True)