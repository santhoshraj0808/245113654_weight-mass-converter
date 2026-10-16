"""Main Tkinter window for the Weight / Mass Converter application.

Frontend responsibilities only: build the visual layout, capture user
input, validate it, and hand real conversions to ``converter`` while
persisting every success through ``database``.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import converter
import database

APP_TITLE = "WEIGHT / MASS CONVERTER"
APP_SUBTITLE = "Convert between different units of weight and mass"

UNITS = ["Kilogram", "Gram", "Tonne"]

COLORS = {
    "bg": "#f4f6f9",
    "card": "#ffffff",
    "primary": "#1f4e79",
    "primary_dark": "#163a5c",
    "accent": "#2e86c1",
    "border": "#d9dee4",
    "text": "#1d2733",
    "muted": "#5d6b7a",
    "error": "#c0392b",
}

HISTORY_COLUMNS = ("input", "from_unit", "to_unit", "result", "timestamp")
HISTORY_LABELS = {
    "input": "Input",
    "from_unit": "From",
    "to_unit": "To",
    "result": "Result",
    "timestamp": "Date/Time",
}


def format_number(value):
    """Return a clean, readable string representation of a number.

    Integers show without decimals; other values are shown with up to ten
    decimal places, with trailing zeros removed.
    """
    number = float(value)
    if number == int(number):
        return str(int(number))
    text = "{:.10f}".format(number).rstrip("0").rstrip(".")
    return text


class MainWindow:
    """The full GUI for the converter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Weight / Mass Converter")
        self.root.geometry("760x760")
        self.root.minsize(640, 620)
        self.root.configure(bg=COLORS["bg"])

        database.initialize_database()
        self._configure_styles()
        self._build_ui()
        self._refresh_history()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Card.TFrame",
            background=COLORS["card"],
            relief="flat",
        )
        style.configure(
            "TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "Section.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Result.TLabel",
            background=COLORS["card"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "Accent.TButton",
            background=COLORS["primary"],
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padding=(18, 9),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["primary_dark"])],
        )
        style.configure(
            "Default.TButton",
            background=COLORS["accent"],
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        style.map(
            "Default.TButton",
            background=[("active", "#2471a3")],
        )
        style.configure(
            "Danger.TButton",
            background=COLORS["error"],
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#943126")],
        )
        style.configure(
            "TCombobox",
            font=("Segoe UI", 11),
            padding=6,
            fieldbackground=COLORS["card"],
            background=COLORS["card"],
        )
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
            background=COLORS["card"],
            fieldbackground=COLORS["card"],
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=COLORS["primary"],
            foreground="#ffffff",
            padding=6,
        )
        style.configure("Vertical.TScrollbar", background="#c9d0d8")

    def _build_ui(self):
        root_frame = tk.Frame(self.root, bg=COLORS["bg"])
        root_frame.pack(fill="both", expand=True)
        root_frame.columnconfigure(0, weight=1)
        root_frame.rowconfigure(3, weight=1)

        header = tk.Frame(root_frame, bg=COLORS["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 6))
        ttk.Label(header, text=APP_TITLE, style="Header.TLabel").pack()
        ttk.Label(header, text=APP_SUBTITLE, style="Subtitle.TLabel").pack(pady=(2, 0))

        self._build_input_card(root_frame)
        self._build_result_card(root_frame)
        self._build_history_card(root_frame)

    def _build_input_card(self, parent):
        card = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        card.grid(row=1, column=0, sticky="ew", padx=24, pady=10)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Enter Value", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(card, textvariable=self.value_var, font=("Segoe UI", 14), justify="center")
        self.value_entry.grid(row=1, column=0, sticky="ew", padx=18)
        self.value_entry.bind("<Return>", lambda event: self.on_convert())

        unit_row = tk.Frame(card, bg=COLORS["card"])
        unit_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(14, 4))
        unit_row.columnconfigure(0, weight=1)
        unit_row.columnconfigure(1, weight=1)
        unit_row.columnconfigure(2, weight=1)

        ttk.Label(unit_row, text="From Unit", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(unit_row, text="To Unit", style="Field.TLabel").grid(row=0, column=2, sticky="w")

        self.from_var = tk.StringVar(value=UNITS[0])
        self.to_var = tk.StringVar(value=UNITS[1])
        self.from_combo = ttk.Combobox(unit_row, textvariable=self.from_var, values=UNITS, state="readonly", width=14, font=("Segoe UI", 11))
        self.to_combo = ttk.Combobox(unit_row, textvariable=self.to_var, values=UNITS, state="readonly", width=14, font=("Segoe UI", 11))
        self.from_combo.grid(row=1, column=0, sticky="w", pady=(2, 8))
        self.to_combo.grid(row=1, column=2, sticky="w", pady=(2, 8))

        self.swap_button = ttk.Button(unit_row, text="SWAP", style="Default.TButton", command=self.on_swap)
        self.swap_button.grid(row=1, column=1, sticky="ew", padx=10)

        actions = tk.Frame(card, bg=COLORS["card"])
        actions.grid(row=3, column=0, sticky="ew", padx=18, pady=(4, 18))
        actions.columnconfigure(1, weight=1)

        self.convert_button = ttk.Button(actions, text="CONVERT", style="Accent.TButton", command=self.on_convert)
        self.convert_button.grid(row=0, column=1, sticky="ew")

        self.clear_button = ttk.Button(actions, text="CLEAR", style="Default.TButton", command=self.on_clear)
        self.clear_button.grid(row=0, column=2, padx=(10, 0))

    def _build_result_card(self, parent):
        card = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=(4, 10))
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Converted Result", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=18, pady=(12, 4))
        self.result_var = tk.StringVar(value="-")
        ttk.Label(card, textvariable=self.result_var, style="Result.TLabel", anchor="center").grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))

    def _build_history_card(self, parent):
        card = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        card.grid(row=3, column=0, sticky="nsew", padx=24, pady=(4, 20))
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        header_row = tk.Frame(card, bg=COLORS["card"])
        header_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(12, 8))
        header_row.columnconfigure(0, weight=1)
        ttk.Label(header_row, text="Conversion History", style="Section.TLabel").grid(row=0, column=0, sticky="w")

        self.clear_history_button = ttk.Button(header_row, text="CLEAR HISTORY", style="Danger.TButton", command=self.on_clear_history)
        self.clear_history_button.grid(row=0, column=1, sticky="e")

        tree_frame = tk.Frame(card, bg=COLORS["card"])
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=HISTORY_COLUMNS, show="headings", selectmode="browse", height=8)
        for column in HISTORY_COLUMNS:
            self.tree.heading(column, text=HISTORY_LABELS[column])
        self.tree.column("input", width=90, anchor="center")
        self.tree.column("from_unit", width=110, anchor="center")
        self.tree.column("to_unit", width=110, anchor="center")
        self.tree.column("result", width=120, anchor="center")
        self.tree.column("timestamp", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def get_input_value(self):
        """Validate the input box.

        Returns the parsed positive float, or shows the friendly error
        message and returns None.
        """
        raw = self.value_var.get().strip()
        if not raw:
            messagebox.showwarning("Invalid Input", converter.ERROR_EMPTY)
            self._focus_input()
            return None
        try:
            value = float(raw)
        except ValueError:
            messagebox.showwarning("Invalid Input", converter.ERROR_INVALID)
            self._focus_input()
            return None
        if value <= 0:
            messagebox.showwarning("Invalid Input", converter.ERROR_NON_POSITIVE)
            self._focus_input()
            return None
        return value

    def _focus_input(self):
        self.value_entry.focus_set()
        self.value_entry.selection_range(0, "end")

    def on_convert(self):
        value = self.get_input_value()
        if value is None:
            return
        from_unit = self.from_var.get()
        to_unit = self.to_var.get()
        try:
            result = converter.convert_weight(value, from_unit, to_unit)
        except KeyError:
            messagebox.showerror("Conversion Error", "One of the selected units is not supported.")
            return

        self.result_var.set("{} {} = {} {}".format(format_number(value), from_unit, format_number(result), to_unit))
        database.save_conversion(value, from_unit, to_unit, result)
        self._refresh_history()
        self.value_entry.focus_set()

    def on_swap(self):
        from_unit = self.from_var.get()
        to_unit = self.to_var.get()
        self.from_var.set(to_unit)
        self.to_var.set(from_unit)

    def on_clear(self):
        self.value_var.set("")
        self.result_var.set("-")
        self.value_entry.focus_set()

    def on_clear_history(self):
        database.clear_history()
        self._refresh_history()

    def _refresh_history(self):
        """Reload history rows from the database into the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = database.get_history()
        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    format_number(record["input_value"]),
                    record["from_unit"],
                    record["to_unit"],
                    format_number(record["result"]),
                    record["timestamp"],
                ),
            )